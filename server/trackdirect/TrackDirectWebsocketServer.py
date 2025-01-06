import logging
from twisted.internet import threads, reactor, task
from twisted.internet.error import AlreadyCancelled, AlreadyCalled
from autobahn.twisted.websocket import WebSocketServerProtocol
import json
import time
import psycopg2
import psycopg2.extras
import os
from server.trackdirect.TrackDirectConfig import TrackDirectConfig
from server.trackdirect.database.DatabaseConnection import DatabaseConnection
from server.trackdirect.websocket.WebsocketResponseCreator import WebsocketResponseCreator
from server.trackdirect.websocket.WebsocketConnectionState import WebsocketConnectionState
from server.trackdirect.websocket.aprsis.AprsISReader import AprsISReader
from server.trackdirect.websocket.aprsis.AprsISPayloadCreator import AprsISPayloadCreator


class TrackDirectWebsocketServer(WebSocketServerProtocol):
    """The TrackDirectWebsocketServer class handles the incoming requests."""

    def __init__(self):
        """Initialize the TrackDirectWebsocketServer."""
        super().__init__()

        self.logger = logging.getLogger('trackdirect')

        self.max_queued_realtime_packets = None
        self.max_client_idle_time = None

        db_connection = DatabaseConnection()
        db = db_connection.get_connection(True)

        self.connection_state = WebsocketConnectionState()
        self.response_creator = WebsocketResponseCreator(self.connection_state, db)
        self.aprs_is_reader = AprsISReader(self.connection_state, db)
        self.aprs_is_payload_creator = AprsISPayloadCreator(self.connection_state, db)

        self.number_of_real_time_packet_threads = 0
        self.timestamp_sender_call = None
        self.real_time_listener_call = None
        self.on_inactive_call = None
        self.is_unknown_client = False

    def onConnect(self, request):
        """Executed on connect."""
        try:
            config = TrackDirectConfig()
            config.populate(self.factory.config_file)

            self.max_client_idle_time = int(config.max_client_idle_time) * 60
            self.max_queued_realtime_packets = int(config.max_queued_realtime_packets)

            if 'x-forwarded-for' in request.headers:
                self.logger.warning(
                    f"Client connecting from origin: {request.origin}, x-forwarded-for: {request.headers['x-forwarded-for']} (server pid {os.getpid()})"
                )
            else:
                self.logger.warning(
                    f"Client connecting from origin: {request.origin} (server pid {os.getpid()})"
                )
        except Exception as e:
            self.logger.error(e, exc_info=True)
            raise

    def onOpen(self):
        """Executed on open."""
        try:
            self.logger.info("WebSocket connection open.")
            self._send_response_by_type(42)  # Inform client that we are active
            self._start_timestamp_sender()
            self._re_schedule_inactive_event()
        except Exception as e:
            self.logger.error(e, exc_info=True)

    def onMessage(self, payload, is_binary):
        """Executed on incoming message."""
        try:
            request = json.loads(payload)
            if self.is_unknown_client:
                self.logger.warning(f"Incoming message from unknown client: {request}")

            if "payload_request_type" not in request:
                self.logger.warning("Incoming request has no type")
                self.logger.warning(payload)
                return
            self._on_request(request)
        except ValueError as exp:
            self.logger.warning(f"Incoming request could not be parsed ({exp})")
            self.logger.warning(payload)
        except psycopg2.InterfaceError as e:
            self.logger.error(e, exc_info=True)
            raise
        except Exception as e:
            self.logger.error(e, exc_info=True)

    def onClose(self, was_clean, code, reason):
        """Executed on close."""
        try:
            self.logger.info(f"WebSocket connection closed: {reason}")
            self.connection_state.disconnected = True
            self._stop_timestamp_sender()
            self._stop_real_time_listener(True)
        except Exception as e:
            self.logger.error(e, exc_info=True)

    def _on_request(self, request, request_id=None):
        """Executed on incoming request."""
        if request["payload_request_type"] != 11:
            self._re_schedule_inactive_event()

        if request["payload_request_type"] in [5, 7, 9]:
            deferred = threads.deferToThread(self._process_request, request, None)
            deferred.addErrback(self._on_error)
        else:
            if request_id is None:
                request_id = self.connection_state.latest_requestId + 1
                self.connection_state.latest_request_type = request["payload_request_type"]
                self.connection_state.latest_requestId = request_id
                self.connection_state.latest_request_timestamp = int(time.time())
                self._stop_real_time_listener(False)

            if self.connection_state.latest_handled_request_id < request_id - 1:
                reactor.callLater(0.1, self._on_request, request, request_id)
            else:
                self._update_state(request)
                deferred = threads.deferToThread(self._process_request, request, request_id)
                deferred.addErrback(self._on_error)
                deferred.addCallback(self._on_request_done)

    def _process_request(self, request, request_id):
        """Send a response to websocket client based on request."""
        try:
            for response in self.response_creator.get_responses(request, request_id):
                if self.connection_state.disconnected:
                    break
                reactor.callFromThread(self._send_dict_response, response)
            return request_id
        except psycopg2.InterfaceError as e:
            self.logger.error(e, exc_info=True)
            raise
        except Exception as e:
            self.logger.error(e, exc_info=True)

    def _on_request_done(self, request_id):
        """Executed when request is processed."""
        try:
            if self.connection_state.latest_handled_request_id < request_id:
                self.connection_state.latest_handled_request_id = request_id
            if self.connection_state.latest_requestId == request_id:
                self._send_response_by_type(35)

                if (self.connection_state.latest_time_travel_request is None
                        and not self.connection_state.no_real_time
                        and self.connection_state.is_valid_latest_position()):
                    self._start_real_time_listener(request_id)
                elif (int(time.time()) - self.connection_state.latest_request_timestamp) <= self.max_client_idle_time:
                    self._send_response_by_type(33)
        except psycopg2.InterfaceError as e:
            raise
        except Exception as e:
            self.logger.error(e, exc_info=True)

    def _on_error(self, error):
        """Executed when a deferToThread failed."""
        if reactor.running:
            reactor.stop()
        raise error

    def _start_real_time_listener(self, related_request_id):
        """Start real time APRS-IS listener."""
        def read_real_time_packet():
            if (self.connection_state.latest_requestId == related_request_id
                    and not self.connection_state.disconnected):
                self.aprs_is_reader.read(on_real_time_packet_found)

        def on_real_time_packet_complete():
            self.number_of_real_time_packet_threads -= 1
            if self.number_of_real_time_packet_threads <= 0:
                read_real_time_packet()

        def on_real_time_packet_found(raw, source_id):
            if raw is None and source_id is None:
                self._on_inactive()
            else:
                if self.number_of_real_time_packet_threads > self.max_queued_realtime_packets:
                    self.aprs_is_reader.clear(5)
                else:
                    self.number_of_real_time_packet_threads += 1
                    deferred = threads.deferToThread(self._process_real_time_packet, raw, source_id)
                    deferred.addCallback(lambda _: on_real_time_packet_complete())
                    deferred.addErrback(self._on_error)

        self._send_response_by_type(34)
        self.aprs_is_reader.start()
        self._send_response_by_type(31)

        self.real_time_listener_call = task.LoopingCall(read_real_time_packet)
        self.real_time_listener_call.start(0.2, False)

    def _stop_real_time_listener(self, disconnect=False):
        """Stop real time APRS-IS listener."""
        if self.real_time_listener_call is not None:
            try:
                self.real_time_listener_call.stop()
            except (AlreadyCalled, AssertionError):
                pass

            if disconnect:
                self.aprs_is_reader.stop()
            else:
                self.aprs_is_reader.pause()

    def _process_real_time_packet(self, raw, source_id):
        """Executed when we have a new real time packet to send."""
        try:
            for response in self.aprs_is_payload_creator.get_payloads(raw, source_id):
                reactor.callFromThread(self._send_dict_response, response)
        except psycopg2.InterfaceError as e:
            self.logger.error(e, exc_info=True)
            raise
        except Exception as e:
            self.logger.error(e, exc_info=True)

    def _start_timestamp_sender(self):
        """Schedule call to _sendTimestampResponse to keep connection up."""
        self.timestamp_sender_call = task.LoopingCall(self._send_timestamp_response)
        self.timestamp_sender_call.start(1.0)

    def _stop_timestamp_sender(self):
        """Stop looping call to _sendTimestampResponse."""
        if self.timestamp_sender_call is not None:
            try:
                self.timestamp_sender_call.stop()
            except AssertionError:
                pass

    def _re_schedule_inactive_event(self):
        """Schedule call to _onInactive when client has been idle too long."""
        if self.on_inactive_call is not None:
            try:
                self.on_inactive_call.cancel()
            except (AlreadyCalled, AlreadyCancelled):
                pass
        self.on_inactive_call = reactor.callLater(self.max_client_idle_time, self._on_inactive)

    def _on_inactive(self):
        """Executed when client has been inactive too long."""
        try:
            self._send_response_by_type(36)
            self._stop_timestamp_sender()
            self._stop_real_time_listener(True)
            self.connection_state.total_reset()
        except psycopg2.InterfaceError as e:
            self.logger.error(e, exc_info=True)
            raise
        except Exception as e:
            self.logger.warning('Exception in _on_inactive')
            self.logger.warning(e, exc_info=False)

    def _send_timestamp_response(self):
        """Send server timestamp to synchronize server and client."""
        try:
            if self.connection_state.latest_handled_request_id < self.connection_state.latest_requestId:
                return
            data = {"timestamp": int(time.time())}
            self._send_response_by_type(41, data)
        except psycopg2.InterfaceError as e:
            self.logger.error(e, exc_info=True)
            raise
        except Exception as e:
            self.logger.warning('Exception in _send_timestamp_response')
            self.logger.warning(e, exc_info=False)

    def _send_response_by_type(self, payload_response_type, data=None):
        """Send specified response to client."""
        payload = {'payload_response_type': payload_response_type}
        if data is not None:
            payload['data'] = data
        self._send_dict_response(payload)

    def _send_dict_response(self, payload):
        """Send message dict payload to client."""
        try:
            json_payload = json.dumps(payload, ensure_ascii=True).encode('utf8')
            if json_payload is not None:
                self.sendMessage(json_payload)
        except psycopg2.InterfaceError as e:
            self.logger.error(e, exc_info=True)
            raise
        except Exception as e:
            self.logger.warning('Exception in _send_dict_response')
            self.logger.warning(e, exc_info=False)

    def _update_state(self, request):
        """Update the connection state based on request."""
        if all(key in request for key in ["neLat", "neLng", "swLat", "swLng", "minutes"]):
            self.connection_state.set_latest_map_bounds(
                request["neLat"], request["neLng"], request["swLat"], request["swLng"]
            )

        if "onlyLatestPacket" in request:
            self.connection_state.set_only_latest_packet_requested(request["onlyLatestPacket"] == 1)

        if "minutes" in request:
            time = request.get("time")
            self.connection_state.set_latest_minutes(request["minutes"], time)

        if "noRealTime" in request:
            self.connection_state.disable_real_time()