import logging
from twisted.python import log
import json
import datetime
import time
import calendar
import hashlib

from trackdirect.exceptions.TrackDirectParseError import TrackDirectParseError
from trackdirect.exceptions.TrackDirectMissingSenderError import TrackDirectMissingSenderError
from trackdirect.exceptions.TrackDirectMissingStationError import TrackDirectMissingStationError

from trackdirect.repositories.OgnHiddenStationRepository import OgnHiddenStationRepository
from trackdirect.repositories.OgnDeviceRepository import OgnDeviceRepository
from trackdirect.repositories.StationRepository import StationRepository
from trackdirect.repositories.SenderRepository import SenderRepository
from trackdirect.repositories.PacketRepository import PacketRepository
from trackdirect.repositories.PacketTelemetryRepository import PacketTelemetryRepository
from trackdirect.repositories.PacketWeatherRepository import PacketWeatherRepository
from trackdirect.repositories.PacketOgnRepository import PacketOgnRepository
from trackdirect.repositories.MarkerRepository import MarkerRepository
from trackdirect.repositories.StationTelemetryBitsRepository import StationTelemetryBitsRepository
from trackdirect.repositories.StationTelemetryEqnsRepository import StationTelemetryEqnsRepository
from trackdirect.repositories.StationTelemetryParamRepository import StationTelemetryParamRepository
from trackdirect.repositories.StationTelemetryUnitRepository import StationTelemetryUnitRepository

from trackdirect.objects.Packet import Packet
from trackdirect.objects.Station import Station
from trackdirect.objects.PacketWeather import PacketWeather
from trackdirect.objects.PacketTelemetry import PacketTelemetry
from trackdirect.objects.Marker import Marker
from trackdirect.objects.OgnHiddenStation import OgnHiddenStation
from trackdirect.objects.OgnDevice import OgnDevice

from trackdirect.parser.policies.AprsPacketTypePolicy import AprsPacketTypePolicy
from trackdirect.parser.policies.PacketAssumedMoveTypePolicy import PacketAssumedMoveTypePolicy
from trackdirect.parser.policies.PacketSpeedComputablePolicy import PacketSpeedComputablePolicy
from trackdirect.parser.policies.PreviousPacketPolicy import PreviousPacketPolicy
from trackdirect.parser.policies.PacketTailPolicy import PacketTailPolicy
from trackdirect.parser.policies.PacketRelatedMapSectorsPolicy import PacketRelatedMapSectorsPolicy
from trackdirect.parser.policies.PacketMapIdPolicy import PacketMapIdPolicy
from trackdirect.parser.policies.PacketPathPolicy import PacketPathPolicy
from trackdirect.parser.policies.MapSectorPolicy import MapSectorPolicy
from trackdirect.parser.policies.PacketCommentPolicy import PacketCommentPolicy
from trackdirect.parser.policies.PacketKillCharPolicy import PacketKillCharPolicy
from trackdirect.parser.policies.StationNameFormatPolicy import StationNameFormatPolicy
from trackdirect.parser.policies.PacketOgnDataPolicy import PacketOgnDataPolicy


class AprsPacketParser():
    """AprsPacketParser tackes a aprslib output and converts it to a Trackdirect Packet
    """

    def __init__(self, db, saveOgnStationsWithMissingIdentity):
        """The __init__ method.

        Args:
            db (psycopg2.Connection):                       Database connection
            saveOgnStationsWithMissingIdentity (boolean):   True if we should not ignore stationss with a missing identity
        """
        self.db = db
        self.saveOgnStationsWithMissingIdentity = saveOgnStationsWithMissingIdentity
        self.logger = logging.getLogger('trackdirect')

        self.databaseWriteAccess = True
        self.sourceId = 1

        self.ognDeviceRepository = OgnDeviceRepository(db)
        self.ognHiddenStationRepository = OgnHiddenStationRepository(db)
        self.stationRepository = StationRepository(db)
        self.senderRepository = SenderRepository(db)
        self.packetRepository = PacketRepository(db)
        self.packetTelemetryRepository = PacketTelemetryRepository(db)
        self.packetWeatherRepository = PacketWeatherRepository(db)
        self.packetOgnRepository = PacketOgnRepository(db)
        self.markerRepository = MarkerRepository(db)
        self.stationTelemetryBitsRepository = StationTelemetryBitsRepository(db)
        self.stationTelemetryEqnsRepository = StationTelemetryEqnsRepository(db)
        self.stationTelemetryParamRepository = StationTelemetryParamRepository(db)
        self.stationTelemetryUnitRepository = StationTelemetryUnitRepository(db)

    def setDatabaseWriteAccess(self, databaseWriteAccess):
        """Enable or disable database updates

        Args:
            databaseWriteAccess (boolean):   True if we have database access otherwise false
        """
        self.databaseWriteAccess = databaseWriteAccess

    def setSourceId(self, sourceId):
        """Set what source packet is from (APRS, CWOP ...)

        Args:
            sourceId (int):  Id that corresponds to id in source-table
        """
        self.sourceId = sourceId

    def getPacket(self, data, timestamp=None, minimal=False):
        """Returns the resulting packet

        Args:
            data (dict):            Raw packet data
            timestamp (int):        Packet timestamp
            minimal (boolean):      Set to true to only perform minimal parsing

        Returns:
            Packet
        """
        self.isHiddenStation = False
        self.data = data
        self.packet = Packet(self.db)
        self.packet.sourceId = self.sourceId
        self._parsePacketInitialValues(timestamp)
        self._parsePacketReportedTimestamp()

        # Parse OGN stuff before station-id, may result in no station to create
        self._parsePacketOgn()
        if (self.packet.mapId != 15):
            self._parsePacketType()
            self._parsePacketSender()
            self._parsePacketStationName()
            self._parsePacketStationId()

            self._parsePacketRng()
            self._parsePacketPhg()

            if (self.packet.stationId is None):
                self.packet.mapId = 4
            else:
                self._parsePacketComment()
                self._parsePacketWeather()
                self._parsePacketTelemetryDefinition()
                self._parsePacketTelemetry()
                self._parsePacketPosition()
                self._parsePacketPath()

                if (not minimal):
                    previousPacketPolicy = PreviousPacketPolicy(
                        self.packet, self.db)
                    previousPacket = previousPacketPolicy.getPreviousPacket()
                    self._parseAssumedMoveTypeId(previousPacket)
                    self._parsePacketTail(previousPacket)
                    self._parsePacketMapId(previousPacket)
                    self._parsePacketPreviousTimestamps(previousPacket)
                    self._parsePacketPhgRngTimestamps(previousPacket)
                    self._parsePacketRelatedMapSectors(previousPacket)

        if (self.isHiddenStation):
            if (self.packet.ogn is not None):
                self.packet.ogn.ognAddressTypeId = None
                self.packet.ogn.ognSenderAddress = None
            self.packet.comment = None
            self.packet.raw = None
        return self.packet

    def _parsePacketInitialValues(self, timestamp):
        """Set packet initial values

        Args:
            timestamp (int):    Packet timestamp
        """
        self.packet.raw = self.data['raw'].replace('\x00', '')
        self.packet.symbol = self.data['symbol'] if (
            'symbol' in self.data) else None
        self.packet.symbolTable = self.data['symbol_table'] if (
            'symbol_table' in self.data) else None
        self.packet.reportedTimestamp = self.data['timestamp'] if (
            'timestamp' in self.data) else None
        self.packet.rawPath = self.data['to'] + ',' + ','.join(self.data['path']) if (
            'path' in self.data and 'to' in self.data) else None
        if (timestamp is not None):
            self.packet.timestamp = timestamp
        else:
            self.packet.timestamp = int(time.time())
        self.packet.positionTimestamp = self.packet.timestamp
        self.packet.packetTailTimestamp = 0
        self.packet.posambiguity = self.data['posambiguity'] if (
            'posambiguity' in self.data) else None
        self.packet.speed = self.data['speed'] if (
            'speed' in self.data) else None
        self.packet.course = self.data['course'] if (
            'course' in self.data) else None
        self.packet.altitude = self.data['altitude'] if (
            'altitude' in self.data) else None
        self.packet.mapId = 10  # Default map for a packet without a position
        self.packet.markerId = 1
        self.packet.markerCounter = 1  # We allways start at 1

    def _parsePacketReportedTimestamp(self):
        """Set packet reported timestamp
        """
        if ('timestamp' in self.data):
            reportedTimestampDay = int(datetime.datetime.utcfromtimestamp(
                int(self.data['timestamp'])).strftime('%d'))
            currentTimestampDay = int(datetime.datetime.utcfromtimestamp(
                self.packet.timestamp).strftime('%d'))
            if (reportedTimestampDay > currentTimestampDay and self.data['timestamp'] > self.packet.timestamp):
                # Day is in the future, the reported timestamp was probably in previous month

                prevMonth = int(datetime.datetime.utcfromtimestamp(
                    int(self.data['timestamp']) - (reportedTimestampDay+1)*24*60*60).strftime('%m'))
                prevMonthYear = int(datetime.datetime.utcfromtimestamp(
                    int(self.data['timestamp']) - (reportedTimestampDay+1)*24*60*60).strftime('%Y'))
                numberOfDaysInMonth = int(
                    calendar.monthrange(prevMonthYear, prevMonth)[1])

                self.packet.reportedTimestamp = int(
                    self.data['timestamp']) - (numberOfDaysInMonth*24*60*60)
        else:
            self.packet.reportedTimestamp = None

    def _parsePacketRng(self):
        """Set packet RNG data
        """
        if ('rng' in self.data):
            try:
                self.packet.rng = float(self.data['rng'])
                self.packet.latestRngTimestamp = self.packet.timestamp
                if (self.packet.rng <= 0):
                    self.packet.rng = None
            except ValueError:
                # Not a float
                self.packet.rng = None

    def _parsePacketPhg(self):
        """Set packet PHG data
        """
        if ('phg' in self.data):
            phg = str(self.data['phg'])[0:4]
            if (len(phg) == 4 and phg.isdigit()):
                self.packet.phg = phg
                self.packet.latestPhgTimestamp = self.packet.timestamp

    def _parsePacketSender(self):
        """Set sender id and name
        """
        stationNameFormatPolicy = StationNameFormatPolicy()
        self.packet.senderName = stationNameFormatPolicy.getCorrectFormat(
            self.data["from"])
        try:
            sender = self.senderRepository.getCachedObjectByName(
                self.packet.senderName)
            self.packet.senderId = sender.id
        except (TrackDirectMissingSenderError) as exp:
            if (self.databaseWriteAccess):
                sender = self.senderRepository.getObjectByName(
                    self.packet.senderName, True, self.packet.sourceId)
                self.packet.senderId = sender.id

    def _parsePacketStationName(self):
        """Set station name
        """
        if ("object_name" in self.data
                and self.data["object_name"] is not None
                and self.data["object_name"] != ''):
            self.packet.stationTypeId = 2
            stationNameFormatPolicy = StationNameFormatPolicy()
            self.packet.stationName = stationNameFormatPolicy.getCorrectFormat(
                self.data["object_name"])
            if (self.packet.stationName is None or self.packet.stationName == ''):
                self.packet.stationName = self.packet.senderName
            if (self.packet.stationName == self.packet.senderName):
                self.packet.stationTypeId = 1
        else:
            self.packet.stationTypeId = 1
            self.packet.stationName = self.packet.senderName

    def _parsePacketStationId(self):
        """Set station id
        """
        if (self.packet.stationName is None):
            return
        try:
            station = self.stationRepository.getCachedObjectByName(
                self.packet.stationName,
                self.packet.sourceId
            )
            self.packet.stationId = station.id

            if (self.packet.stationName != station.name):
                # Station lower/upper case is modified
                station.name = self.packet.stationName
                station.save()

            if (station.stationTypeId != self.packet.stationTypeId and int(self.packet.stationTypeId) == 1):
                # Switch to station type 1
                station.stationTypeId = self.packet.stationTypeId
                station.save()

        except (TrackDirectMissingStationError) as exp:
            if (self.databaseWriteAccess):
                station = self.stationRepository.getObjectByName(
                    self.packet.stationName,
                    self.packet.sourceId,
                    self.packet.stationTypeId,
                    True
                )
                self.packet.stationId = station.id

    def _parsePacketComment(self):
        """Set packet comment
        """
        commentPolicy = PacketCommentPolicy()
        self.packet.comment = commentPolicy.getComment(
            self.data, self.packet.packetTypeId)

    def _parsePacketOgn(self):
        """Set th OGN sender address
        """
        ognDataPolicy = PacketOgnDataPolicy(
            self.data, self.ognDeviceRepository, self.packet.sourceId)
        if (ognDataPolicy.isOgnPositionPacket):
            originalRaw = self.packet.raw

            if (not ognDataPolicy.isAllowedToTrack):
                self.packet.mapId = 15
                return

            elif (not ognDataPolicy.isAllowedToIdentify):
                if (not self.saveOgnStationsWithMissingIdentity) :
                    self.packet.mapId = 15
                    return
                self.isHiddenStation = True
                self.data["from"] = self._getHiddenStationName()
                self.data["object_name"] = None

            self.data['ogn'] = ognDataPolicy.getOgnData()
            if (self.data['ogn'] is not None):
                self.packet.ogn = self.packetOgnRepository.getObjectFromPacketData(
                    self.data)
                self.packet.ogn.stationId = self.packet.stationId
                self.packet.ogn.timestamp = self.packet.timestamp
                self.data["comment"] = None
            self._modifyOgnSymbol(originalRaw)

    def _modifyOgnSymbol(self, originalRaw):
        """Sets a better symbol for an OGN station

        Args:
            originalRaw (string):    Non modified raw
        """
        if ((self.packet.symbol == '\'' and self.packet.symbolTable == '/') or (self.packet.symbol == '^' and self.packet.symbolTable in ['/', '\\']) or (self.packet.symbol == 'g' and self.packet.symbolTable in ['/'])):
            ognDevice = None
            if (self.packet.ogn is not None and self.packet.ogn.ognSenderAddress is not None):
                ognDevice = self.ognDeviceRepository.getObjectByDeviceId(
                    self.packet.ogn.ognSenderAddress)

            if (ognDevice is not None and ognDevice.isExistingObject() and ognDevice.ddbAircraftType > 0 and ognDevice.ddbAircraftType < 6):
                # If another aircraft type exist in device db, use that instead
                if (ognDevice.ddbAircraftType == 1):  # Gliders/motoGliders
                    # Glider -> Glider
                    self.packet.symbol = '^'
                    self.packet.symbolTable = 'G'

                elif (ognDevice.ddbAircraftType == 2):  # Planes
                    # Powered aircraft -> Propeller aircraft
                    self.packet.symbol = '^'
                    self.packet.symbolTable = 'P'

                elif (ognDevice.ddbAircraftType == 3):  # Ultralights
                    # Small plane
                    self.packet.symbol = '\''
                    self.packet.symbolTable = '/'

                elif (ognDevice.ddbAircraftType == 4):  # Helicopters
                    # Helicopter
                    self.packet.symbol = 'X'
                    self.packet.symbolTable = '/'

                elif (ognDevice.ddbAircraftType == 5):  # Drones/UAV
                    # UAV -> Drone
                    self.packet.symbol = '^'
                    self.packet.symbolTable = 'D'

            elif (self.packet.ogn is not None and self.packet.ogn.ognAircraftTypeId is not None):
                if (self.packet.ogn.ognAircraftTypeId == 1):
                    # Glider -> Glider
                    self.packet.symbol = '^'
                    self.packet.symbolTable = 'G'
                elif (self.packet.ogn.ognAircraftTypeId == 9):
                    # Jet aircraft -> Jet
                    self.packet.symbol = '^'
                    self.packet.symbolTable = 'J'
                elif (self.packet.ogn.ognAircraftTypeId == 8):
                    # Powered aircraft -> Propeller aircraft
                    self.packet.symbol = '^'
                    self.packet.symbolTable = 'P'
                elif (self.packet.ogn.ognAircraftTypeId == 13):
                    # UAV -> Drone
                    self.packet.symbol = '^'
                    self.packet.symbolTable = 'D'
                elif (self.packet.ogn.ognAircraftTypeId == 7): #paraglider
                    # map to own symbol 94-76.svg (do not show hangglider symbol 103-1.svg, 'g' = 103)
                    self.packet.symbol = '^' #94
                    self.packet.symbolTable = 'L' #76

        if ((self.packet.symbol == '\'' and self.packet.symbolTable == '/') or (self.packet.symbol == '^' and self.packet.symbolTable in ['/', '\\'])):
            # Current symbol is still "small aircraft" or "large aircraft"
            if (originalRaw.startswith('FMT')):
                # FMT, Remotely Piloted
                self.packet.symbol = '^'
                self.packet.symbolTable = 'R'

    def _getHiddenStationName(self):
        """Returnes a unidentifiable station name

        Returns:
            string
        """
        date = datetime.datetime.utcfromtimestamp(
            self.packet.timestamp).strftime('%Y%m%d')
        dailyStationNameHash = hashlib.sha256(
            self.data["from"] + date).hexdigest()

        ognHiddenStation = self.ognHiddenStationRepository.getObjectByHashedName(
            dailyStationNameHash, True)
        return ognHiddenStation.getStationName()

    def _parsePacketWeather(self):
        """Parse weather data
        """
        if ("weather" in self.data):
            self.packet.weather = self.packetWeatherRepository.getObjectFromPacketData(
                self.data)
            self.packet.weather.stationId = self.packet.stationId
            self.packet.weather.timestamp = self.packet.timestamp

    def _parsePacketTelemetry(self):
        """Parse telemetry data
        """
        if ("telemetry" in self.data):
            self.packet.telemetry = self.packetTelemetryRepository.getObjectFromPacketData(
                self.data)
            self.packet.telemetry.stationId = self.packet.stationId
            self.packet.telemetry.timestamp = self.packet.timestamp

    def _parsePacketTelemetryDefinition(self):
        """Parse telemetry definition
        """
        if ("tBITS" in self.data):
            self.packet.stationTelemetryBits = self.stationTelemetryBitsRepository.getObjectFromPacketData(
                self.data)
            self.packet.stationTelemetryBits.stationId = self.packet.stationId
            self.packet.stationTelemetryBits.timestamp = self.packet.timestamp

        if ("tEQNS" in self.data):
            self.packet.stationTelemetryEqns = self.stationTelemetryEqnsRepository.getObjectFromPacketData(
                self.data)
            self.packet.stationTelemetryEqns.stationId = self.packet.stationId
            self.packet.stationTelemetryEqns.timestamp = self.packet.timestamp

        if ("tPARM" in self.data):
            self.packet.stationTelemetryParam = self.stationTelemetryParamRepository.getObjectFromPacketData(
                self.data)
            self.packet.stationTelemetryParam.stationId = self.packet.stationId
            self.packet.stationTelemetryParam.timestamp = self.packet.timestamp

        if ("tUNIT" in self.data):
            self.packet.stationTelemetryUnit = self.stationTelemetryUnitRepository.getObjectFromPacketData(
                self.data)
            self.packet.stationTelemetryUnit.stationId = self.packet.stationId
            self.packet.stationTelemetryUnit.timestamp = self.packet.timestamp

    def _parsePacketType(self):
        """Set packet type
        """
        aprsPacketTypePolicy = AprsPacketTypePolicy()
        self.packet.packetTypeId = aprsPacketTypePolicy.getPacketType(
            self.packet)

    def _parsePacketPosition(self):
        """Parse the packet position and related attributes
        """
        if ("latitude" in self.data
            and "longitude" in self.data
            and self.data["latitude"] is not None
                and self.data["longitude"] is not None):

            self.packet.latitude = self.data['latitude']
            self.packet.longitude = self.data['longitude']

            mapSectorPolicy = MapSectorPolicy()
            self.packet.mapSector = mapSectorPolicy.getMapSector(
                self.data["latitude"], self.data["longitude"])
            self.packet.mapId = 1  # Default map for a packet with a position
            self.packet.isMoving = 1  # Moving/Stationary, default value is moving

    def _parsePacketPath(self):
        """Parse packet path
        """
        if ("path" in self.data and isinstance(self.data["path"], list)):
            packetPathPolicy = PacketPathPolicy(
                self.data['path'], self.packet.sourceId, self.stationRepository, self.senderRepository)
            self.packet.stationIdPath = packetPathPolicy.getStationIdPath()
            self.packet.stationNamePath = packetPathPolicy.getStationNamePath()
            self.packet.stationLocationPath = packetPathPolicy.getStationLocationPath()

    def _getPacketRawBody(self):
        """Returns packet raw body as string

        Returns:
            Packet raw body as string
        """
        try:
            (rawHeader, rawBody) = self.data["raw"].split(':', 1)
        except:
            raise TrackDirectParseError(
                'Could not split packet into header and body', self.data)

        if len(rawBody) == 0:
            raise TrackDirectParseError('Packet body is empty', self.data)
        return rawBody

    def _parsePacketPhgRngTimestamps(self, previousPacket):
        """Set current packet timestamp when latest rng / phg was received

        Args:
            previousPacket (Packet): Packet object that represents the packet before the current packet
        """
        if (previousPacket.isExistingObject()
                and self.packet.isPostitionEqual(previousPacket)):
            if (self.packet.phg is None
                    and previousPacket.latestPhgTimestamp is not None
                    and previousPacket.latestPhgTimestamp > (self.packet.timestamp - (60*60*24))):
                self.latestPhgTimestamp = previousPacket.latestPhgTimestamp

            if (self.packet.rng is None
                    and previousPacket.latestRngTimestamp is not None
                    and previousPacket.latestRngTimestamp > (self.packet.timestamp - (60*60*24))):
                self.latestRngTimestamp = previousPacket.latestRngTimestamp

    def _parsePacketMapId(self, previousPacket):
        """Set current packet map id and related

        Args:
            previousPacket (Packet): Packet object that represents the packet before the current packet
        """
        mapIdPolicy = PacketMapIdPolicy(self.packet, previousPacket)
        killCharPolicy = PacketKillCharPolicy()
        if (killCharPolicy.hasKillCharacter(self.data)):
            mapIdPolicy.enableHavingKillCharacter()

        if (mapIdPolicy.isReplacingPreviousPacket()):
            self.packet.replacePacketId = previousPacket.id
            self.packet.replacePacketTimestamp = previousPacket.timestamp

        if (mapIdPolicy.isConfirmingPreviousPacket()):
            self.packet.confirmPacketId = previousPacket.id
            self.packet.confirmPacketTimestamp = previousPacket.timestamp

        if (mapIdPolicy.isKillingPreviousPacket()):
            self.packet.abnormalPacketId = previousPacket.id
            self.packet.abnormalPacketTimestamp = previousPacket.timestamp

        self.packet.mapId = mapIdPolicy.getMapId()
        self.packet.markerId = mapIdPolicy.getMarkerId()
        if (self.packet.markerId is None):
            # Policy could not find a marker id to use, create a new
            self.packet.markerId = self._getNewMarkerId()
            if (self.packet.markerId == 1):
                self.packet.mapId = 4

    def _parsePacketPreviousTimestamps(self, previousPacket):
        """Set packet previous timestamps and related

        Args:
            previousPacket (Packet): Packet object that represents the packet before the current packet
        """
        if (previousPacket.isExistingObject()
                and self.packet.markerId == previousPacket.markerId):
            isPostitionEqual = self.packet.isPostitionEqual(previousPacket)
            if (not self.databaseWriteAccess
                    and isPostitionEqual
                    and self.packet.isMoving == 1
                    and previousPacket.positionTimestamp == previousPacket.timestamp):
                # This is probably the exact same packet
                self.packet.markerPrevPacketTimestamp = previousPacket.markerPrevPacketTimestamp
                self.packet.markerCounter = previousPacket.markerCounter
                self.packet.positionTimestamp = self.packet.timestamp
            else:
                self.packet.markerPrevPacketTimestamp = previousPacket.timestamp
                self.packet.markerCounter = previousPacket.markerCounter + 1
                if (isPostitionEqual):
                    self.packet.positionTimestamp = previousPacket.positionTimestamp
                else:
                    self.packet.positionTimestamp = self.packet.timestamp

    def _parseAssumedMoveTypeId(self, previousPacket):
        """Set current packet move type id

        Args:
            previousPacket (Packet): Packet object that represents the packet before the current packet
        """
        packetAssumedMoveTypePolicy = PacketAssumedMoveTypePolicy(self.db)
        self.packet.isMoving = packetAssumedMoveTypePolicy.getAssumedMoveType(self.packet, previousPacket)

    def _parsePacketTail(self, previousPacket):
        """Set current packet tail timestamp

        Args:
            previousPacket (Packet): Packet object that represents the packet before the current packet
        """
        packetTailPolicy = PacketTailPolicy(self.packet, previousPacket)
        self.packet.packetTailTimestamp = packetTailPolicy.getPacketTailTimestamp()

    def _parsePacketRelatedMapSectors(self, previousPacket):
        """Set current packet related map sectors

        Args:
            previousPacket (Packet): Packet object that represents the packet before the current packet
        """
        packetRelatedMapSectorsPolicy = PacketRelatedMapSectorsPolicy(
            self.packetRepository)
        self.packet.relatedMapSectors = packetRelatedMapSectorsPolicy.getAllRelatedMapSectors(
            self.packet, previousPacket)

    def _getNewMarkerId(self):
        """Creates a new marker id

        Returns:
            int
        """
        if (not self.databaseWriteAccess):
            return 1
        else:
            # No suitable marker id found, let's create a new!
            marker = self.markerRepository.create()
            marker.save()
            return marker.id
