import datetime, time, calendar
from trackdirect.repositories.PacketRepository import PacketRepository
from trackdirect.websocket.queries.MissingPacketsQuery import MissingPacketsQuery


class MostRecentPacketsQuery() :
    """This query class returnes the latest packet for moving stations and the latest packet for every uniqe position for stationary stations.

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
        self.simulateEmptyStation = False


    def enableSimulateEmptyStation(self) :
        """Enable simulation even if we have no packet from station at all
        """
        self.simulateEmptyStation = True


    def getPackets(self, stationIds) :
        """Fetch the most recent packets for the specified stations.
        Returns the latest packet for moving stations and the latest packet for every uniqe position for stationary stations.

        Args:
            stationIds (array):   An array of all stations we want packets for

        Returns:
            array
        """
        if (self.state.latestTimeTravelRequest is not None) :
            timestamp = int(self.state.latestTimeTravelRequest) - (int(self.state.latestMinutesRequest)*60)
            packets = self.packetRepository.getMostRecentConfirmedObjectListByStationIdListAndTimeInterval(stationIds, timestamp, self.state.latestTimeTravelRequest)
        else :
            timestamp = int(time.time()) - (int(self.state.latestMinutesRequest)*60)
            packets = self.packetRepository.getMostRecentConfirmedObjectListByStationIdList(stationIds, timestamp)

        if (len(packets) < len(stationIds)) :
            # If we have no recent markers we just send the latest that we have
            query = MissingPacketsQuery(self.state, self.db)
            if (self.simulateEmptyStation) :
                query.enableSimulateEmptyStation()

            foundMissingPackets = query.getMissingPackets(stationIds, packets)
            if (foundMissingPackets) :
                foundMissingPackets.extend(packets)
                packets = foundMissingPackets
        return packets
