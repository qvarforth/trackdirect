import logging
import re
from twisted.python import log
import json
import datetime
import time
from math import sin, cos, sqrt, atan2, radians, floor, ceil

from trackdirect.common.Model import Model
from trackdirect.repositories.StationRepository import StationRepository
from trackdirect.repositories.SenderRepository import SenderRepository
from trackdirect.objects.Station import Station

from trackdirect.exceptions.TrackDirectMissingSenderError import TrackDirectMissingSenderError
from trackdirect.exceptions.TrackDirectMissingStationError import TrackDirectMissingStationError


class Packet(Model):
    """Packet represents a APRS packet, AIS packet or any other supported packet

    Note:
        Packet corresponds to a row in the packetYYYYMMDD table
    """

    def __init__(self, db):
        """The __init__ method.

        Args:
            db (psycopg2.Connection): Database connection
        """
        Model.__init__(self, db)
        self.logger = logging.getLogger('trackdirect')

        self.id = None
        self.stationId = None
        self.senderId = None
        self.packetTypeId = None
        self.timestamp = None
        self.reportedTimestamp = None
        self.positionTimestamp = None # Inherited from prev packet if position was equal
        self.latitude = None
        self.longitude = None
        self.symbol = None
        self.symbolTable = None
        self.markerId = None
        self.markerCounter = None
        self.markerPrevPacketTimestamp = None
        self.mapId = None
        self.sourceId = None
        self.mapSector = None
        self.relatedMapSectors = []
        self.speed = None
        self.course = None
        self.altitude = None
        self.rng = None
        self.phg = None
        self.latestRngTimestamp = None
        self.latestPhgTimestamp = None
        self.comment = None
        self.rawPath = None
        self.raw = None

        # packet tail timestamp indicates how long time ago we had a tail
        self.packetTailTimestamp = None

        # If packet reports a new position for a moving symbol is_moving will be 1 otherwise 0
        # Some times is_moving will be 0 for a moving symbol, but as fast we realize it is moving related packets will have is_moving set to 1
        self.isMoving = 1

        self.posambiguity = None

        # Following attributes will not allways be loaded from database (comes from related tables)
        self.stationIdPath = []
        self.stationNamePath = []
        self.stationLocationPath = []

        # Will only be used when packet is not inserted to database yet
        self.replacePacketId = None
        self.replacePacketTimestamp = None
        self.abnormalPacketId = None
        self.abnormalPacketTimestamp = None
        self.confirmPacketId = None
        self.confirmPacketTimestamp = None

        # Will only be used when packet is not inserted to database yet
        self.ogn = None
        self.weather = None
        self.telemetry = None
        self.stationTelemetryBits = None
        self.stationTelemetryEqns = None
        self.stationTelemetryParam = None
        self.stationTelemetryUnit = None
        self.senderName = None
        self.stationName = None

    def validate(self):
        """Returns true on success (when object content is valid), otherwise false

        Returns:
            True on success otherwise False
        """
        return True

    def insert(self):
        """Method to call when we want to save a new object to database

        Since packet will be inserted in batch we never use this method.

        Returns:
            True on success otherwise False
        """
        return False

    def update(self):
        """Method to call when we want to save changes to database

        Since packet will be updated in batch we never use this method.

        Returns:
            True on success otherwise False
        """
        return False

    def getDistance(self, p2Lat, p2Lng):
        """Get distance in meters between current position and specified position

        Args:
            p2Lat (float): Position 2 latitude
            p2Lng (float): Position 2 longitude

        Returns:
            Distance in meters between the two specified positions (as float)
        """
        if (self.latitude is not None
                and self.longitude is not None):
            p1Lat = self.latitude
            p1Lng = self.longitude
            R = 6378137  # Earths mean radius in meter
            dLat = radians(p2Lat - p1Lat)
            dLong = radians(p2Lng - p1Lng)
            a = sin(dLat / 2) * sin(dLat / 2) + cos(radians(p1Lat)) * \
                cos(radians(p2Lat)) * sin(dLong / 2) * sin(dLong / 2)
            c = 2 * atan2(sqrt(a), sqrt(1 - a))
            d = R * c
            return d  # returns the distance in meter
        else:
            return None

    def getCalculatedSpeed(self, prevPacket):
        """Get speed compared to previous packet position and timestamp

        Args:
            prevPacket (Packet):  Previous related packet for the same station

        Returns:
            Speed in kmh compared to previous packet position and timestamp (as float)
        """
        if (self.latitude is not None
                and self.longitude is not None):
            distance = self.getDistance(
                prevPacket.latitude, prevPacket.longitude)
            time = abs(prevPacket.timestamp - self.timestamp)
            if (self.reportedTimestamp is not None
                    and prevPacket.reportedTimestamp is not None
                    and self.reportedTimestamp != 0
                    and prevPacket.reportedTimestamp != 0
                    and (self.reportedTimestamp % 60 != 0 or prevPacket.reportedTimestamp % 60 != 0)
                    and prevPacket.reportedTimestamp != self.reportedTimestamp):
                time = abs(prevPacket.reportedTimestamp -
                           self.reportedTimestamp)

            if (time == 0):
                return 0
            return distance / time  # meters per second
        else:
            return None

    def isSymbolEqual(self, comparePacket):
        """Returns true if current symbol is equal to symbol in specified packet

        Args:
            comparePacket (Packet): Packet to compare current symbol with

        Returns:
            True if current symbol is equal to symbol in specified packet
        """
        if (self.symbol is not None
            and self.symbolTable is not None
            and comparePacket.symbol is not None
            and comparePacket.symbolTable is not None
            and self.symbol == comparePacket.symbol
                and self.symbolTable == comparePacket.symbolTable):
            return True
        else:
            return False

    def isPostitionEqual(self, comparePacket):
        """Returns true if current position is equal to position in specified packet

        Args:
            comparePacket (Packet): Packet to compare current position with

        Returns:
            True if current position is equal to position in specified packet
        """
        if (comparePacket.latitude is not None
              and comparePacket.longitude is not None
              and self.longitude is not None
              and self.latitude is not None
              and round(self.latitude, 5) == round(comparePacket.latitude, 5)
              and round(self.longitude, 5) == round(comparePacket.longitude, 5)):
            return True
        else:
            return False

    def getTransmitDistance(self):
        """Calculate the transmit distance

        Notes:
            require that stationLocationPath is set

        Args:
            None

        Returns:
            Distance in meters for this transmission
        """
        if (self.stationLocationPath is None
                or len(self.stationLocationPath) < 1):
            return None

        location = self.stationLocationPath[0]
        if (location[0] is None
                or location[1] is None):
            return None

        if (self.latitude is not None
                and self.longitude is not None):

            # Current packet contains position, use that
            return self.getDistance(location[0], location[1])
        else:

            # Current packet is missing position, use latest station position
            stationRepository = StationRepository(self.db)
            station = stationRepository.getObjectById(self.stationId)
            if (not station.isExistingObject()):
                return None

            if (station.latestConfirmedLatitude is not None and station.latestConfirmedLongitude is not None):
                curStationLatestLocationPacket = Packet(self.db)
                curStationLatestLocationPacket.latitude = station.latestConfirmedLatitude
                curStationLatestLocationPacket.longitude = station.latestConfirmedLongitude
                return curStationLatestLocationPacket.getDistance(location[0], location[1])
            else:
                return None

    def getDict(self, includeStationName=False):
        """Returns a dict representation of the object

        Args:
            includeStationName (Boolean):  Include station name and sender name in dict

        Returns:
            Dict representation of the object
        """
        data = {}
        data['id'] = self.id

        if (self.stationId is not None):
            data['station_id'] = int(self.stationId)
        else:
            data['station_id'] = None

        if (self.senderId is not None):
            data['sender_id'] = int(self.senderId)
        else:
            data['sender_id'] = None

        data['packet_type_id'] = self.packetTypeId
        data['timestamp'] = self.timestamp
        data['reported_timestamp'] = self.reportedTimestamp
        data['position_timestamp'] = self.positionTimestamp

        if (self.latitude is not None and self.longitude is not None):
            data['latitude'] = float(self.latitude)
            data['longitude'] = float(self.longitude)
        else:
            data['latitude'] = None
            data['longitude'] = None

        data['symbol'] = self.symbol
        data['symbol_table'] = self.symbolTable
        data['marker_id'] = self.markerId
        data['marker_counter'] = self.markerCounter
        data['map_id'] = self.mapId
        data['source_id'] = self.sourceId
        data['map_sector'] = self.mapSector
        data['related_map_sectors'] = self.relatedMapSectors
        data['speed'] = self.speed
        data['course'] = self.course
        data['altitude'] = self.altitude
        data['rng'] = self.rng
        data['phg'] = self.phg
        data['latest_phg_timestamp'] = self.latestPhgTimestamp
        data['latest_rng_timestamp'] = self.latestRngTimestamp
        data['comment'] = self.comment
        data['raw_path'] = self.rawPath
        data['raw'] = self.raw
        data['packet_tail_timestamp'] = self.packetTailTimestamp
        data['is_moving'] = self.isMoving
        data['posambiguity'] = self.posambiguity
        data['db'] = 1

        if (includeStationName):
            try:
                stationRepository = StationRepository(self.db)
                station = stationRepository.getCachedObjectById(
                    data['station_id'])
                data['station_name'] = station.name
            except TrackDirectMissingStationError as e:
                data['station_name'] = ''

            try:
                senderRepository = SenderRepository(self.db)
                sender = senderRepository.getCachedObjectById(
                    data['sender_id'])
                data['sender_name'] = sender.name
            except TrackDirectMissingSenderError as e:
                data['sender_name'] = ''

        data['station_id_path'] = self.stationIdPath
        data['station_name_path'] = self.stationNamePath
        data['station_location_path'] = self.stationLocationPath
        data['telemetry'] = None
        if (self.telemetry is not None):
            data['telemetry'] = self.telemetry.getDict()
        data['weather'] = None
        if (self.weather is not None):
            data['weather'] = self.weather.getDict()
        data['ogn'] = None
        if (self.ogn is not None):
            data['ogn'] = self.ogn.getDict()
        return data

    def getJson(self):
        """Returns a json representation of the object

        Returns:
            Json representation of the object (returnes None on failure)
        """
        data = self.getDict()

        try:
            return json.dumps(data, ensure_ascii=False).encode('utf8')
        except (ValueError) as exp:
            self.logger.error(e, exc_info=1)

        return None
