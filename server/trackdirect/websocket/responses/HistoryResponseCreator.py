import logging
from twisted.python import log

from math import floor, ceil
import datetime, time
import psycopg2, psycopg2.extras

from trackdirect.repositories.PacketRepository import PacketRepository

from trackdirect.websocket.queries.StationIdByMapSectorQuery import StationIdByMapSectorQuery
from trackdirect.websocket.responses.ResponseDataConverter import ResponseDataConverter


class HistoryResponseCreator():
    """The HistoryResponseCreator class creates websocket history responses for the latest websocket request
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
        self.packetRepository = PacketRepository(db)
        self.responseDataConverter = ResponseDataConverter(state, db)


    def getResponses(self, request, requestId) :
        """Create all history responses for the current request

        Args:
            request (dict):    The request to process
            requestId (int):   Request id of processed request

        Returns:
            generator
        """
        if (request["payload_request_type"] == 1 or request["payload_request_type"] == 11) :
            if (not self.state.isValidLatestPosition()) :
                return

            if (self.state.latestNeLat >= 90
                    and self.state.latestNeLng >= 180
                    and self.state.latestSwLat <= -90
                    and self.state.latestSwLng <= -180) :
                # request is requesting to much
                return

            for response in self._getMapSectorHistoryResponses(requestId) :
                yield response

        elif (request["payload_request_type"] == 7 and "station_id" in request) :
            for response in self._getStationHistoryResponses([request["station_id"]], None, True) :
                yield response

        else :
            self.logger.error('Request is not supported')
            self.logger.error(request)


    def _getMapSectorHistoryResponses(self, requestId) :
        """Creates all needed history responses for the currently visible map sectors

        Args:
            requestId (int):   Request id of processed request

        Returns:
            generator
        """
        mapSectorArray = self.state.getVisibleMapSectors()
        if (len(mapSectorArray) > 20000) :
            # Our client will never send a request like this
            self.logger.error("To many map sectors requested!")
            return

        handledStationIdDict = {}
        for mapSector in mapSectorArray :
            try:
                # Handle one map sector at the time
                if (requestId is not None and self.state.latestRequestId > requestId) :
                    # If new request is recived we want to skip this one (this request is not that important)
                    # As long as we handle a complete map sector everything is ok
                    return

                foundStationIds = self._getStationIdsByMapSector(mapSector)
                stationIds = []
                for stationId in foundStationIds :
                    if (stationId not in handledStationIdDict) :
                        stationIds.append(stationId)
                        handledStationIdDict[stationId] = True

                if (stationIds) :
                    for response in self._getStationHistoryResponses(stationIds, mapSector, False) :
                        yield response
            except psycopg2.InterfaceError as e:
                # Connection to database is lost, better just exit
                raise e
            except Exception as e:
                self.logger.error(e, exc_info=1)


    def _getStationHistoryResponses(self, stationIds, mapSector, includeCompleteHistory = False) :
        """Creates one history response per station

        Args:
            stationIds (array):                 An array of the stations that we want history data for
            mapSector (int):                    The map sector that we want history data for
            includeCompleteHistory (boolean):   Include all previous packets (even if we currently only request the latest packets)

        Returns:
            generator
        """
        # Important to fetch map sector timestamp before loop (may be updated in loop)
        minTimestamp = self.state.getMapSectorTimestamp(mapSector)
        for stationId in stationIds:
            try:
                if (self.state.latestTimeTravelRequest is not None) :
                    response = self._getPastHistoryResponse(stationId, mapSector, minTimestamp, includeCompleteHistory)
                else :
                    response = self._getRecentHistoryResponse(stationId, mapSector, minTimestamp, includeCompleteHistory)
                if (response is not None) :
                    yield response
            except psycopg2.InterfaceError as e:
                # Connection to database is lost, better just exit
                raise e
            except Exception as e:
                self.logger.error(e, exc_info=1)


    def _getRecentHistoryResponse(self, stationId, mapSector, minTimestamp, includeCompleteHistory = False) :
        """Creates a history response for the specified station, includes all packets from minTimestamp until now

        Args:
            stationId (int):                    The station id that we want history data for
            mapSector (int):                    The map sector that we want history data for
            minTimestamp (int):                 The map sector min timestamp to use in query
            includeCompleteHistory (boolean):   Include all previous packets (even if we currently only request the latest packets)

        Returns:
            Dict
        """
        packets = []
        onlyLatestPacketFetched = False
        currentStationIds = [stationId]

        currentMinTimestamp = self.state.getStationLatestTimestampOnMap(stationId)
        if (currentMinTimestamp is None) :
            currentMinTimestamp = minTimestamp
        else :
            # Since station already exists on map we should continue adding all packets
            includeCompleteHistory = True

        if (not self.state.onlyLatestPacketRequested or includeCompleteHistory) :
            packets = self.packetRepository.getObjectListByStationIdList(currentStationIds, currentMinTimestamp)
        else :
            # We could call getMostRecentConfirmedObjectListByStationIdList, would take longer time but would show all positions for a station
            packets = self.packetRepository.getLatestConfirmedObjectListByStationIdList(currentStationIds, currentMinTimestamp)
            if (packets) :
                packets = [packets[-1]] # we only need the latest
            onlyLatestPacketFetched = True

        if (packets) :
            flags = []
            if (onlyLatestPacketFetched) :
                flags = ["latest"]
            data = self.responseDataConverter.getResponseData(packets, [mapSector], flags)
            payload = {'payload_response_type': 2, 'data': data}
            return payload


    def _getPastHistoryResponse(self, stationId, mapSector, minTimestamp, includeCompleteHistory = False) :
        """Creates a history response for the specified station, includes all packets between minTimestamp and the current latestTimeTravelRequest timestamp

        Args:
            stationId (int):                    The station id that we want history data for
            mapSector (int):                    The map sector that we want history data for
            minTimestamp (int):                 The map sector min timestamp to use in query
            includeCompleteHistory (boolean):   Include all previous packets (even if we currently only request the latest packets)

        Returns:
            Dict
        """
        packets = []
        onlyLatestPacketFetched = False
        currentStationIds = [stationId]

        currentMinTimestamp = self.state.getStationLatestTimestampOnMap(stationId)
        if (currentMinTimestamp is None) :
            currentMinTimestamp = minTimestamp

        if (self.state.onlyLatestPacketRequested and not includeCompleteHistory) :
            if (stationId not in self.state.stationsOnMapDict) :
                # we only need to fetch latest packet for a time-travel request if station is not on map
                onlyLatestPacketFetched = True
                packets = self.packetRepository.getLatestObjectListByStationIdListAndTimeInterval(currentStationIds, currentMinTimestamp, self.state.latestTimeTravelRequest)
        else :
            if (not self.state.isStationHistoryOnMap(stationId)) :
                packets = self.packetRepository.getObjectListByStationIdListAndTimeInterval(currentStationIds, currentMinTimestamp, self.state.latestTimeTravelRequest)

        if (packets) :
            flags = []
            if (onlyLatestPacketFetched) :
                flags = ["latest"]
            data = self.responseDataConverter.getResponseData(packets, [mapSector], flags)
            payload = {'payload_response_type': 2, 'data': data}
            return payload


    def _getStationIdsByMapSector(self, mapSector) :
        """Returns the station Id's in specified map sector

        Args:
            mapSector (int):   The map sector that we are interested in

        Returns:
            array of ints
        """
        query = StationIdByMapSectorQuery(self.db)
        if (self.state.latestTimeTravelRequest is not None) :
            if (self.state.isMapSectorKnown(mapSector)) :
                # This map sector is under control
                return []
            else :
                startTimestamp = self.state.latestTimeTravelRequest - (int(self.state.latestMinutesRequest)*60)
                endTimestamp = self.state.latestTimeTravelRequest;
                return query.getStationIdListByMapSector(mapSector, startTimestamp, endTimestamp)
        else :
            timestamp = self.state.getMapSectorTimestamp(mapSector)
            return query.getStationIdListByMapSector(mapSector, timestamp, None)
