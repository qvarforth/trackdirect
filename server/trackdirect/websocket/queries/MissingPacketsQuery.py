import datetime, time, calendar
from trackdirect.repositories.PacketRepository import PacketRepository
from trackdirect.repositories.StationRepository import StationRepository
from trackdirect.parser.policies.MapSectorPolicy import MapSectorPolicy

class MissingPacketsQuery() :
    """This query class is used to find a packet for all stations that we are missing a packet for (when we rely need a packet for them)

    Note:
        If no packet are found we will simulate them
    """

    def __init__(self, state, db) :
        """The __init__ method.

        Args:
            state (WebsocketConnectionState):   The current state for a websocket connection
            db (psycopg2.Connection):           Database connection
        """
        self.state = state
        self.db = db
        self.packetRepository = PacketRepository(db)
        self.stationRepository = StationRepository(db)
        self.simulateEmptyStation = False


    def enableSimulateEmptyStation(self) :
        """Enable simulation even if we have no packet from station at all
        """
        self.simulateEmptyStation = True


    def getMissingPackets(self, stationIds, foundPackets) :
        """Fetch latest packets for stations that has no packet in foundPackets

        Args:
            stationIds (array):   An array of all stations we should filter on
            foundPackets (array): Packets that we have found

        Returns:
            array
        """
        foundMissingPackets = []
        for stationId in stationIds :
            foundStationPacket = False
            for packet in foundPackets :
                if packet.stationId == stationId :
                    foundStationPacket = True
                    break # will go to next stationId

            # Get latest packet for this station
            if (not foundStationPacket) :
                missingPacket = self._getLatestPacket(stationId)
                if (missingPacket is not None) :
                    foundMissingPackets.append(missingPacket)

        def getSortKey(item) :
            return item.timestamp
        return sorted(foundMissingPackets, key = getSortKey)


    def _getLatestPacket(self, stationId) :
        """This method tries to find a packet for the specified station, in worst case a packet will be simulated based on old data

        Args:
            stationId (int): Stations id that we need a packet for

        Returns:
            Packet
        """
        if (self.state.latestTimeTravelRequest is not None) :
            ts = int(self.state.latestTimeTravelRequest) - (30*24*60*60) # For time travelers we need a limit
            olderPackets = self.packetRepository.getLatestObjectListByStationIdListAndTimeInterval([stationId], ts, self.state.latestTimeTravelRequest)
        else :
            olderPackets = self.packetRepository.getLatestConfirmedObjectListByStationIdList([stationId], 0)

        if (len(olderPackets) > 0) :
            return olderPackets[0] # The lastet is the first in array
        else :
            # Lets try not confirmed packets
            if (self.state.latestTimeTravelRequest is not None) :
                ts = int(self.state.latestTimeTravelRequest) - (30*24*60*60) # For time travelers we need a limit
                olderNonConfirmedPackets = self.packetRepository.getLatestObjectListByStationIdListAndTimeInterval([stationId], ts, self.state.latestTimeTravelRequest, False)
            else :
                olderNonConfirmedPackets = self.packetRepository.getLatestObjectListByStationIdList([stationId], 0)

            if (len(olderNonConfirmedPackets) > 0) :
                # Make this ghost-packet visible...
                packet = olderNonConfirmedPackets[0]
                packet.mapId = 1
                packet.sourceId = 0 #simulated
                return packet
            else :
                # We still do not have packets for this station, just get what we have from the station-table
                return self._getSimulatedPacket(stationId)
        return None


    def _getSimulatedPacket(self, stationId) :
        """Creates a simulated packet based on data saved in the station table

        Args:
            stationId (int):                  The station that we want a packet from

        Returns:
            Packet
        """
        station = self.stationRepository.getObjectById(stationId)
        if (station.isExistingObject()
                and (station.latestConfirmedPacketId is not None
                        or self.simulateEmptyStation)) :
            packet = self.packetRepository.create()
            packet.stationId = station.id
            packet.senderId = station.latestSenderId
            packet.sourceId = station.sourceId
            packet.ogn_sender_address = station.latestOgnSenderAddress

            if (station.latestConfirmedPacketId is not None) :
                packet.id = station.latestConfirmedPacketId
            else :
                packet.id = -station.id # simulate a packet id that is uniqe

            if (station.latestConfirmedMarkerId is not None) :
                packet.markerId = station.latestConfirmedMarkerId
            else :
                packet.markerId = -station.id # simulate a marker id

            packet.isMoving = 0
            packet.packetTypeId = 1 # Assume it was a position packet...

            if (station.latestConfirmedLatitude is not None and station.latestConfirmedLongitude is not None) :
                packet.latitude = station.latestConfirmedLatitude
                packet.longitude = station.latestConfirmedLongitude
            else :
                packet.latitude = float(0.0)
                packet.longitude = float(0.0)

            if (self.state.latestTimeTravelRequest is not None) :
                packet.timestamp = 0 # don't know anything better to set here...
            elif (station.latestConfirmedPacketTimestamp is not None) :
                packet.timestamp = station.latestConfirmedPacketTimestamp
            else :
                packet.timestamp = 0

            packet.reportedTimestamp = None
            packet.positionTimestamp = packet.timestamp
            packet.posambiguity = 0

            if (station.latestConfirmedSymbol is not None and station.latestConfirmedSymbolTable is not None) :
                packet.symbol = station.latestConfirmedSymbol
                packet.symbolTable = station.latestConfirmedSymbolTable
            else :
                packet.symbol = None
                packet.symbolTable = None

            mapSectorPolicy = MapSectorPolicy()
            packet.mapSector = mapSectorPolicy.getMapSector(packet.latitude, packet.longitude)
            packet.relatedMapSectors = []
            packet.mapId = 1
            packet.speed = None
            packet.course = None
            packet.altitude = None
            packet.packetTailTimestamp = packet.timestamp
            packet.comment = None
            packet.rawPath = None
            packet.raw = None

            return packet
        return None
