import logging

import time


import trackdirect

from trackdirect.repositories.PacketRepository import PacketRepository
from trackdirect.repositories.StationRepository import StationRepository

from trackdirect.websocket.queries.MostRecentPacketsQuery import MostRecentPacketsQuery
from trackdirect.websocket.responses.ResponseDataConverter import ResponseDataConverter


class FilterResponseCreator():
    """The FilterResponseCreator is used to create filter responses, a response sent to client when client wants to filter on a station
    """


    def __init__(self, state, db):
        """The __init__ method.

        Args:
            state (WebsocketConnectionState):    WebsocketConnectionState instance that contains current state
            db (psycopg2.Connection):            Database connection (with autocommit)
        """
        self.state = state
        self.db = db
        self.logger = logging.getLogger('trackdirect')
        self.responseDataConverter = ResponseDataConverter(state, db)
        self.packetRepository = PacketRepository(db)
        self.stationRepository = StationRepository(db)
        self.config = trackdirect.TrackDirectConfig()


    def getResponses(self, request) :
        """Creates responses related to a filter request

        Args:
            request (dict):    The request to process

        Returns:
            generator
        """
        self._updateState(request)
        if (self.state.isReset()) :
            yield self._getResetResponse()
        yield self._getFilterResponse()


    def _updateState(self, request) :
        """Update connection state based on filter request

        Args:
            request (dict):    The request to process
        """
        if (request["payload_request_type"] == 4 and "list" in request) :
            if (len(request["list"]) > 0) :
                for stationId in request["list"]:
                    # Only send data about specified objects
                    self.state.filterStationIdDict[int(stationId)] = True
            else :
                # User wants to see everything again
                self.state.filterStationIdDict = {}
                self.state.setLatestMapBounds(0, 0, 0, 0)
                self.state.setLatestMinutes(60, None)
            self.state.reset()

        elif (request["payload_request_type"] == 6 and "station_id" in request) :
            self.state.filterStationIdDict.pop(int(request["station_id"]), None)
            self.state.reset()

        elif (request["payload_request_type"] == 8 and "namelist" in request) :
            if (len(request["namelist"]) > 0) :
                minTimestamp = int(time.time()) - (10*365*24*60*60)
                if (not self.config.allowTimeTravel) :
                    minTimestamp = int(time.time()) - (24*60*60)

                for stationName in request["namelist"]:
                    # Only send data about specified objects
                    stations = self.stationRepository.getObjectListByName(stationName, None, None, minTimestamp)
                    for station in stations:
                        self.state.filterStationIdDict[int(station.id)] = True
            else :
                # User wants to see everything again
                self.state.filterStationIdDict = {}
                self.state.setLatestMapBounds(0, 0, 0, 0)
                self.state.setLatestMinutes(60, None)
            self.state.reset()

    def _getResetResponse(self) :
        """This method creates a reset response

        Returns:
            Dict
        """
        payload =  {'payload_response_type': 40}
        return payload


    def _getFilterResponse(self) :
        """This method creates a filter response

        Returns:
            Dict
        """
        data = []
        if (self.state.filterStationIdDict) :
            filterStationIds = list(self.state.filterStationIdDict.keys())
            data = self._getFilterResponseData(filterStationIds)

        payload =  {'payload_response_type': 5, 'data': data}
        return payload


    def _getFilterResponseData(self, filterStationIds) :
        """Creates data to be included in a filter response

        Args:
            filterStationIds (array):   An array of all stations we should filter on
        """
        if (self.state.latestTimeTravelRequest is not None) :
            timestamp = int(self.state.latestTimeTravelRequest) - (int(self.state.latestMinutesRequest)*60)
        else :
            timestamp = int(time.time()) - (int(self.state.latestMinutesRequest)*60)

        query = MostRecentPacketsQuery(self.state, self.db)
        query.enableSimulateEmptyStation()
        packets = query.getPackets(filterStationIds)
        data = self.responseDataConverter.getResponseData(packets, [])
        self.state.reset() # Reset to make sure client will get the same packet on history request
        result = []
        for packetData in data :
            if (self.config.allowTimeTravel or packetData['timestamp'] > int(time.time()) - (24*60*60)) :
                packetData['overwrite'] = 1
                packetData['realtime'] = 0
                packetData['packet_order_id'] = 1 # Last packet for this station in this response
                packetData['requested_timestamp'] = timestamp
                if packetData['station_id'] in filterStationIds:
                    packetData['related'] = 0
                else :
                    packetData['related'] = 1
                result.append(packetData)
        return result
