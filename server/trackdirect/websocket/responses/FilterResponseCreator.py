import logging
import time
from server.trackdirect.TrackDirectConfig import TrackDirectConfig
from server.trackdirect.repositories.PacketRepository import PacketRepository
from server.trackdirect.repositories.StationRepository import StationRepository
from server.trackdirect.websocket.queries.MostRecentPacketsQuery import MostRecentPacketsQuery
from server.trackdirect.websocket.responses.ResponseDataConverter import ResponseDataConverter


class FilterResponseCreator:
    """The FilterResponseCreator is used to create filter responses, a response sent to client when client wants to filter on a station."""

    PAYLOAD_REQUEST_TYPE_FILTER = 4
    PAYLOAD_REQUEST_TYPE_REMOVE = 6
    PAYLOAD_REQUEST_TYPE_NAME = 8
    PAYLOAD_RESPONSE_TYPE_RESET = 40
    PAYLOAD_RESPONSE_TYPE_FILTER = 5
    DEFAULT_MINUTES = 60
    TIME_TRAVEL_LIMIT = 24 * 60 * 60
    TEN_YEARS_IN_SECONDS = 10 * 365 * 24 * 60 * 60

    def __init__(self, state, db):
        """Initialize the FilterResponseCreator.

        Args:
            state (WebsocketConnectionState): WebsocketConnectionState instance that contains current state.
            db (psycopg2.Connection): Database connection (with autocommit).
        """
        self.state = state
        self.db = db
        self.logger = logging.getLogger('trackdirect')
        self.response_data_converter = ResponseDataConverter(state, db)
        self.packet_repository = PacketRepository(db)
        self.station_repository = StationRepository(db)
        self.config = TrackDirectConfig()

    def get_responses(self, request):
        """Creates responses related to a filter request.

        Args:
            request (dict): The request to process.

        Yields:
            dict: Response payloads.
        """
        self._update_state(request)
        if self.state.is_reset():
            yield self._get_reset_response()
        yield self._get_filter_response()

    def _update_state(self, request):
        """Update connection state based on filter request.

        Args:
            request (dict): The request to process.
        """
        request_type = request.get("payload_request_type")
        if request_type == self.PAYLOAD_REQUEST_TYPE_FILTER and "list" in request:
            station_ids = request.get("list", [])
            if station_ids:
                self.state.filter_station_id_dict = {int(station_id): True for station_id in station_ids}
            else:
                self._reset_filter()
            self.state.reset()

        elif request_type == self.PAYLOAD_REQUEST_TYPE_REMOVE and "station_id" in request:
            self.state.filter_station_id_dict.pop(int(request["station_id"]), None)
            self.state.reset()

        elif request_type == self.PAYLOAD_REQUEST_TYPE_NAME and "namelist" in request:
            station_names = request.get("namelist", [])
            if station_names:
                min_timestamp = int(time.time()) - (self.TEN_YEARS_IN_SECONDS if self.config.allow_time_travel else self.TIME_TRAVEL_LIMIT)
                for station_name in station_names:
                    stations = self.station_repository.get_object_list_by_name(station_name, None, None, min_timestamp)
                    for station in stations:
                        self.state.filter_station_id_dict[int(station.id)] = True
            else:
                self._reset_filter()
            self.state.reset()

    def _reset_filter(self):
        """Reset the filter state."""
        self.state.filter_station_id_dict = {}
        self.state.set_latest_map_bounds(0, 0, 0, 0)
        self.state.set_latest_minutes(self.DEFAULT_MINUTES, None)

    def _get_reset_response(self):
        """Create a reset response.

        Returns:
            dict: Reset response payload.
        """
        return {'payload_response_type': self.PAYLOAD_RESPONSE_TYPE_RESET}

    def _get_filter_response(self):
        """Create a filter response.

        Returns:
            dict: Filter response payload.
        """
        data = []
        if self.state.filter_station_id_dict:
            filter_station_ids = list(self.state.filter_station_id_dict.keys())
            data = self._get_filter_response_data(filter_station_ids)

        return {'payload_response_type': self.PAYLOAD_RESPONSE_TYPE_FILTER, 'data': data}

    def _get_filter_response_data(self, filter_station_ids):
        """Create data to be included in a filter response.

        Args:
            filter_station_ids (list): A list of all stations to filter on.

        Returns:
            list: Filter response data.
        """
        timestamp = (int(self.state.latest_time_travel_request) - int(self.state.latest_minutes_request) * 60
                     if self.state.latest_time_travel_request is not None
                     else int(time.time()) - int(self.state.latest_minutes_request) * 60)

        query = MostRecentPacketsQuery(self.state, self.db)
        query.enable_simulate_empty_station()
        packets = query.get_packets(filter_station_ids)
        data = self.response_data_converter.get_response_data(packets, [])
        self.state.reset()  # Reset to ensure client gets the same packet on history request

        result = [
            self._process_packet_data(packet_data, timestamp, filter_station_ids)
            for packet_data in data
            if self.config.allow_time_travel or packet_data['timestamp'] > int(time.time()) - self.TIME_TRAVEL_LIMIT
        ]
        return result

    def _process_packet_data(self, packet_data, timestamp, filter_station_ids):
        """Process individual packet data for filter response.

        Args:
            packet_data (dict): Packet data to process.
            timestamp (int): Requested timestamp.
            filter_station_ids (list): List of station IDs to filter on.

        Returns:
            dict: Processed packet data.
        """
        packet_data.update({
            'overwrite': 1,
            'realtime': 0,
            'packet_order_id': 1,  # Last packet for this station in this response
            'requested_timestamp': timestamp,
            'related': 0 if packet_data['station_id'] in filter_station_ids else 1
        })
        return packet_data
