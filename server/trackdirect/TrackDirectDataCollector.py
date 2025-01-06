import logging
import psycopg2
import psycopg2.extras
import re
import aprslib
import datetime
import time
from twisted.internet import reactor, threads

from server.trackdirect.TrackDirectConfig import TrackDirectConfig
from server.trackdirect.parser.AprsPacketParser import AprsPacketParser
from server.trackdirect.parser.AprsISConnection import AprsISConnection
from server.trackdirect.parser.policies.PacketDuplicatePolicy import PacketDuplicatePolicy
from server.trackdirect.collector.PacketBatchInserter import PacketBatchInserter
from server.trackdirect.exceptions.TrackDirectParseError import TrackDirectParseError
from server.trackdirect.database.DatabaseConnection import DatabaseConnection
from server.trackdirect.repositories.StationRepository import StationRepository

#from pympler.tracker import SummaryTracker

class TrackDirectDataCollector:
    """An TrackDirectDataCollector instance connects to the data source and saves all received packets to the database

    Note:
        The collector class is built to handle ONE connection to a data source server (may be a APRS-IS server), if two is wanted run two processes.
        This is useful if you want one connection to the regular APRS-IS network and one connection to the CWOP network.
    """

    def __init__(self, collector_options, save_ogn_stations_with_missing_identity):
        """The __init__ method.

        Args:
            collector_options (dict): Contains data like host, port, callsign, passcode, source id
            save_ogn_stations_with_missing_identity (bool): True if we should not ignore stations with a missing identity
        """
        self.station_repository = None
        self.db_no_auto_commit = None
        self.db = None

        self.logger = logging.getLogger(__name__)

        self.save_ogn_stations_with_missing_identity = save_ogn_stations_with_missing_identity
        self.source_hostname = collector_options['host']
        self.source_port = collector_options['port_full']
        self.numbers_in_batch = collector_options['numbers_in_batch']
        self.save_fast_packets = collector_options['save_fast_packets']
        self.frequency_limit = collector_options['frequency_limit']
        self.detect_duplicates = collector_options['detect_duplicates']
        self.hard_frequency_limit = None
        if not self.save_fast_packets and self.frequency_limit is not None and int(self.frequency_limit) > 0:
            # Only respect hard frequency limit if we are not saving "fast packets"
            self.hard_frequency_limit = self.frequency_limit
        self.source_id = collector_options['source_id']
        self.callsign = collector_options['callsign']
        self.passcode = collector_options['passcode']

        self.latest_packet_timestamp = None
        self.first_packet_timestamp = None
        self.latest_batch_insert_timestamp = int(time.time())

        self.packets = []
        self.station_ids_with_visible_packet = []
        self.moving_station_ids_with_visible_packet = []
        self.moving_marker_ids_with_visible_packet = []
        self.delay = 0

    def run(self, config_file):
        """Start the collector

        Args:
            config_file (string): TrackDirect config file path
        """
        config = TrackDirectConfig()
        config.populate(config_file)

        db_connection = DatabaseConnection()
        self.db = db_connection.get_connection(True)
        self.db_no_auto_commit = db_connection.get_connection(False)
        self.station_repository = StationRepository(self.db)

        threads.deferToThread(self.consume)
        reactor.run()

    def consume(self):
        """Start consuming packets"""
        connection = AprsISConnection(
            self.callsign, self.passcode, self.source_hostname, self.source_port)
        connection.set_frequency_limit(self.hard_frequency_limit)
        connection.set_source_id(self.source_id)

        def on_packet_read(line):
            if not reactor.running:
                raise StopIteration('Stopped')

            timestamp = int(time.time())
            deferred = threads.deferToThread(self._parse, line, timestamp)
            deferred.addCallback(on_parse_complete)
            deferred.addErrback(on_parse_error)

        def on_parse_complete(packet):
            reactor.callFromThread(self._add_packet, packet)

        def on_parse_error(error):
            # Parse will more or less only cast exception if db connection is lost
            if reactor.running:
                reactor.stop()
            raise error

        try:
            connection.connect()
            connection.filtered_consumer(on_packet_read, True, True)
        except aprslib.ConnectionDrop as exp:
            self.logger.warning('Lost connection: %s', exp)
            self.consume()
        except Exception as e:
            self.logger.exception('Error in consume method: %s', e)
            if reactor.running:
                reactor.stop()

    def _parse(self, line, timestamp):
        """Parse raw packet

        Args:
            line (str): APRS raw packet string
            timestamp (int): Receive time of packet

        Returns:
            Packet
        """
        try:
            self.delay = int(time.time()) - timestamp
            if self.delay > 60:
                self.logger.error(
                    'Collector has a delay of %s seconds, ignoring packets until solved', self.delay)
                return None
            elif self.delay > 15:
                self.logger.warning(
                    'Collector has a delay of %s seconds', self.delay)

            packet_dict = aprslib.parse(line)
            parser = AprsPacketParser(self.db, self.save_ogn_stations_with_missing_identity)
            parser.set_source_id(self.source_id)
            packet = parser.get_packet(packet_dict, timestamp)

            if packet.map_id in [15, 16]:
                return None

            if self.detect_duplicates:
                self._check_if_duplicate(packet)

            return self._clean_packet(packet)

        except (aprslib.ParseError, aprslib.UnknownFormat, TrackDirectParseError) as exp:
            return self._parse_unsupported_packet(line, timestamp)
        except psycopg2.InterfaceError as e:
            raise e
        except UnicodeDecodeError:
            pass
        except Exception as e:
            self.logger.exception('Error in _parse method: %s', e)
        return None

    def _parse_unsupported_packet(self, line, timestamp):
        """Try to parse raw packet that aprs-lib could not handle

        Args:
            line (str): APRS raw packet string
            timestamp (int): Receive time of packet

        Returns:
            Packet
        """
        try:
            line = line.decode('utf-8', 'ignore')
            packet_dict = self.basic_parse(line)
            parser = AprsPacketParser(self.db, self.save_ogn_stations_with_missing_identity)
            parser.set_source_id(self.source_id)
            packet = parser.get_packet(packet_dict, timestamp, True)
            packet.marker_id = 1

            if packet.packet_type_id == 6:  # Telemetry packet
                packet.packet_type_id = 10  # Has no position
            else:
                packet.map_id = 11  # Unsupported packet

            return packet
        except Exception as e:
            self.logger.debug('Error in _parse_unsupported_packet: %s', e)
            self.logger.debug('Line: %s', line)
        return None

    def _add_packet(self, packet):
        """Adds packet to database

        Args:
            packet (Packet): The packet
        """
        if packet is None:
            return

        if self._is_station_sending_too_fast(packet):
            if not self.save_fast_packets:
                return

            packet.marker_id = 1
            packet.map_id = 8

            # Reset all mapId related values
            packet.replace_packet_id = None
            packet.abnormal_packet_id = None
            packet.confirm_packet_id = None
            packet.replace_packet_timestamp = None
            packet.abnormal_packet_timestamp = None
            packet.confirm_packet_timestamp = None

        if packet.map_id == 6:
            if not self.save_fast_packets:
                return

        if not self._is_packet_valid_in_current_batch(packet):
            self._insert_batch()

        if self._should_packet_be_added(packet):
            self._add_packet_to_batch(packet)

        if self._is_batch_full() or self._is_batch_old():
            self._insert_batch()

    def _is_station_sending_too_fast(self, packet):
        """Returns true if this packet has been sent too close to the previous packet from the same station

        Args:
            packet (Packet): The packet that may have been sent too fast

        Returns:
            bool
        """
        if packet.map_id in [1, 5, 7, 9] and packet.is_moving == 1 and self.frequency_limit is not None:
            frequency_limit_to_apply = int(self.frequency_limit)

            if frequency_limit_to_apply == 0:
                return False

            if packet.ogn is not None and packet.ogn.ogn_turn_rate is not None:
                turn_rate = abs(float(packet.ogn.ogn_turn_rate))
                if turn_rate > 0:
                    frequency_limit_to_apply = int(frequency_limit_to_apply / (1 + turn_rate))

            if packet.marker_prev_packet_timestamp:
                if (packet.timestamp - frequency_limit_to_apply) < packet.marker_prev_packet_timestamp:
                    return True

            if packet.station_id in self.moving_station_ids_with_visible_packet:
                return True

            if packet.marker_id in self.moving_marker_ids_with_visible_packet:
                return True
        return False

    def _is_packet_valid_in_current_batch(self, packet):
        """Returns true if this packet can be added to current batch

        Args:
            packet (Packet): The packet that we want to add to current batch

        Returns:
            bool
        """
        if self.latest_packet_timestamp is not None:
            current_packet_date = datetime.datetime.utcfromtimestamp(
                int(packet.timestamp)).strftime('%Y%m%d')
            latest_packet_date = datetime.datetime.utcfromtimestamp(
                self.latest_packet_timestamp).strftime('%Y%m%d')

            if current_packet_date != latest_packet_date and len(self.packets) > 0:
                return False

        if packet.station_id in self.station_ids_with_visible_packet:
            return False

        return True

    def _should_packet_be_added(self, packet):
        """Returns true if this packet should be added to database

        Args:
            packet (Packet): The packet that we want to add to batch

        Returns:
            bool
        """
        return packet.source_id != 3 or packet.station_id_path

    def _is_batch_full(self):
        """Returns true if batch is considered full

        Returns:
            bool
        """
        return len(self.packets) > int(self.numbers_in_batch) or (
            len(self.packets) > 0 and self.latest_batch_insert_timestamp < int(time.time()) - 5)

    def _is_batch_old(self):
        """Returns true if batch is considered old

        Returns:
            bool
        """
        return (self.latest_packet_timestamp is not None
                and self.first_packet_timestamp is not None
                and self.latest_packet_timestamp - self.first_packet_timestamp > 1)

    def _add_packet_to_batch(self, packet):
        """Add instance of ParsedPacket to batch

        Args:
            packet (Packet): Packet that we want to add to batch
        """
        self.latest_packet_timestamp = int(packet.timestamp)
        if self.first_packet_timestamp is None:
            self.first_packet_timestamp = int(packet.timestamp)
        self.packets.append(packet)
        if packet.map_id in [1, 5, 7, 9]:
            self.station_ids_with_visible_packet.append(packet.station_id)
            if packet.is_moving == 1:
                self.moving_station_ids_with_visible_packet.append(packet.station_id)
                self.moving_marker_ids_with_visible_packet.append(packet.marker_id)

    def _insert_batch(self):
        """Perform insert on the current batch"""
        if len(self.packets) > 0:
            self.latest_batch_insert_timestamp = int(time.time())

            # Make sure packets are inserted in the order that they were received
            self.packets.reverse()

            # Do batch insert
            packet_batch_inserter = PacketBatchInserter(
                self.db, self.db_no_auto_commit)
            packet_batch_inserter.insert(self.packets[:])

            self._reset()

    def _reset(self):
        """Reset all collector variables"""
        self.packets = []
        self.station_ids_with_visible_packet = []
        self.moving_station_ids_with_visible_packet = []
        self.moving_marker_ids_with_visible_packet = []
        self.latest_packet_timestamp = None
        self.first_packet_timestamp = None

    def _clean_packet(self, packet):
        """Method used to clean a Packet from unused columns

        Args:
            packet (Packet): Object of class Packet

        Returns:
            Packet
        """
        if packet.map_id not in [1, 5, 7, 9]:
            # This packet will never be shown on map, remove information that won't be used
            packet.marker_id = None
            packet.marker_counter = None
            packet.packet_tail_timestamp = None
            packet.position_timestamp = None
            packet.posambiguity = None
            packet.symbol = None
            packet.symbol_table = None
            packet.map_sector = None
            packet.related_map_sectors = None
            packet.speed = None
            packet.course = None
            packet.altitude = None
            packet.is_moving = 1
        return packet

    def _check_if_duplicate(self, packet):
        """Method used to check if this packet is a duplicate

        Note:
            If packet is a duplicate the object attribute mapId will be updated, and some related attributes.

        Args:
            packet (Packet): Object of class Packet
        """
        packet_duplicate_policy = PacketDuplicatePolicy(self.station_repository)
        if packet_duplicate_policy.is_duplicate(packet):
            # It is a duplicate (or at least we treat it as one just to be safe)
            packet.map_id = 3
            packet.marker_id = 1
            packet.replace_packet_id = None
            packet.replace_packet_timestamp = None
            packet.abnormal_packet_id = None
            packet.abnormal_packet_timestamp = None
            packet.confirm_packet_id = None
            packet.confirm_packet_timestamp = None

    def basic_parse(self, line):
        """Perform a basic packet parse and return result as a dict

        Args:
            line (str): Packet raw string

        Returns:
            dict: Packet dict
        """
        # Divide into body and head
        try:
            head, body = line.split(':', 1)
        except ValueError:
            raise TrackDirectParseError("no body", {})

        if len(body) == 0:
            raise TrackDirectParseError("body is empty", {})

        packet_type = body[0]
        body = body[1:]

        # Find sender, destination and path in header
        try:
            fromcall, path = head.split('>', 1)
        except ValueError:
            raise TrackDirectParseError("no header", {})

        if not 1 <= len(fromcall) <= 9:
            raise TrackDirectParseError("fromcallsign has invalid length", {})

        path = path.split(',')
        tocall = path[0] if path else None
        path = path[1:]

        for station in path:
            if not re.match(r"^[A-Z0-9\-]{1,9}\*?$", station, re.I):
                path = None
                break

        object_name = ''
        if packet_type == ';':
            match = re.match(r"^([ -~]{9})(\*|_)", body)
            if match:
                name, flag = match.groups()
                object_name = name
                body = body[10:]

        if packet_type == ')':
            match = re.match(r"^([ -~!]{3,9})(\!|_)", body)
            if match:
                name, flag = match.groups()
                object_name = name
                body = body[len(name)+1:]

        comment = None
        telemetry = None
        if packet_type == 'T':
            telemetry = {}
            lst = body.split(',')
            if len(lst) >= 7:
                seq = lst[0]
                vals = lst[1:6]
                bits = lst[6][:8]
                comment = lst[6][8:]

                if seq.startswith('T'):
                    seq = seq[1:]
                if seq.startswith('#'):
                    seq = seq[1:]

                for i in range(5):
                    try:
                        vals[i] = float(vals[i]) if vals[i] != '' else None
                    except ValueError:
                        vals[i] = None

                telemetry = {
                    'seq': seq,
                    'vals': vals,
                    'bits': bits
                }

        # Create result
        packet = {
            'from': fromcall,
            'to': tocall,
            'path': path,
            'raw': line,
            'object_name': object_name,
            'packet_type': packet_type,
            'telemetry': telemetry,
            'comment': comment
        }
        return packet