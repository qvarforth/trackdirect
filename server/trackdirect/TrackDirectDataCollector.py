import logging
import psycopg2
import psycopg2.extras
import re
import aprslib
import datetime
import time
from twisted.internet import reactor, threads

from trackdirect.parser.AprsPacketParser import AprsPacketParser
from trackdirect.parser.AprsISConnection import AprsISConnection
from trackdirect.parser.policies.PacketDuplicatePolicy import PacketDuplicatePolicy
from trackdirect.collector.PacketBatchInserter import PacketBatchInserter
from trackdirect.exceptions.TrackDirectParseError import TrackDirectParseError
from trackdirect.database.DatabaseConnection import DatabaseConnection
from trackdirect.repositories.StationRepository import StationRepository

#from pympler.tracker import SummaryTracker

class TrackDirectDataCollector():
    """An TrackDirectDataCollector instance connects to the data source and saves all received packets to the database

    Note:
        The collector class is built to handle ONE connection to a data source server (may be a APRS-IS server), if two is wanted run two processes.
        This is useful if you want one connection to the regular APRS-IS network and one connection to the CWOP network.
    """

    def __init__(self, collectorOptions, saveOgnStationsWithMissingIdentity):
        """The __init__ method.

        Args:
            collectorOptions (dict):                       Contains data like host, port, callsign, passcode, source id
            saveOgnStationsWithMissingIdentity (boolean):  True if we should not ignore stationss with a missing identity
        """
        self.saveOgnStationsWithMissingIdentity = saveOgnStationsWithMissingIdentity
        self.sourceHostname = collectorOptions['host']
        self.sourcePort = collectorOptions['port_full']
        self.numbersInBatch = collectorOptions['numbers_in_batch']
        self.saveFastPackets = collectorOptions['save_fast_packets']
        self.frequencyLimit = collectorOptions['frequency_limit']
        self.detectDuplicates = collectorOptions['detect_duplicates']
        self.hardFrequencyLimit = None
        if (not self.saveFastPackets and self.frequencyLimit is not None and int(self.frequencyLimit) > 0):
            # Only respect hard frequency limit if we are not saving "fast packets"
            self.hardFrequencyLimit = self.frequencyLimit
        self.sourceId = collectorOptions['source_id']
        self.callsign = collectorOptions['callsign']
        self.passcode = collectorOptions['passcode']

        dbConnection = DatabaseConnection()
        self.db = dbConnection.getConnection(True)
        self.dbNoAutoCommit = dbConnection.getConnection(False)

        self.stationRepository = StationRepository(self.db)
        self.logger = logging.getLogger(__name__)

        self.latestPacketTimestamp = None
        self.firstPacketTimestamp = None
        self.latestBatchInsertTimestamp = int(time.time())

        self.packets = []
        self.stationIdsWithVisiblePacket = []
        self.movingStationIdsWithVisiblePacket = []
        self.movingMarkerIdsWithVisiblePacket = []
        self.delay = 0

    def run(self):
        """Start the collector
        """
        threads.deferToThread(self.consume)
        # reactor.suggestThreadPoolSize(20)
        reactor.run()

    def consume(self):
        """Start consuming packets
        """

        #tracker = SummaryTracker()

        connection = AprsISConnection(
            self.callsign, self.passcode, self.sourceHostname, self.sourcePort)
        connection.setFrequencyLimit(self.hardFrequencyLimit)
        connection.setSourceId(self.sourceId)

        def onPacketRead(line):
            if (not reactor.running):
                raise StopIteration('Stopped')

            timestamp = int(time.time())
            deferred = threads.deferToThread(self._parse, line, timestamp)
            deferred.addCallback(onParseComplete)
            deferred.addErrback(onParseError)

        def onParseComplete(packet):
            reactor.callFromThread(self._addPacket, packet)

        def onParseError(error):
            # Parse will more or less only cast exception if db connection is lost

            # Force restart of collector (we assume that server will be autostarted if stopped)
            if reactor.running:
                reactor.stop()
            raise error

        try:
            connection.connect()
            connection.filteredConsumer(onPacketRead, True, True)

            #tracker.print_diff()

        except (aprslib.ConnectionDrop) as exp:
            # Just reconnect...
            self.logger.warning('Lost connection')
            self.logger.warning(exp)
            self.consume()

        except Exception as e:
            self.logger.error(e)

            # Force restart of collector
            if reactor.running:
                reactor.stop()

    def _parse(self, line, timestamp):
        """Parse raw packet

        Args:
            line (string):     APRS raw packet string
            timestamp (int):   Receive time of packet

        Returns:
            Returns a Packet
        """
        try:
            self.delay = int(time.time())-timestamp
            if (self.delay > 60):
                self.logger.error(
                    'Collector has a delay on %s seconds, ignoring packets until solved', self.delay)
                return None
            elif (self.delay > 15):
                self.logger.warning(
                    'Collector has a delay on %s seconds', self.delay)

            packetDict = aprslib.parse(line)
            parser = AprsPacketParser(self.db, self.saveOgnStationsWithMissingIdentity)
            parser.setSourceId(self.sourceId)
            packet = parser.getPacket(packetDict, timestamp)

            if (packet.mapId == 15 or packet.mapId == 16):
                return None

            if (self.detectDuplicates):
                self._checkIfDuplicate(packet)

            return self._cleanPacket(packet)

        except (aprslib.ParseError, aprslib.UnknownFormat, TrackDirectParseError) as exp:
            return self._parseUnsupportedPacket(line, timestamp)
        except psycopg2.InterfaceError as e:
            # Connection to database is lost, better just exit
            raise e
        except (UnicodeDecodeError) as exp:
            # just forget about this packet
            pass
        except Exception as e:
            self.logger.error(e, exc_info=1)
        return None

    def _parseUnsupportedPacket(self, line, timestamp):
        """Try to parse raw packet that aprs-lib could not handle

        Args:
            line (string):     APRS raw packet string
            timestamp (int):   Receive time of packet

        Returns:
            Returns a Packet
        """
        try:
            line = line.decode('utf-8', 'ignore')
            packetDict = self.basicParse(line)
            parser = AprsPacketParser(self.db, self.saveOgnStationsWithMissingIdentity)
            parser.setSourceId(self.sourceId)
            packet = parser.getPacket(packetDict, timestamp, True)
            packet.markerId = 1

            if (packet.packetTypeId == 6): # Telemetry packet
                packet.packetTypeId = 10 # Has no position
            else:
                packet.mapId = 11 # Unsupported packet

            return packet
        except Exception as e:
            self.logger.debug(e)
            self.logger.debug(line)
        return None

    def _addPacket(self, packet):
        """Adds packet to database

        Args:
            packet (Packet):   The packet
        """
        if (packet is None):
            return

        # Soft frequency limit check
        if (self._isStationSendingToFast(packet)):
            if (not self.saveFastPackets):
                return

            packet.markerId = 1
            packet.mapId = 8

            # Reset all mapId related values
            packet.replacePacketId = None
            packet.abnormalPacketId = None
            packet.confirmPacketId = None
            packet.replacePacketTimestamp = None
            packet.abnormalPacketTimestamp = None
            packet.confirmPacketTimestamp = None

        if (packet.mapId == 6):
            # Packet received in wrong order
            if (not self.saveFastPackets):
                return

        if (not self._isPacketValidInCurrentBatch(packet)):
            self._insertBatch()

        if (self._shouldPacketBeAdded(packet)):
            self._addPacketToBatch(packet)

        if (self._isBatchFull()):
            self._insertBatch()

        if (self._isBatchOld()):
            self._insertBatch()

    def _isStationSendingToFast(self, packet):
        """Returns true if this packet has been sent to close to previous packet from the same station (we need to save previous packet first)

        Args:
            packet (Packet) :  The packet that may have been sent to fast

        Returns:
            Boolean
        """
        if (packet.mapId in [1, 5, 7, 9] and packet.isMoving == 1 and self.frequencyLimit is not None):
            frequencyLimitToApply = int(self.frequencyLimit)

            if (frequencyLimitToApply == 0):
                return False

            if (packet.ogn is not None and packet.ogn.ognTurnRate is not None):
                turnRate = abs(float(packet.ogn.ognTurnRate))
                if (turnRate > 0) :
                    frequencyLimitToApply = int(frequencyLimitToApply / (1+turnRate))

            if packet.markerPrevPacketTimestamp:
                if ((packet.timestamp - frequencyLimitToApply) < packet.markerPrevPacketTimestamp):
                    # This station is sending faster than config limit
                    return True

            if (packet.stationId in self.movingStationIdsWithVisiblePacket):
                # This station is sending way to fast (we havn't even added the previous packet to database yet)
                return True

            if (packet.markerId in self.movingMarkerIdsWithVisiblePacket):
                # The senders of this object is sending way to fast (we havn't even added the previous packet to database yet)
                return True
        return False

    def _isPacketValidInCurrentBatch(self, packet):
        """Returns true if this packet can be added to current batch

        Args:
            packet (Packet) :  The packet that e want to add to current batch

        Returns:
            Boolean
        """
        if (self.latestPacketTimestamp is not None):
            # If previous packet belongs to another date we can not add packet to current batch
            currentPacketDate = datetime.datetime.utcfromtimestamp(
                int(packet.timestamp)).strftime('%Y%m%d')
            latestPacketDate = datetime.datetime.utcfromtimestamp(
                self.latestPacketTimestamp).strftime('%Y%m%d')

            if (currentPacketDate != latestPacketDate and len(self.packets) > 0):
                return False

        if (packet.stationId in self.stationIdsWithVisiblePacket):
            # We only want to handle one packet per station per batch
            return False

        return True

    def _shouldPacketBeAdded(self, packet):
        """Returns true if this packet should be added to database

        Args:
            packet (Packet) :  The packet that we want to add to batch

        Returns:
            Boolean
        """
        if (packet.sourceId != 3 or packet.stationIdPath):
            # We only add pure duplicates to batch if they have a path, otherwise we are not interested
            return True
        return False

    def _isBatchFull(self):
        """Returns true if batch is considered full

        Returns:
            Boolean
        """
        # If we do insert when we have specified amount of packets (or if more than 5s has passed)
        if (int(len(self.packets)) > int(self.numbersInBatch)):
            return True
        elif (len(self.packets) > 0 and self.latestBatchInsertTimestamp < int(time.time()) - 5):
            return True
        return False

    def _isBatchOld(self):
        """Returns true if batch is considered old

        Returns:
            Boolean
        """
        if (self.latestPacketTimestamp is not None
                and self.firstPacketTimestamp is not None
                and self.latestPacketTimestamp - self.firstPacketTimestamp > 1):
            return True
        return False

    def _addPacketToBatch(self, packet):
        """Add instance of ParsedPacket to batch

        Args:
            packet (Packet):  Packet that we want to add to batch
        """
        self.latestPacketTimestamp = int(packet.timestamp)
        if (self.firstPacketTimestamp is None):
            self.firstPacketTimestamp = int(packet.timestamp)
        self.packets.append(packet)
        if (packet.mapId in [1, 5, 7, 9]):
            self.stationIdsWithVisiblePacket.append(packet.stationId)
            if (packet.isMoving == 1):
                self.movingStationIdsWithVisiblePacket.append(packet.stationId)
                self.movingMarkerIdsWithVisiblePacket.append(packet.markerId)

    def _insertBatch(self):
        """Perform insert on the current batch
        """
        if (len(self.packets) > 0):
            self.latestBatchInsertTimestamp = int(time.time())

            # Make sure packets is inserted in the order that they where received
            self.packets.reverse()

            # Do batch insert
            packetBatchInserter = PacketBatchInserter(
                self.db, self.dbNoAutoCommit)
            packetBatchInserter.insert(self.packets[:], self.sourceId)

            self._reset()

    def _reset(self):
        """Reset all collector variables
        """
        self.packets = []
        self.stationIdsWithVisiblePacket = []
        self.movingStationIdsWithVisiblePacket = []
        self.movingMarkerIdsWithVisiblePacket = []
        self.latestPacketTimestamp = None
        self.firstPacketTimestamp = None

    def _cleanPacket(self, packet):
        """Method used to clean a Packet from unused columns

        Args:
            packet (Packet): Object of class Packet

        Returns:
            Returns a packet (cleaned)
        """
        if (packet.mapId not in [1, 5, 7, 9]):
            # This packet will never be shown on map, remove information that won't be used (just to save some space in database)
            packet.markerId = None
            packet.markerCounter = None
            packet.packetTailTimestamp = None
            packet.positionTimestamp = None
            packet.posambiguity = None
            packet.symbol = None
            packet.symbolTable = None
            packet.mapSector = None
            packet.relatedMapSectors = None
            packet.speed = None
            packet.course = None
            packet.altitude = None
            packet.isMoving = 1
        return packet

    def _checkIfDuplicate(self, packet):
        """Method used to check if this packet is a duplicate

        Note:
            If packet is a duplicate the object attribute mapId will be updated, and some related attributes.

        Args:
            packet (Packet): Object of class Packet
        """
        packetDuplicatePolicy = PacketDuplicatePolicy(self.stationRepository)
        if (packetDuplicatePolicy.isDuplicate(packet)):
            # It is a duplicate (or at least we treat it as one just to be safe)
            packet.mapId = 3
            packet.markerId = 1
            packet.replacePacketId = None  # No older packet should be replaced!!!
            packet.replacePacketTimestamp = None
            packet.abnormalPacketId = None  # Do not mark previous as abnormal yet
            packet.abnormalPacketTimestamp = None
            packet.confirmPacketId = None  # Do not confirm previous position
            packet.confirmPacketTimestamp = None

    def basicParse(self, line):
        """Performes a basic packet parse and returnes result as a dict

        Args:
            line (string):  Packet raw string

        Returns:
            Returns packet dict
        """
        # Divide into body and head
        try:
            (head, body) = line.split(':', 1)
        except:
            raise TrackDirectParseError("no body", {})

        if len(body) == 0:
            raise TrackDirectParseError("body is empty", {})

        packetType = body[0]
        body = body[1:]

        # Find sender, destination and path in header
        try:
            (fromcall, path) = head.split('>', 1)
        except:
            raise TrackDirectParseError("no header", {})

        if (not 1 <= len(fromcall) <= 9):
            raise TrackDirectParseError("fromcallsign has invalid length", {})

        path = path.split(',')
        tocall = path[0]

        if len(tocall) == 0:
            tocall = None

        path = path[1:]

        for station in path:
            if not re.findall(r"^[A-Z0-9\-]{1,9}\*?$", station, re.I):
                path = None
                break

        objectName = ''
        if packetType == ';':
            match = re.findall(r"^([ -~]{9})(\*|_)", body)
            if match:
                name, flag = match[0]
                objectName = name
                body = body[10:]

        if packetType == ')':
            match = re.findall(r"^([ -~!]{3,9})(\!|_)", body)
            if match:
                name, flag = match[0]
                objectName = name
                body = body[len(name)+1:]

        comment = None
        telemetry = None
        if packetType == 'T':
            telemetry = {}
            lst = body.split(',')
            if len(lst) >= 7 :
                seq = body.split(',')[0]
                vals = body.split(',')[1:6]
                bits = body.split(',')[6][:8]
                comment = body.split(',')[6][8:]

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
            'object_name': objectName,
            'packet_type': packetType,
            'telemetry': telemetry,
            'comment': comment
        }
        return packet
