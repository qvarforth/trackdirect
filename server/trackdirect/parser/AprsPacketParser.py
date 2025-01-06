import logging
import datetime
import time
import calendar
import hashlib
from server.trackdirect.exceptions.TrackDirectParseError import TrackDirectParseError
from server.trackdirect.exceptions.TrackDirectMissingSenderError import TrackDirectMissingSenderError
from server.trackdirect.exceptions.TrackDirectMissingStationError import TrackDirectMissingStationError
from server.trackdirect.repositories.OgnHiddenStationRepository import OgnHiddenStationRepository
from server.trackdirect.repositories.OgnDeviceRepository import OgnDeviceRepository
from server.trackdirect.repositories.StationRepository import StationRepository
from server.trackdirect.repositories.SenderRepository import SenderRepository
from server.trackdirect.repositories.PacketRepository import PacketRepository
from server.trackdirect.repositories.PacketTelemetryRepository import PacketTelemetryRepository
from server.trackdirect.repositories.PacketWeatherRepository import PacketWeatherRepository
from server.trackdirect.repositories.PacketOgnRepository import PacketOgnRepository
from server.trackdirect.repositories.MarkerRepository import MarkerRepository
from server.trackdirect.repositories.StationTelemetryBitsRepository import StationTelemetryBitsRepository
from server.trackdirect.repositories.StationTelemetryEqnsRepository import StationTelemetryEqnsRepository
from server.trackdirect.repositories.StationTelemetryParamRepository import StationTelemetryParamRepository
from server.trackdirect.repositories.StationTelemetryUnitRepository import StationTelemetryUnitRepository
from server.trackdirect.objects.Packet import Packet
from server.trackdirect.parser.policies.AprsPacketTypePolicy import AprsPacketTypePolicy
from server.trackdirect.parser.policies.PacketAssumedMoveTypePolicy import PacketAssumedMoveTypePolicy
from server.trackdirect.parser.policies.PreviousPacketPolicy import PreviousPacketPolicy
from server.trackdirect.parser.policies.PacketTailPolicy import PacketTailPolicy
from server.trackdirect.parser.policies.PacketRelatedMapSectorsPolicy import PacketRelatedMapSectorsPolicy
from server.trackdirect.parser.policies.PacketMapIdPolicy import PacketMapIdPolicy
from server.trackdirect.parser.policies.PacketPathPolicy import PacketPathPolicy
from server.trackdirect.parser.policies.MapSectorPolicy import MapSectorPolicy
from server.trackdirect.parser.policies.PacketCommentPolicy import PacketCommentPolicy
from server.trackdirect.parser.policies.PacketKillCharPolicy import PacketKillCharPolicy
from server.trackdirect.parser.policies.StationNameFormatPolicy import StationNameFormatPolicy
from server.trackdirect.parser.policies.PacketOgnDataPolicy import PacketOgnDataPolicy


class AprsPacketParser:
    """AprsPacketParser takes an aprslib output and converts it to a Track direct Packet."""

    def __init__(self, db, save_ogn_stations_with_missing_identity):
        """Initialize the AprsPacketParser class.

        Args:
            db (psycopg2.Connection): Database connection
            save_ogn_stations_with_missing_identity (bool): True if we should not ignore stations with a missing identity
        """
        self.is_hidden_station = None
        self.data = None
        self.packet = None
        self.db = db
        self.save_ogn_stations_with_missing_identity = save_ogn_stations_with_missing_identity
        self.logger = logging.getLogger('trackdirect')

        self.database_write_access = True
        self.source_id = 1

        self.ogn_device_repository = OgnDeviceRepository(db)
        self.ogn_hidden_station_repository = OgnHiddenStationRepository(db)
        self.station_repository = StationRepository(db)
        self.sender_repository = SenderRepository(db)
        self.packet_repository = PacketRepository(db)
        self.packet_telemetry_repository = PacketTelemetryRepository(db)
        self.packet_weather_repository = PacketWeatherRepository(db)
        self.packet_ogn_repository = PacketOgnRepository(db)
        self.markerRepository = MarkerRepository(db)
        self.station_telemetry_bits_repository = StationTelemetryBitsRepository(db)
        self.station_telemetry_eqns_repository = StationTelemetryEqnsRepository(db)
        self.station_telemetry_param_repository = StationTelemetryParamRepository(db)
        self.station_telemetry_unit_repository = StationTelemetryUnitRepository(db)

    def set_database_write_access(self, database_write_access):
        """Enable or disable database updates.

        Args:
            database_write_access (bool): True if we have database access otherwise false
        """
        self.database_write_access = database_write_access

    def set_source_id(self, source_id):
        """Set what source packet is from (APRS, CWOP ...).

        Args:
            source_id (int): Id that corresponds to id in source-table
        """
        self.source_id = source_id

    def get_packet(self, data, timestamp=None, minimal=False):
        """Returns the resulting packet.

        Args:
            data (dict): Raw packet data
            timestamp (int): Packet timestamp
            minimal (bool): Set to true to only perform minimal parsing

        Returns:
            Packet
        """
        self.is_hidden_station = False
        self.data = data
        self.packet = Packet(self.db)
        self.packet.source_id = self.source_id
        self._parse_packet_initial_values(timestamp)
        self._parse_packet_reported_timestamp()

        # Parse OGN stuff before station-id, may result in no station to create
        self._parse_packet_ogn()
        if self.packet.map_id != 15:
            self._parse_packet_type()
            self._parse_packet_sender()
            self._parse_packet_station_name()
            self._parse_packet_station_id()

            self._parse_packet_rng()
            self._parse_packet_phg()

            if self.packet.station_id is None:
                self.packet.map_id = 4
            else:
                self._parse_packet_comment()
                self._parse_packet_weather()
                self._parse_packet_telemetry_definition()
                self._parse_packet_telemetry()
                self._parse_packet_position()
                self._parse_packet_path()

                if not minimal:
                    previous_packet_policy = PreviousPacketPolicy(self.packet, self.db)
                    previous_packet = previous_packet_policy.get_previous_packet()
                    self._parse_assumed_move_type_id(previous_packet)
                    self._parse_packet_tail(previous_packet)
                    self._parse_packet_map_id(previous_packet)
                    self._parse_packet_previous_timestamps(previous_packet)
                    self._parse_packet_phg_rng_timestamps(previous_packet)
                    self._parse_packet_related_map_sectors(previous_packet)

        if self.is_hidden_station:
            if self.packet.ogn is not None:
                self.packet.ogn.ogn_address_type_id = None
                self.packet.ogn.ogn_sender_address = None
            self.packet.comment = None
            self.packet.raw = None
        return self.packet

    def _parse_packet_initial_values(self, timestamp):
        """Set packet initial values.

        Args:
            timestamp (int): Packet timestamp
        """
        self.packet.raw = self.data['raw'].replace('\x00', '')
        self.packet.symbol = self.data.get('symbol')
        self.packet.symbol_table = self.data.get('symbol_table')
        self.packet.reported_timestamp = self.data.get('timestamp')
        self.packet.raw_path = f"{self.data['to']},{','.join(self.data['path'])}" if 'path' in self.data and 'to' in self.data else None
        self.packet.timestamp = timestamp if timestamp is not None else int(time.time())
        self.packet.position_timestamp = self.packet.timestamp
        self.packet.packet_tail_timestamp = 0
        self.packet.posambiguity = self.data.get('posambiguity')
        self.packet.speed = self.data.get('speed')
        self.packet.course = self.data.get('course')
        self.packet.altitude = self.data.get('altitude')
        self.packet.map_id = 10  # Default map for a packet without a position
        self.packet.marker_id = 1
        self.packet.marker_counter = 1  # We always start at 1

    def _parse_packet_reported_timestamp(self):
        """Set packet reported timestamp."""
        if 'timestamp' in self.data:
            reported_timestamp_day = int(datetime.datetime.utcfromtimestamp(int(self.data['timestamp'])).strftime('%d'))
            current_timestamp_day = int(datetime.datetime.utcfromtimestamp(self.packet.timestamp).strftime('%d'))
            if reported_timestamp_day > current_timestamp_day and self.data['timestamp'] > self.packet.timestamp:
                # Day is in the future, the reported timestamp was probably in previous month
                prev_month = int(datetime.datetime.utcfromtimestamp(int(self.data['timestamp']) - (reported_timestamp_day + 1) * 24 * 60 * 60).strftime('%m'))
                prev_month_year = int(datetime.datetime.utcfromtimestamp(int(self.data['timestamp']) - (reported_timestamp_day + 1) * 24 * 60 * 60).strftime('%Y'))
                number_of_days_in_month = int(calendar.monthrange(prev_month_year, prev_month)[1])
                self.packet.reported_timestamp = int(self.data['timestamp']) - (number_of_days_in_month * 24 * 60 * 60)
        else:
            self.packet.reported_timestamp = None

    def _parse_packet_rng(self):
        """Set packet RNG data."""
        if 'rng' in self.data:
            try:
                self.packet.rng = float(self.data['rng'])
                self.packet.latest_rng_timestamp = self.packet.timestamp
                if self.packet.rng <= 0:
                    self.packet.rng = None
            except ValueError:
                # Not a float
                self.packet.rng = None

    def _parse_packet_phg(self):
        """Set packet PHG data."""
        if 'phg' in self.data:
            phg = str(self.data['phg'])[0:4]
            if len(phg) == 4 and phg.isdigit():
                self.packet.phg = phg
                self.packet.latest_phg_timestamp = self.packet.timestamp

    def _parse_packet_sender(self):
        """Set sender id and name."""
        station_name_format_policy = StationNameFormatPolicy()
        self.packet.senderName = station_name_format_policy.get_correct_format(self.data["from"])
        try:
            sender = self.sender_repository.get_cached_object_by_name(self.packet.senderName)
            self.packet.sender_id = sender.id
        except TrackDirectMissingSenderError:
            if self.database_write_access:
                sender = self.sender_repository.get_object_by_name(self.packet.senderName, True, self.packet.source_id)
                self.packet.sender_id = sender.id

    def _parse_packet_station_name(self):
        """Set station name."""
        if "object_name" in self.data and self.data["object_name"]:
            self.packet.station_type_id = 2
            station_name_format_policy = StationNameFormatPolicy()
            self.packet.stationName = station_name_format_policy.get_correct_format(self.data["object_name"])
            if not self.packet.stationName:
                self.packet.stationName = self.packet.senderName
            if self.packet.stationName == self.packet.senderName:
                self.packet.station_type_id = 1
        else:
            self.packet.station_type_id = 1
            self.packet.stationName = self.packet.senderName

    def _parse_packet_station_id(self):
        """Set station id."""
        if self.packet.stationName is None:
            return
        try:
            station = self.station_repository.get_cached_object_by_name(self.packet.stationName, self.packet.source_id)
            self.packet.station_id = station.id

            if self.packet.stationName != station.name:
                # Station lower/upper case is modified
                station.name = self.packet.stationName
                station.save()

            if station.station_type_id != self.packet.station_type_id and int(self.packet.station_type_id) == 1:
                # Switch to station type 1
                station.station_type_id = self.packet.station_type_id
                station.save()

        except TrackDirectMissingStationError:
            if self.database_write_access:
                station = self.station_repository.get_object_by_name(self.packet.stationName, self.packet.source_id, self.packet.station_type_id, True)
                self.packet.station_id = station.id

    def _parse_packet_comment(self):
        """Set packet comment."""
        comment_policy = PacketCommentPolicy()
        self.packet.comment = comment_policy.get_comment(self.data, self.packet.packet_type_id)

    def _parse_packet_ogn(self):
        """Set the OGN sender address."""
        ogn_data_policy = PacketOgnDataPolicy(self.data, self.ogn_device_repository, self.packet.source_id)
        if ogn_data_policy.is_ogn_position_packet:
            original_raw = self.packet.raw

            if not ogn_data_policy.is_allowed_to_track:
                self.packet.map_id = 15
                return

            elif not ogn_data_policy.is_allowed_to_identify:
                if not self.save_ogn_stations_with_missing_identity:
                    self.packet.map_id = 15
                    return
                self.is_hidden_station = True
                self.data["from"] = self._get_hidden_station_name()
                self.data["object_name"] = None

            self.data['ogn'] = ogn_data_policy.get_ogn_data()
            if self.data['ogn'] is not None:
                self.packet.ogn = self.packet_ogn_repository.get_object_from_packet_data(self.data)
                self.packet.ogn.station_id = self.packet.station_id
                self.packet.ogn.timestamp = self.packet.timestamp
                self.data["comment"] = None
            self._modify_ogn_symbol(original_raw)

    def _modify_ogn_symbol(self, original_raw):
        """Sets a better symbol for an OGN station.

        Args:
            original_raw (str): Non modified raw
        """
        if (self.packet.symbol == '\'' and self.packet.symbol_table == '/') or (self.packet.symbol == '^' and self.packet.symbol_table in ['/', '\\']) or (self.packet.symbol == 'g' and self.packet.symbol_table in ['/']):
            ogn_device = None
            if self.packet.ogn is not None and self.packet.ogn.ogn_sender_address is not None:
                ogn_device = self.ogn_device_repository.get_object_by_device_id(self.packet.ogn.ogn_sender_address)

            if ogn_device is not None and ogn_device.is_existing_object() and 0 < ogn_device.ddb_aircraft_type < 6:
                # If another aircraft type exist in device db, use that instead
                if ogn_device.ddb_aircraft_type == 1:  # Gliders/motoGliders
                    # Glider -> Glider
                    self.packet.symbol = '^'
                    self.packet.symbol_table = 'G'

                elif ogn_device.ddb_aircraft_type == 2:  # Planes
                    # Powered aircraft -> Propeller aircraft
                    self.packet.symbol = '^'
                    self.packet.symbol_table = 'P'

                elif ogn_device.ddb_aircraft_type == 3:  # Ultralights
                    # Small plane
                    self.packet.symbol = '\''
                    self.packet.symbol_table = '/'

                elif ogn_device.ddb_aircraft_type == 4:  # Helicopters
                    # Helicopter
                    self.packet.symbol = 'X'
                    self.packet.symbol_table = '/'

                elif ogn_device.ddb_aircraft_type == 5:  # Drones/UAV
                    # UAV -> Drone
                    self.packet.symbol = '^'
                    self.packet.symbol_table = 'D'

            elif self.packet.ogn is not None and self.packet.ogn.ogn_aircraft_type_id is not None:
                if self.packet.ogn.ogn_aircraft_type_id == 1:
                    # Glider -> Glider
                    self.packet.symbol = '^'
                    self.packet.symbol_table = 'G'
                elif self.packet.ogn.ogn_aircraft_type_id == 9:
                    # Jet aircraft -> Jet
                    self.packet.symbol = '^'
                    self.packet.symbol_table = 'J'
                elif self.packet.ogn.ogn_aircraft_type_id == 8:
                    # Powered aircraft -> Propeller aircraft
                    self.packet.symbol = '^'
                    self.packet.symbol_table = 'P'
                elif self.packet.ogn.ogn_aircraft_type_id == 13:
                    # UAV -> Drone
                    self.packet.symbol = '^'
                    self.packet.symbol_table = 'D'
                elif self.packet.ogn.ogn_aircraft_type_id == 7:  # Paraglider
                    # Map to own symbol 94-76.svg (do not show hangglider symbol 103-1.svg, 'g' = 103)
                    self.packet.symbol = '^'  # 94
                    self.packet.symbol_table = 'L'  # 76

        if (self.packet.symbol == '\'' and self.packet.symbol_table == '/') or (self.packet.symbol == '^' and self.packet.symbol_table in ['/', '\\']):
            # Current symbol is still "small aircraft" or "large aircraft"
            if original_raw.startswith('FMT'):
                # FMT, Remotely Piloted
                self.packet.symbol = '^'
                self.packet.symbol_table = 'R'

    def _get_hidden_station_name(self):
        """Returns a unidentifiable station name.

        Returns:
            str
        """
        date = datetime.datetime.utcfromtimestamp(self.packet.timestamp).strftime('%Y%m%d')
        daily_station_name_hash = hashlib.sha256((self.data["from"] + date).encode()).hexdigest()

        ogn_hidden_station = self.ogn_hidden_station_repository.get_object_by_hashed_name(daily_station_name_hash, True)
        return ogn_hidden_station.get_station_name()

    def _parse_packet_weather(self):
        """Parse weather data."""
        if "weather" in self.data:
            self.packet.weather = self.packet_weather_repository.get_object_from_packet_data(self.data)
            self.packet.weather.station_id = self.packet.station_id
            self.packet.weather.timestamp = self.packet.timestamp

    def _parse_packet_telemetry(self):
        """Parse telemetry data."""
        if "telemetry" in self.data:
            self.packet.telemetry = self.packet_telemetry_repository.get_object_from_packet_data(self.data)
            self.packet.telemetry.station_id = self.packet.station_id
            self.packet.telemetry.timestamp = self.packet.timestamp

    def _parse_packet_telemetry_definition(self):
        """Parse telemetry definition."""
        if "tBITS" in self.data:
            self.packet.station_telemetry_bits = self.station_telemetry_bits_repository.get_object_from_packet_data(self.data)
            self.packet.station_telemetry_bits.station_id = self.packet.station_id
            self.packet.station_telemetry_bits.timestamp = self.packet.timestamp

        if "tEQNS" in self.data:
            self.packet.station_telemetry_eqns = self.station_telemetry_eqns_repository.get_object_from_packet_data(self.data)
            self.packet.station_telemetry_eqns.station_id = self.packet.station_id
            self.packet.station_telemetry_eqns.timestamp = self.packet.timestamp

        if "tPARM" in self.data:
            self.packet.station_telemetry_param = self.station_telemetry_param_repository.get_object_from_packet_data(self.data)
            self.packet.station_telemetry_param.station_id = self.packet.station_id
            self.packet.station_telemetry_param.timestamp = self.packet.timestamp

        if "tUNIT" in self.data:
            self.packet.station_telemetry_unit = self.station_telemetry_unit_repository.get_object_from_packet_data(self.data)
            self.packet.station_telemetry_unit.station_id = self.packet.station_id
            self.packet.station_telemetry_unit.timestamp = self.packet.timestamp

    def _parse_packet_type(self):
        """Set packet type."""
        aprs_packet_type_policy = AprsPacketTypePolicy()
        self.packet.packet_type_id = aprs_packet_type_policy.get_packet_type(self.packet)

    def _parse_packet_position(self):
        """Parse the packet position and related attributes."""
        if "latitude" in self.data and "longitude" in self.data and self.data["latitude"] is not None and self.data["longitude"] is not None:
            self.packet.latitude = self.data['latitude']
            self.packet.longitude = self.data['longitude']

            map_sector_policy = MapSectorPolicy()
            self.packet.map_sector = map_sector_policy.get_map_sector(self.data["latitude"], self.data["longitude"])
            self.packet.map_id = 1  # Default map for a packet with a position
            self.packet.is_moving = 1  # Moving/Stationary, default value is moving

    def _parse_packet_path(self):
        """Parse packet path."""
        if "path" in self.data and isinstance(self.data["path"], list):
            packet_path_policy = PacketPathPolicy(self.data['path'], self.packet.source_id, self.station_repository, self.sender_repository)
            self.packet.station_id_path = packet_path_policy.get_station_id_path()
            self.packet.station_name_path = packet_path_policy.get_station_name_path()
            self.packet.station_location_path = packet_path_policy.get_station_location_path()

    def _get_packet_raw_body(self):
        """Returns packet raw body as string.

        Returns:
            str: Packet raw body as string
        """
        try:
            raw_header, raw_body = self.data["raw"].split(':', 1)
        except ValueError:
            raise TrackDirectParseError('Could not split packet into header and body', self.data)

        if len(raw_body) == 0:
            raise TrackDirectParseError('Packet body is empty', self.data)
        return raw_body

    def _parse_packet_phg_rng_timestamps(self, previous_packet):
        """Set current packet timestamp when latest rng / phg was received

        Args:
            previous_packet (Packet): Packet object that represents the packet before the current packet
        """
        if previous_packet.is_existing_object() and self.packet.is_position_equal(previous_packet):
            if (self.packet.phg is None and previous_packet.latest_phg_timestamp is not None
                    and previous_packet.latest_phg_timestamp > (self.packet.timestamp - 86400)):
                self.latest_phg_timestamp = previous_packet.latest_phg_timestamp

            if (self.packet.rng is None and previous_packet.latest_rng_timestamp is not None
                    and previous_packet.latest_rng_timestamp > (self.packet.timestamp - 86400)):
                self.latest_rng_timestamp = previous_packet.latest_rng_timestamp


    def _parse_packet_map_id(self, previous_packet):
        """Set current packet map id and related

        Args:
            previous_packet (Packet): Packet object that represents the packet before the current packet
        """
        map_id_policy = PacketMapIdPolicy(self.packet, previous_packet)
        kill_char_policy = PacketKillCharPolicy()

        if kill_char_policy.has_kill_character(self.data):
            map_id_policy.enable_having_kill_character()

        if map_id_policy.is_replacing_previous_packet():
            self.packet.replace_packet_id = previous_packet.id
            self.packet.replace_packet_timestamp = previous_packet.timestamp

        if map_id_policy.is_confirming_previous_packet():
            self.packet.confirm_packet_id = previous_packet.id
            self.packet.confirm_packet_timestamp = previous_packet.timestamp

        if map_id_policy.is_killing_previous_packet():
            self.packet.abnormal_packet_id = previous_packet.id
            self.packet.abnormal_packet_timestamp = previous_packet.timestamp

        self.packet.map_id = map_id_policy.get_map_id()
        self.packet.marker_id = map_id_policy.get_marker_id()

        if self.packet.marker_id is None:
            # Policy could not find a marker id to use, create a new
            self.packet.marker_id = self._get_new_marker_id()
            if self.packet.marker_id == 1:
                self.packet.map_id = 4


    def _parse_packet_previous_timestamps(self, previous_packet):
        """Set packet previous timestamps and related

        Args:
            previous_packet (Packet): Packet object that represents the packet before the current packet
        """
        if previous_packet.is_existing_object() and self.packet.marker_id == previous_packet.marker_id:
            is_position_equal = self.packet.is_position_equal(previous_packet)
            if (not self.database_write_access and is_position_equal and self.packet.is_moving == 1
                    and previous_packet.position_timestamp == previous_packet.timestamp):
                # This is probably the exact same packet
                self.packet.marker_prev_packet_timestamp = previous_packet.marker_prev_packet_timestamp
                self.packet.marker_counter = previous_packet.marker_counter
                self.packet.position_timestamp = self.packet.timestamp
            else:
                self.packet.marker_prev_packet_timestamp = previous_packet.timestamp
                self.packet.marker_counter = previous_packet.marker_counter + 1
                if is_position_equal:
                    self.packet.position_timestamp = previous_packet.position_timestamp
                else:
                    self.packet.position_timestamp = self.packet.timestamp


    def _parse_assumed_move_type_id(self, previous_packet):
        """Set current packet move type id

        Args:
            previous_packet (Packet): Packet object that represents the packet before the current packet
        """
        packet_assumed_move_type_policy = PacketAssumedMoveTypePolicy(self.db)
        self.packet.is_moving = packet_assumed_move_type_policy.get_assumed_move_type(self.packet, previous_packet)


    def _parse_packet_tail(self, previous_packet):
        """Set current packet tail timestamp

        Args:
            previous_packet (Packet): Packet object that represents the packet before the current packet
        """
        packet_tail_policy = PacketTailPolicy(self.packet, previous_packet)
        self.packet.packet_tail_timestamp = packet_tail_policy.get_packet_tail_timestamp()


    def _parse_packet_related_map_sectors(self, previous_packet):
        """Set current packet related map sectors

        Args:
            previous_packet (Packet): Packet object that represents the packet before the current packet
        """
        packet_related_map_sectors_policy = PacketRelatedMapSectorsPolicy(self.packet_repository)
        self.packet.related_map_sectors = packet_related_map_sectors_policy.get_all_related_map_sectors(self.packet, previous_packet)


    def _get_new_marker_id(self):
        """Creates a new marker id

        Returns:
            int
        """
        if not self.database_write_access:
            return 1
        else:
            # No suitable marker id found, let's create a new!
            marker = self.markerRepository.create()
            marker.save()
            return marker.id