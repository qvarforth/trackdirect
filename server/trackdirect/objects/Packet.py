import logging
import json
from math import sin, cos, sqrt, atan2, radians

from server.trackdirect.common.Model import Model
from server.trackdirect.repositories.StationRepository import StationRepository
from server.trackdirect.repositories.SenderRepository import SenderRepository
from server.trackdirect.exceptions.TrackDirectMissingSenderError import TrackDirectMissingSenderError
from server.trackdirect.exceptions.TrackDirectMissingStationError import TrackDirectMissingStationError


class Packet(Model):
    """Packet represents an APRS packet, AIS packet or any other supported packet

    Note:
        Packet corresponds to a row in the packetYYYYMMDD table
    """

    def __init__(self, db):
        """The __init__ method.

        Args:
            db (psycopg2.Connection): Database connection
        """
        super().__init__(db)
        self.logger = logging.getLogger('trackdirect')

        self.id = None
        self.station_id = None
        self.sender_id = None
        self.packet_type_id = None
        self.timestamp = None
        self.reported_timestamp = None
        self.position_timestamp = None  # Inherited from prev packet if position was equal
        self.latitude = None
        self.longitude = None
        self.symbol = None
        self.symbol_table = None
        self.marker_id = None
        self.marker_counter = None
        self.marker_prev_packet_timestamp = None
        self.map_id = None
        self.source_id = None
        self.map_sector = None
        self.related_map_sectors = []
        self.speed = None
        self.course = None
        self.altitude = None
        self.rng = None
        self.phg = None
        self.latest_rng_timestamp = None
        self.latest_phg_timestamp = None
        self.comment = None
        self.raw_path = None
        self.raw = None

        # packet tail timestamp indicates how long time ago we had a tail
        self.packet_tail_timestamp = None

        # If packet reports a new position for a moving symbol is_moving will be 1 otherwise 0
        # Sometimes is_moving will be 0 for a moving symbol, but as fast we realize it is moving related packets will have is_moving set to 1
        self.is_moving = 1

        self.posambiguity = None

        # Following attributes will not always be loaded from database (comes from related tables)
        self.station_id_path = []
        self.station_name_path = []
        self.station_location_path = []

        # Will only be used when packet is not inserted to database yet
        self.replace_packet_id = None
        self.replace_packet_timestamp = None
        self.abnormal_packet_id = None
        self.abnormal_packet_timestamp = None
        self.confirm_packet_id = None
        self.confirm_packet_timestamp = None

        # Will only be used when packet is not inserted to database yet
        self.ogn = None
        self.weather = None
        self.telemetry = None
        self.station_telemetry_bits = None
        self.station_telemetry_eqns = None
        self.station_telemetry_param = None
        self.station_telemetry_unit = None
        self.senderName = None
        self.stationName = None

    def validate(self) -> bool:
        """Returns true on success (when object content is valid), otherwise false

        Returns:
            True on success otherwise False
        """
        return True

    def insert(self) -> bool:
        """Method to call when we want to save a new object to database

        Since packet will be inserted in batch we never use this method.

        Returns:
            True on success otherwise False
        """
        return False

    def update(self) -> bool:
        """Method to call when we want to save changes to database

        Since packet will be updated in batch we never use this method.

        Returns:
            True on success otherwise False
        """
        return False

    def get_distance(self, p2_lat: float, p2_lng: float) -> float | None:
        """Get distance in meters between current position and specified position

        Args:
            p2_lat (float): Position 2 latitude
            p2_lng (float): Position 2 longitude

        Returns:
            Distance in meters between the two specified positions (as float)
        """
        if self.latitude is not None and self.longitude is not None:
            p1_lat = self.latitude
            p1_lng = self.longitude
            R = 6378137  # Earth's mean radius in meters
            d_lat = radians(p2_lat - p1_lat)
            d_long = radians(p2_lng - p1_lng)
            a = sin(d_lat / 2) ** 2 + cos(radians(p1_lat)) * cos(radians(p2_lat)) * sin(d_long / 2) ** 2
            c = 2 * atan2(sqrt(a), sqrt(1 - a))
            d = R * c
            return d  # returns the distance in meters
        return None

    def get_calculated_speed(self, prev_packet: 'Packet') -> float | None:
        """Get speed compared to previous packet position and timestamp

        Args:
            prev_packet (Packet):  Previous related packet for the same station

        Returns:
            Speed in km/h compared to previous packet position and timestamp (as float)
        """
        if self.latitude is not None and self.longitude is not None:
            distance = self.get_distance(prev_packet.latitude, prev_packet.longitude)
            time = abs(prev_packet.timestamp - self.timestamp)
            if (self.reported_timestamp is not None
                    and prev_packet.reported_timestamp is not None
                    and self.reported_timestamp != 0
                    and prev_packet.reported_timestamp != 0
                    and (self.reported_timestamp % 60 != 0 or prev_packet.reported_timestamp % 60 != 0)
                    and prev_packet.reported_timestamp != self.reported_timestamp):
                time = abs(prev_packet.reported_timestamp - self.reported_timestamp)

            if time == 0:
                return 0
            return distance / time  # meters per second
        return None

    def is_symbol_equal(self, compare_packet: 'Packet') -> bool:
        """Returns true if current symbol is equal to symbol in specified packet

        Args:
            compare_packet (Packet): Packet to compare current symbol with

        Returns:
            True if current symbol is equal to symbol in specified packet
        """
        return (self.symbol is not None
                and self.symbol_table is not None
                and compare_packet.symbol is not None
                and compare_packet.symbol_table is not None
                and self.symbol == compare_packet.symbol
                and self.symbol_table == compare_packet.symbol_table)

    def is_position_equal(self, compare_packet: 'Packet') -> bool:
        """Returns true if current position is equal to position in specified packet

        Args:
            compare_packet (Packet): Packet to compare current position with

        Returns:
            True if current position is equal to position in specified packet
        """
        return (compare_packet.latitude is not None
                and compare_packet.longitude is not None
                and self.longitude is not None
                and self.latitude is not None
                and round(self.latitude, 5) == round(compare_packet.latitude, 5)
                and round(self.longitude, 5) == round(compare_packet.longitude, 5))

    def get_transmit_distance(self) -> float | None:
        """Calculate the transmit distance

        Notes:
            require that stationLocationPath is set

        Returns:
            Distance in meters for this transmission
        """
        if not self.station_location_path:
            return None

        location = self.station_location_path[0]
        if location[0] is None or location[1] is None:
            return None

        if self.latitude is not None and self.longitude is not None:
            # Current packet contains position, use that
            return self.get_distance(location[0], location[1])
        else:
            # Current packet is missing position, use latest station position
            stationRepository = StationRepository(self.db)
            station = stationRepository.get_object_by_id(self.station_id)
            if not station.is_existing_object():
                return None

            if station.latest_confirmed_latitude is not None and station.latest_confirmed_longitude is not None:
                curStationLatestLocationPacket = Packet(self.db)
                curStationLatestLocationPacket.latitude = station.latest_confirmed_latitude
                curStationLatestLocationPacket.longitude = station.latest_confirmed_longitude
                return curStationLatestLocationPacket.get_distance(location[0], location[1])
            return None

    def get_dict(self, include_station_name: bool = False) -> dict:
        """Returns a dict representation of the object

        Args:
            include_station_name (Boolean):  Include station name and sender name in dict

        Returns:
            Dict representation of the object
        """
        data = {
            'id': self.id,
            'station_id': int(self.station_id) if self.station_id is not None else None,
            'sender_id': int(self.sender_id) if self.sender_id is not None else None,
            'packet_type_id': self.packet_type_id,
            'timestamp': self.timestamp,
            'reported_timestamp': self.reported_timestamp,
            'position_timestamp': self.position_timestamp,
            'latitude': float(self.latitude) if self.latitude is not None else None,
            'longitude': float(self.longitude) if self.longitude is not None else None,
            'symbol': self.symbol,
            'symbol_table': self.symbol_table,
            'marker_id': self.marker_id,
            'marker_counter': self.marker_counter,
            'map_id': self.map_id,
            'source_id': self.source_id,
            'map_sector': self.map_sector,
            'related_map_sectors': self.related_map_sectors,
            'speed': self.speed,
            'course': self.course,
            'altitude': self.altitude,
            'rng': self.rng,
            'phg': self.phg,
            'latest_phg_timestamp': self.latest_phg_timestamp,
            'latest_rng_timestamp': self.latest_rng_timestamp,
            'comment': self.comment,
            'raw_path': self.raw_path,
            'raw': self.raw,
            'packet_tail_timestamp': self.packet_tail_timestamp,
            'is_moving': self.is_moving,
            'posambiguity': self.posambiguity,
            'db': 1,
            'station_id_path': self.station_id_path,
            'station_name_path': self.station_name_path,
            'station_location_path': self.station_location_path,
            'telemetry': self.telemetry.get_dict() if self.telemetry is not None else None,
            'weather': self.weather.get_dict() if self.weather is not None else None,
            'ogn': self.ogn.get_dict() if self.ogn is not None else None,
        }

        if include_station_name:
            try:
                stationRepository = StationRepository(self.db)
                station = stationRepository.get_cached_object_by_id(data['station_id'])
                data['station_name'] = station.name
            except TrackDirectMissingStationError:
                data['station_name'] = ''

            try:
                senderRepository = SenderRepository(self.db)
                sender = senderRepository.get_cached_object_by_id(data['sender_id'])
                data['sender_name'] = sender.name
            except TrackDirectMissingSenderError:
                data['sender_name'] = ''

        return data

    def get_json(self) -> str | None:
        """Returns a json representation of the object

        Returns:
            Json representation of the object (returns None on failure)
        """
        data = self.get_dict()

        try:
            return json.dumps(data, ensure_ascii=False).encode('utf8')
        except ValueError as e:
            self.logger.error(e, exc_info=1)

        return None