import logging
import time
import aprslib
from server.trackdirect.TrackDirectConfig import TrackDirectConfig
from server.trackdirect.parser.AprsPacketParser import AprsPacketParser
from server.trackdirect.exceptions.TrackDirectParseError import TrackDirectParseError
from server.trackdirect.websocket.responses.ResponseDataConverter import ResponseDataConverter
from server.trackdirect.websocket.responses.HistoryResponseCreator import HistoryResponseCreator


class AprsISPayloadCreator:
    """The AprsISPayloadCreator creates a payload to send to client based on data received from the APRS-IS server."""

    def __init__(self, state, db):
        """Initialize the AprsISPayloadCreator.

        Args:
            state (ConnectionState): Instance of ConnectionState which contains the current state of the connection.
            db (psycopg2.Connection): Database connection (with autocommit).
        """
        self.logger = logging.getLogger('trackdirect')
        self.state = state
        self.db = db
        self.response_data_converter = ResponseDataConverter(state, db)
        self.history_response_creator = HistoryResponseCreator(state, db)
        self.config = TrackDirectConfig()
        self.station_hash_timestamps = {}
        self.save_ogn_stations_with_missing_identity = self.config.save_ogn_stations_with_missing_identity

    def get_payloads(self, line, source_id):
        """Takes a raw packet and returns a generator with the parsed result.

        Args:
            line (str): The raw packet as a string.
            source_id (int): The id of the source.

        Returns:
            generator
        """
        try:
            packet = self._parse(line, source_id)
            if not self._is_packet_valid(packet):
                return

            self._update_station_on_map(packet)

            if self._is_station_filtered(packet):
                yield from self._get_previous_packets_payload(packet)

            yield self._get_real_time_packet_payload(packet)
        except (aprslib.ParseError, aprslib.UnknownFormat, TrackDirectParseError, UnicodeDecodeError) as exp:
            self.logger.error(f"Error processing packet: {exp}")

    def _parse(self, line, source_id):
        """Parse packet raw.

        Args:
            line (str): The raw packet as a string.
            source_id (int): The id of the source.

        Returns:
            Packet
        """
        try:
            basic_packet_dict = aprslib.parse(line)
            parser = AprsPacketParser(self.db, self.save_ogn_stations_with_missing_identity)
            parser.set_database_write_access(False)
            parser.set_source_id(source_id)
            packet = parser.get_packet(basic_packet_dict)

            if packet and packet.map_id == 4:
                time.sleep(1)
                packet = parser.get_packet(basic_packet_dict)

            return packet if packet and packet.map_id != 15 else None
        except (aprslib.ParseError, aprslib.UnknownFormat, TrackDirectParseError):
            return None

    def _is_packet_valid(self, packet):
        """Check if the packet is valid to send to client.

        Args:
            packet (Packet): Found packet that we may want to send to client.

        Returns:
            bool: True if the packet is valid, False otherwise.
        """
        if not packet:
            return False

        if packet.map_id in {4, 15} or packet.station_id is None:
            return False

        if packet.marker_id in {None, 1} or packet.latitude is None or packet.longitude is None:
            return False

        if self.state.filter_station_id_dict and packet.station_id not in self.state.filter_station_id_dict:
            return False

        return True

    def _update_station_on_map(self, packet):
        """Update the station on the map if not already present."""
        if packet.station_id not in self.state.stations_on_map_dict:
            self.state.stations_on_map_dict[packet.station_id] = True

    def _is_station_filtered(self, packet):
        """Check if the station is filtered."""
        return bool(self.state.filter_station_id_dict) and packet.station_id in self.state.filter_station_id_dict

    def _get_real_time_packet_payload(self, packet):
        """Create a payload response for a real-time packet.

        Args:
            packet (Packet): The packet directly received from APRS-IS.

        Returns:
            dict
        """
        options = ["realtime"]
        data = self.response_data_converter.get_response_data([packet], None, options)
        return {'payload_response_type': 2, 'data': data}

    def _get_previous_packets_payload(self, packet):
        """Create payloads containing previous packets for the station that sent the specified packet.

        Args:
            packet (Packet): The packet directly received from APRS-IS.

        Returns:
            generator
        """
        latest_timestamp_on_map = self.state.get_station_latest_timestamp_on_map(packet.station_id) or 0
        latest_timestamp_on_map += 5

        if (self.state.is_station_history_on_map(packet.station_id) and
                packet.marker_prev_packet_timestamp and
                packet.timestamp > latest_timestamp_on_map and
                packet.marker_prev_packet_timestamp > latest_timestamp_on_map):
            # Ups! We got a problem, the previous packet for this station has not been sent to client
            # If no packets at all had been sent we would have marked the realtime-packet to be overwritten,
            # but now we have a missing packet from current station that may never be sent!
            # Send it now! This may result in that we send the same packet twice (but client should handle that)
            request = {"station_id": packet.station_id, "payload_request_type": 7}
            yield from self.history_response_creator.get_responses(request, None)
