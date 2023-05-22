import logging
from twisted.python import log

from math import floor, ceil
import datetime, time
import psycopg2, psycopg2.extras

from trackdirect.repositories.PacketRepository import PacketRepository

from trackdirect.websocket.queries.MissingPacketsQuery import MissingPacketsQuery
from trackdirect.websocket.responses.ResponseDataConverter import ResponseDataConverter

class FilterHistoryResponseCreator():
    """The FilterHistoryResponseCreator class creates history responses for stations that we are filtering on
    """


    def __init__(self, state, db):
        """The __init__ method.

        Args:
            state (WebsocketConnectionState):    WebsocketConnectionState instance that contains current state
            db (psycopg2.Connection):            Database connection (with autocommit)
        """
        self.state = state
        self.logger = logging.getLogger('trackdirect')

        self.db = db
        self.responseDataConverter = ResponseDataConverter(state, db)
        self.packetRepository = PacketRepository(db)


    def getResponse(self) :
        """Returns a filter history response

        Returns:
            Dict
        """
        filterStationIds = self.state.filterStationIdDict.keys()

        # When filtering we send everything in the same packet
        # We need to do this since we do not send related objects,
        # if user is filtering on two related OBJECTS they need to be sent together
        packets = self._getPackets(filterStationIds)

        # If map is empty we need to make sure that all specified stations is included
        if (self.state.isMapEmpty()) :
            query = MissingPacketsQuery(self.state, self.db)
            query.enableSimulateEmptyStation()
            sortedFoundMissingPackets = query.getMissingPackets(filterStationIds, packets)
            sortedFoundMissingPackets.extend(packets)
            packets = sortedFoundMissingPackets

        if (packets) :
            data = self.responseDataConverter.getResponseData(packets, [])
            payload = {'payload_response_type': 2, 'data': data}
            return payload


    def _getPackets(self, stationIds) :
        """Returns packets to be used in a filter history response

        Args:
            stationIds (array):    The station id's that we want history data for

        Returns:
            array
        """
        minTimestamp = None
        if (len(stationIds) > 0) :
            minTimestamp = self.state.getStationLatestTimestampOnMap(list(stationIds)[0])
        if (minTimestamp is None) :
            minTimestamp = self.state.getMapSectorTimestamp(None) # None as argument is useful even when not dealing with map-sectors
        if (len(stationIds) > 1) :
            for stationId in stationIds :
                timestamp = self.state.getStationLatestTimestampOnMap(stationId)
                if (timestamp is not None and timestamp > minTimestamp) :
                    minTimestamp = timestamp

        if (self.state.latestTimeTravelRequest is not None) :
            if (not self.state.isStationsOnMap(stationIds)) :
                return self.packetRepository.getObjectListByStationIdListAndTimeInterval(stationIds, minTimestamp, self.state.latestTimeTravelRequest)
        else :
            return self.packetRepository.getObjectListByStationIdList(stationIds, minTimestamp)
