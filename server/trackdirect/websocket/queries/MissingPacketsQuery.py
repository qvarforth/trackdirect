from server.trackdirect.repositories.PacketRepository import PacketRepository
from server.trackdirect.repositories.StationRepository import StationRepository
from server.trackdirect.parser.policies.MapSectorPolicy import MapSectorPolicy

class MissingPacketsQuery:
    """This class is used to find packets for all stations that are missing packets when they are needed.

    Note:
        If no packets are found, they will be simulated.
    """

    def __init__(self, state, db):
        """
        Initialize the MissingPacketsQuery.

        Args:
            state (WebsocketConnectionState): The current state for a websocket connection.
            db (psycopg2.Connection): Database connection.
        """
        self.state = state
        self.db = db
        self.packet_repository = PacketRepository(db)
        self.station_repository = StationRepository(db)
        self.simulate_empty_station = False

    def enable_simulate_empty_station(self):
        """Enable simulation even if no packets are available from the station."""
        self.simulate_empty_station = True

    def get_missing_packets(self, station_ids, found_packets):
        """
        Fetch the latest packets for stations that have no packets in found_packets.

        Args:
            station_ids (list): A list of station IDs to filter on.
            found_packets (list): Packets that have been found.

        Returns:
            list: A sorted list of missing packets.
        """
        found_missing_packets = []
        for station_id in station_ids:
            if not any(packet.station_id == station_id for packet in found_packets):
                missing_packet = self._get_latest_packet(station_id)
                if missing_packet is not None:
                    found_missing_packets.append(missing_packet)

        return sorted(found_missing_packets, key=lambda item: item.timestamp)

    def _get_latest_packet(self, station_id):
        """
        Try to find a packet for the specified station; simulate a packet based on old data if necessary.

        Args:
            station_id (int): Station ID that needs a packet.

        Returns:
            Packet: The latest packet or a simulated packet.
        """
        if self.state.latest_time_travel_request is not None:
            ts = int(self.state.latest_time_travel_request) - (30 * 24 * 60 * 60)  # Limit for time travelers
            older_packets = self.packet_repository.get_latest_object_list_by_station_id_list_and_time_interval(
                [station_id], ts, self.state.latest_time_travel_request
            )
        else:
            older_packets = self.packet_repository.get_latest_confirmed_object_list_by_station_id_list([station_id], 0)

        if older_packets:
            return older_packets[0]  # The latest is the first in the list

        # Try non-confirmed packets
        if self.state.latest_time_travel_request is not None:
            ts = int(self.state.latest_time_travel_request) - (30 * 24 * 60 * 60)
            older_non_confirmed_packets = self.packet_repository.get_latest_object_list_by_station_id_list_and_time_interval(
                [station_id], ts, self.state.latest_time_travel_request, False
            )
        else:
            older_non_confirmed_packets = self.packet_repository.get_latest_object_list_by_station_id_list([station_id], 0)

        if older_non_confirmed_packets:
            packet = older_non_confirmed_packets[0]
            packet.map_id = 1
            packet.source_id = 0  # Simulated
            return packet

        # Simulate a packet if none are found
        return self._get_simulated_packet(station_id)

    def _get_simulated_packet(self, station_id):
        """
        Create a simulated packet based on data saved in the station table.

        Args:
            station_id (int): The station ID for which a packet is needed.

        Returns:
            Packet: A simulated packet or None if not possible.
        """
        station = self.station_repository.get_object_by_id(station_id)
        if station.is_existing_object() and (station.latest_confirmed_packet_id is not None or self.simulate_empty_station):
            packet = self.packet_repository.create()
            packet.station_id = station.id
            packet.sender_id = station.latest_sender_id
            packet.source_id = station.source_id
            packet.ogn_sender_address = station.latest_ogn_sender_address

            packet.id = station.latest_confirmed_packet_id if station.latest_confirmed_packet_id is not None else -station.id
            packet.marker_id = station.latest_confirmed_marker_id if station.latest_confirmed_marker_id is not None else -station.id

            packet.is_moving = 0
            packet.packet_type_id = 1  # Assume it was a position packet

            packet.latitude = station.latest_confirmed_latitude if station.latest_confirmed_latitude is not None else 0.0
            packet.longitude = station.latest_confirmed_longitude if station.latest_confirmed_longitude is not None else 0.0

            packet.timestamp = (
                0 if self.state.latest_time_travel_request is not None else station.latest_confirmed_packet_timestamp or 0
            )

            packet.reported_timestamp = None
            packet.position_timestamp = packet.timestamp
            packet.posambiguity = 0

            packet.symbol = station.latest_confirmed_symbol
            packet.symbol_table = station.latest_confirmed_symbol_table

            map_sector_policy = MapSectorPolicy()
            packet.map_sector = map_sector_policy.get_map_sector(packet.latitude, packet.longitude)
            packet.related_map_sectors = []
            packet.map_id = 1
            packet.speed = None
            packet.course = None
            packet.altitude = None
            packet.packet_tail_timestamp = packet.timestamp
            packet.comment = None
            packet.raw_path = None
            packet.raw = None

            return packet
        return None
