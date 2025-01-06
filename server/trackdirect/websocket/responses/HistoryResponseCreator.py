import logging
import psycopg2, psycopg2.extras
from server.trackdirect.repositories.PacketRepository import PacketRepository
from server.trackdirect.websocket.queries.StationIdByMapSectorQuery import StationIdByMapSectorQuery
from server.trackdirect.websocket.responses.ResponseDataConverter import ResponseDataConverter


class HistoryResponseCreator:
    """The HistoryResponseCreator class creates websocket history responses for the latest websocket request."""

    def __init__(self, state, db):
        """The __init__ method.

        Args:
            state (WebsocketConnectionState): WebsocketConnectionState instance that contains current state
            db (psycopg2.Connection): Database connection (with autocommit)
        """
        self.state = state
        self.logger = logging.getLogger('trackdirect')
        self.db = db
        self.packet_repository = PacketRepository(db)
        self.response_data_converter = ResponseDataConverter(state, db)

    def get_responses(self, request, request_id):
        """Create all history responses for the current request.

        Args:
            request (dict): The request to process
            request_id (int): Request id of processed request

        Returns:
            generator
        """
        payload_type = request.get("payload_request_type")
        if payload_type in {1, 11}:
            if not self.state.is_valid_latest_position():
                return

            if (self.state.latest_ne_lat >= 90 and self.state.latest_ne_lng >= 180 and
                    self.state.latest_sw_lat <= -90 and self.state.latest_sw_lng <= -180):
                # Request is requesting too much
                return

            yield from self._get_map_sector_history_responses(request_id)

        elif payload_type == 7 and "station_id" in request:
            yield from self._get_station_history_responses([request["station_id"]], None, True)

        else:
            self.logger.error('Request is not supported: %s', request)

    def _get_map_sector_history_responses(self, request_id):
        """Creates all needed history responses for the currently visible map sectors.

        Args:
            request_id (int): Request id of processed request

        Returns:
            generator
        """
        map_sector_array = self.state.get_visible_map_sectors()
        if len(map_sector_array) > 20000:
            self.logger.error("Too many map sectors requested!")
            return

        handled_station_ids = set()
        for map_sector in map_sector_array:
            try:
                if request_id is not None and self.state.latest_requestId > request_id:
                    return

                found_station_ids = self._get_station_ids_by_map_sector(map_sector)
                station_ids = [station_id for station_id in found_station_ids if station_id not in handled_station_ids]
                handled_station_ids.update(station_ids)

                if station_ids:
                    yield from self._get_station_history_responses(station_ids, map_sector, False)
            except psycopg2.InterfaceError as e:
                raise e
            except Exception as e:
                self.logger.error('Error processing map sector %s: %s', map_sector, e, exc_info=True)

    def _get_station_history_responses(self, station_ids, map_sector, include_complete_history=False):
        """Creates one history response per station.

        Args:
            station_ids (array): An array of the stations that we want history data for
            map_sector (int): The map sector that we want history data for
            include_complete_history (boolean): Include all previous packets (even if we currently only request the latest packets)

        Returns:
            generator
        """
        min_timestamp = self.state.get_map_sector_timestamp(map_sector)
        for station_id in station_ids:
            try:
                if self.state.latest_time_travel_request is not None:
                    response = self._get_past_history_response(station_id, map_sector, min_timestamp, include_complete_history)
                else:
                    response = self._get_recent_history_response(station_id, map_sector, min_timestamp, include_complete_history)
                if response is not None:
                    yield response
            except psycopg2.InterfaceError as e:
                raise e
            except Exception as e:
                self.logger.error('Error processing station %s: %s', station_id, e, exc_info=True)

    def _get_recent_history_response(self, station_id, map_sector, min_timestamp, include_complete_history=False):
        """Creates a history response for the specified station, includes all packets from minTimestamp until now.

        Args:
            station_id (int): The station id that we want history data for
            map_sector (int): The map sector that we want history data for
            min_timestamp (int): The map sector min timestamp to use in query
            include_complete_history (boolean): Include all previous packets (even if we currently only request the latest packets)

        Returns:
            Dict
        """
        packets = []
        only_latest_packet_fetched = False
        current_station_ids = [station_id]

        current_min_timestamp = self.state.get_station_latest_timestamp_on_map(station_id) or min_timestamp

        if not self.state.only_latest_packet_requested or include_complete_history:
            packets = self.packet_repository.get_object_list_by_station_id_list(current_station_ids, current_min_timestamp)
        else:
            packets = self.packet_repository.get_latest_confirmed_object_list_by_station_id_list(current_station_ids, current_min_timestamp)
            if packets:
                packets = [packets[-1]]
            only_latest_packet_fetched = True

        if packets:
            flags = ["latest"] if only_latest_packet_fetched else []
            data = self.response_data_converter.get_response_data(packets, [map_sector], flags)
            return {'payload_response_type': 2, 'data': data}

    def _get_past_history_response(self, station_id, map_sector, min_timestamp, include_complete_history=False):
        """Creates a history response for the specified station, includes all packets between minTimestamp and the current latestTimeTravelRequest timestamp.

        Args:
            station_id (int): The station id that we want history data for
            map_sector (int): The map sector that we want history data for
            min_timestamp (int): The map sector min timestamp to use in query
            include_complete_history (boolean): Include all previous packets (even if we currently only request the latest packets)

        Returns:
            Dict
        """
        packets = []
        only_latest_packet_fetched = False
        current_station_ids = [station_id]

        current_min_timestamp = self.state.get_station_latest_timestamp_on_map(station_id) or min_timestamp

        if self.state.only_latest_packet_requested and not include_complete_history:
            if station_id not in self.state.stations_on_map_dict:
                only_latest_packet_fetched = True
                packets = self.packet_repository.get_latest_object_list_by_station_id_list_and_time_interval(
                    current_station_ids, current_min_timestamp, self.state.latest_time_travel_request)
        else:
            if not self.state.is_station_history_on_map(station_id):
                packets = self.packet_repository.get_object_list_by_station_id_list_and_time_interval(
                    current_station_ids, current_min_timestamp, self.state.latest_time_travel_request)

        if packets:
            flags = ["latest"] if only_latest_packet_fetched else []
            data = self.response_data_converter.get_response_data(packets, [map_sector], flags)
            return {'payload_response_type': 2, 'data': data}

    def _get_station_ids_by_map_sector(self, map_sector):
        """Returns the station id's in specified map sector.

        Args:
            map_sector (int): The map sector that we are interested in

        Returns:
            array of ints
        """
        query = StationIdByMapSectorQuery(self.db)
        if self.state.latest_time_travel_request is not None:
            if self.state.is_map_sector_known(map_sector):
                return []
            start_timestamp = self.state.latest_time_travel_request - (int(self.state.latest_minutes_request) * 60)
            end_timestamp = self.state.latest_time_travel_request
            return query.get_station_id_list_by_map_sector(map_sector, start_timestamp, end_timestamp)
        else:
            timestamp = self.state.get_map_sector_timestamp(map_sector)
            return query.get_station_id_list_by_map_sector(map_sector, timestamp, None)
