import logging

from twisted.internet import threads, reactor, task
from twisted.internet.error import AlreadyCancelled, AlreadyCalled

from autobahn.twisted.websocket import WebSocketServerProtocol

import json
import time
import psycopg2
import psycopg2.extras
import os
import trackdirect
from trackdirect.database.DatabaseConnection import DatabaseConnection

from trackdirect.websocket.WebsocketResponseCreator import WebsocketResponseCreator
from trackdirect.websocket.WebsocketConnectionState import WebsocketConnectionState

from trackdirect.websocket.aprsis.AprsISReader import AprsISReader
from trackdirect.websocket.aprsis.AprsISPayloadCreator import AprsISPayloadCreator


class TrackDirectWebsocketServer(WebSocketServerProtocol):
    """The TrackDirectWebsocketServer class handles the incoming requests
    """

    def __init__(self):
        """The __init__ method.
        """
        WebSocketServerProtocol.__init__(self)
        self.logger = logging.getLogger('trackdirect')

        self.config = trackdirect.TrackDirectConfig()
        self.maxClientIdleTime = int(self.config.maxClientIdleTime) * 60
        self.maxQueuedRealtimePackets = int(
            self.config.maxQueuedRealtimePackets)

        dbConnection = DatabaseConnection()
        db = dbConnection.getConnection(True)

        self.connectionState = WebsocketConnectionState()
        self.responseCreator = WebsocketResponseCreator(
            self.connectionState, db)
        self.aprsISReader = AprsISReader(self.connectionState, db)
        self.aprsISPayloadCreator = AprsISPayloadCreator(
            self.connectionState, db)

        self.numberOfRealTimePacketThreads = 0
        self.timestampSenderCall = None
        self.realTimeListenerCall = None
        self.onInactiveCall = None
        self.isUnknownClient = False

    def onConnect(self, request):
        """Method that is executed on connect

        Args:
            request (object):  The connection request
        """
        try:
            if ('x-forwarded-for' in request.headers):
                self.logger.warning("Client connecting from origin: {0}, x-forwarded-for: {1} (server pid {2})".format(
                    request.origin, request.headers['x-forwarded-for'], str(os.getpid())))
            else:
                self.logger.warning(
                    "Client connecting from origin: {0} (server pid {1})".format(request.origin, str(os.getpid())))

        except Exception as e:
            self.logger.error(e, exc_info=1)
            raise e

    def onOpen(self):
        """Method that is executed on open
        """
        try:
            self.logger.info("WebSocket connection open.")

            self._sendResponseByType(42)  # Inform client that we are active
            self._startTimestampSender()
            self._reScheduleInactiveEvent()
        except Exception as e:
            self.logger.error(e, exc_info=1)

    def onMessage(self, payload, isBinary):
        """Method that is executed on incoming message

        Args:
            request (object):   The connection request
            isBinary (boolean): True if binary otherwise false
        """
        try:
            request = json.loads(payload)
            if (self.isUnknownClient):
                self.logger.warning(
                    "Incoming message from unknown client: {0}".format(str(request)))

            if ("payload_request_type" not in request):
                self.logger.warning(
                    "Incoming request has no type (%s)" % (exp))
                self.logger.warning(payload)
                return
            self._onRequest(request)
        except (ValueError) as exp:
            self.logger.warning(
                "Incoming request could not be parsed (%s)" % (exp))
            self.logger.warning(payload)
        except psycopg2.InterfaceError as e:
            # Connection to database is lost, better just terminate connection to make user reconnect with new db connection
            self.logger.error(e, exc_info=1)
            raise e
        except Exception as e:
            # Log error to make us aware of unknow problem
            self.logger.error(e, exc_info=1)

    def onClose(self, wasClean, code, reason):
        """Method that is executed on close

        Args:
            wasClean (boolean):  True if clean close otherwise false
            code (int):          Close code
            reason (object):     Reason for close
        """
        try:
            self.logger.info("WebSocket connection closed: {0}".format(reason))
            self.connectionState.disconnected = True
            self._stopTimestampSender()
            self._stopRealTimeListener(True)
        except Exception as e:
            # Log error to make us aware of unknow problem
            self.logger.error(e, exc_info=1)

    def _onRequest(self, request, requestId=None):
        """Method that is executed on incoming request

        Args:
            request (object):   The connection request
            requestId (int):    Id of the request
        """
        if (request["payload_request_type"] != 11):
            self._reScheduleInactiveEvent()

        if (request["payload_request_type"] in [5, 7, 9]):
            # Request that not affects the current map status (to much)
            deferred = threads.deferToThread(
                self._processRequest, request, None)
            deferred.addErrback(self._onError)

        else:
            # Request that affects map and current state
            if (requestId is None):
                requestId = self.connectionState.latestRequestId + 1
                self.connectionState.latestRequestType = request["payload_request_type"]
                self.connectionState.latestRequestId = requestId
                self.connectionState.latestRequestTimestamp = int(time.time())
                self._stopRealTimeListener(False)

            if (self.connectionState.latestHandledRequestId < requestId - 1):
                reactor.callLater(0.1, self._onRequest, request, requestId)
            else:
                self._updateState(request)

                deferred = threads.deferToThread(
                    self._processRequest, request, requestId)
                deferred.addErrback(self._onError)
                deferred.addCallback(self._onRequestDone)

    def _processRequest(self, request, requestId):
        """Method that sends a response to websocket client based on request

        Args:
            request (Dict):   Request from websocket client
            requestId (int):   Request id of processed request
        """
        try:
            for response in self.responseCreator.getResponses(request, requestId):
                if self.connectionState.disconnected:
                    break
                reactor.callFromThread(self._sendDictResponse, response)
            return requestId
        except psycopg2.InterfaceError as e:
            # Connection to database is lost, better just terminate connection to make user reconnect with new db connection
            self.logger.error(e, exc_info=1)
            raise e
        except Exception as e:
            # Log error to make us aware of unknow problem
            self.logger.error(e, exc_info=1)

    def _onRequestDone(self, requestId):
        """Method that is executed when request is processed

        Args:
            requestId (int):   Request id of processed request
        """
        try:
            if (self.connectionState.latestHandledRequestId < requestId):
                self.connectionState.latestHandledRequestId = requestId
            if (self.connectionState.latestRequestId == requestId):
                # We have no newer requests
                # Tell client response is complete
                self._sendResponseByType(35)

                if (self.connectionState.latestTimeTravelRequest is None
                        and self.connectionState.noRealTime is False
                        and self.connectionState.isValidLatestPosition()):
                    self._startRealTimeListener(requestId)

                elif ((int(time.time()) - self.connectionState.latestRequestTimestamp) <= self.maxClientIdleTime):
                    self._sendResponseByType(33)  # Tell client we are idle
        except psycopg2.InterfaceError as e:
            # Connection to database is lost, better just terminate connection to make user reconnect with new db connection
            raise e
        except Exception as e:
            # Log error to make us aware of unknow problem
            self.logger.error(e, exc_info=1)

    def _onError(self, error):
        """Method that is executed when a deferToThread failed

        Args:
            error (Exception):   The Exception
        """
        # Exception should only end up here if db connection is lost
        # Force restart of wsserver
        if reactor.running:
            reactor.stop()
        raise error

    def _startRealTimeListener(self, relatedRequestId):
        """Start real time APRS-IS listener, onRealTimePacketFound will be executed when a packet is received

        Args:
            relatedRequestId (int):   Request id of related request
        """
        def readRealTimePacket():
            if (self.connectionState.latestRequestId == relatedRequestId and not self.connectionState.disconnected):
                self.aprsISReader.read(onRealTimePacketFound)

        def onRealTimePacketComplete():
            self.numberOfRealTimePacketThreads -= 1
            if (self.numberOfRealTimePacketThreads <= 0):
                # If we have no packets on the way we should see if we have another waiting
                readRealTimePacket()

        def onRealTimePacketFound(raw, sourceId):
            if (raw is None and sourceId is None):
                # Something went wrong, stop everything
                self._onInactive()
            else:
                if (self.numberOfRealTimePacketThreads > self.maxQueuedRealtimePackets):
                    # To many packets, several previous LoopingCall's is not done yet.
                    # We need to discard some packets, otherwise server will be overloaded and we will only send old packets.
                    # Client is required to request total update now and then, so the discarded packets should be send to client later.

                    counter = self.aprsISReader.clear(5)
                    #self.logger.warning('Discarding ' + str(counter) + ' packets')
                else:
                    self.numberOfRealTimePacketThreads += 1
                    deferred = threads.deferToThread(
                        self._processRealTimePacket, raw, sourceId)
                    deferred.addCallback(lambda _: onRealTimePacketComplete())
                    deferred.addErrback(self._onError)

        # Tell client we are connecting to real time feed
        self._sendResponseByType(34)
        self.aprsISReader.start()  # Will start if needed and change filter if needed
        # Tell client we are listening on real time feed
        self._sendResponseByType(31)

        self.realTimeListenerCall = task.LoopingCall(readRealTimePacket)
        self.realTimeListenerCall.start(0.2)

    def _stopRealTimeListener(self, disconnect=False):
        """Stop real time APRS-IS listener, onRealTimePacketFound will be executed when a packet is received

        Args:
            disconnect (Boolean):   Set to true to also disconnect from APRS-IS servers
        """
        if (self.realTimeListenerCall is not None):
            try:
                self.realTimeListenerCall.stop()
            except (AlreadyCalled, AssertionError) as e:
                pass

            if (disconnect):
                self.aprsISReader.stop()
            else:
                self.aprsISReader.pause()

    def _processRealTimePacket(self, raw, sourceId):
        """Method that is executed when we have a new real time packet to send

        Args:
            raw (string):    Raw packet from APRS-IS
            sourceId (int):  The id of the source (1 for APRS and 2 for CWOP ...)
        """
        try:
            for response in self.aprsISPayloadCreator.getPayloads(raw, sourceId):
                reactor.callFromThread(self._sendDictResponse, response)
        except psycopg2.InterfaceError as e:
            # Connection to database is lost, better just terminate connection to make user reconnect with new db connection
            self.logger.error(e, exc_info=1)
            raise e
        except Exception as e:
            # Log error to make us aware of unknow problem
            self.logger.error(e, exc_info=1)

    def _startTimestampSender(self):
        """Method schedules call to _sendTimestampResponse to keep connection up
        """
        self.timestampSenderCall = task.LoopingCall(
            self._sendTimestampResponse)
        self.timestampSenderCall.start(1.0)

    def _stopTimestampSender(self):
        """Stop looping call to _sendTimestampResponse
        """
        if (self.timestampSenderCall is not None):
            try:
                self.timestampSenderCall.stop()
            except AssertionError as e:
                pass

    def _reScheduleInactiveEvent(self):
        """Method schedules call to _onInactive when client has been idle too long

        Note:
            When _reScheduleInactiveEvent is called any previous schedules will be cancelled and countdown will be reset
        """
        if (self.onInactiveCall is not None):
            try:
                self.onInactiveCall.cancel()
            except (AlreadyCalled, AlreadyCancelled) as e:
                pass
        self.onInactiveCall = reactor.callLater(
            self.maxClientIdleTime, self._onInactive)

    def _onInactive(self):
        """Method that is executed when client has been inactive too long
        """
        try:
            # Client is inactive, pause (to save bandwidth, cpu and memory)
            self._sendResponseByType(36)
            self._stopTimestampSender()
            self._stopRealTimeListener(True)
            self.connectionState.totalReset()
        except psycopg2.InterfaceError as e:
            # Connection to database is lost, better just terminate connection to make user reconnect with new db connection
            self.logger.error(e, exc_info=1)
            raise e
        except Exception as e:
            # Log error to make us aware of unknow problem
            self.logger.error(e, exc_info=1)

    def _sendTimestampResponse(self):
        """Send server timestamp to syncronize server and client

        Notes:
            This is also used to tell the client that we are still here
            Most browser will disconnect if they do not hear anything in 300sec
        """
        try:
            if (self.connectionState.latestHandledRequestId < self.connectionState.latestRequestId):
                # server is busy with request, no point in doing this now
                return
            data = {}
            data["timestamp"] = int(time.time())
            self._sendResponseByType(41, data)
        except psycopg2.InterfaceError as e:
            # Connection to database is lost, better just terminate connection to make user reconnect with new db connection
            self.logger.error(e, exc_info=1)
            raise e
        except Exception as e:
            # Log error to make us aware of unknow problem
            self.logger.error(e, exc_info=1)

    def _sendResponseByType(self, payloadResponseType, data=None):
        """Send specified response to client

        Args:
            payloadResponseType (int):  A number that specifies what type of response we are sending
            data (dict):                The response data as a dict
        """
        if (data is not None):
            payload = {
                'payload_response_type': payloadResponseType, 'data': data}
        else:
            payload = {'payload_response_type': payloadResponseType}
        self._sendDictResponse(payload)

    def _sendDictResponse(self, payload):
        """Send message dict payload to client

        Args:
            payload (Dict):  Response payload
        """
        try:
            jsonPayload = json.dumps(payload, ensure_ascii=True).encode('utf8')
            if (jsonPayload is not None):
                self.sendMessage(jsonPayload)
        except psycopg2.InterfaceError as e:
            # Connection to database is lost, better just terminate connection to make user reconnect with new db connection
            self.logger.error(e, exc_info=1)
            raise e
        except Exception as e:
            # Log error to make us aware of unknow problem
            self.logger.warning(e, exc_info=1)

    def _updateState(self, request):
        """Update the connection state based on request

        Args:
            request (Dict):    Request form client
        """
        if ("neLat" in request
                and "neLng" in request
                and "swLat" in request
                and "swLng" in request
                and "minutes" in request):
            self.connectionState.setLatestMapBounds(
                request["neLat"], request["neLng"], request["swLat"], request["swLng"])

        if ("onlyLatestPacket" in request):
            self.connectionState.setOnlyLatestPacketRequested(
                (request["onlyLatestPacket"] == 1))

        if ("minutes" in request):
            if ("time" in request):
                self.connectionState.setLatestMinutes(
                    request["minutes"], request["time"])
            else:
                self.connectionState.setLatestMinutes(request["minutes"], None)

        if ("noRealTime" in request):
            self.connectionState.disableRealTime()
