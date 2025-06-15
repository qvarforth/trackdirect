import logging
from server.trackdirect.repositories.PacketRepository import PacketRepository
from server.trackdirect.websocket.queries.MissingPacketsQuery import MissingPacketsQuery
from server.trackdirect.websocket.responses.ResponseDataConverter import ResponseDataConverter
from typing import List, Dict, Optional

class FilterHistoryResponseCreator:
    """The FilterHistoryResponseCreator class creates history responses for stations that we are filtering on."""

    def __init__(self, state, db):
        """
        Initialize the FilterHistoryResponseCreator.

        Args:
            state (WebsocketConnectionState): WebsocketConnectionState instance that contains current state.
            db (psycopg2.Connection): Database connection (with autocommit).
        """
        self.state = state
        self.logger = logging.getLogger('trackdirect')
        self.db = db
        self.response_data_converter = ResponseDataConverter(state, db)
        self.packet_repository = PacketRepository(db)

    def get_response(self) -> Optional[Dict]:
        """Returns a filter history response.

        Returns:
            Optional[Dict]: The response payload or None if no packets are found.
        """
        filter_station_ids = list(self.state.filter_station_id_dict.keys())
        packets = self._get_packets(filter_station_ids)

        if self.state.is_map_empty():
            query = MissingPacketsQuery(self.state, self.db)
            query.enable_simulate_empty_station()
            missing_packets = query.get_missing_packets(filter_station_ids, packets)
            packets.extend(missing_packets)

        if packets:
            data = self.response_data_converter.get_response_data(packets, [])
            payload = {'payload_response_type': 2, 'data': data}
            self.logger.debug("Response payload created with %d packets", len(packets))
            return payload
        else:
            self.logger.debug("No packets found for the given station IDs.")
            return None

    def _get_packets(self, station_ids: List[int]) -> List:
        """Returns packets to be used in a filter history response.

        Args:
            station_ids (List[int]): The station IDs that we want history data for.

        Returns:
            List: A list of packets.
        """
        if not station_ids:
            return []

        min_timestamp = None
        if (len(station_ids) > 0) :
            min_timestamp = self.state.get_station_latest_timestamp_on_map(list(station_ids)[0])
        if (min_timestamp is None) :
            min_timestamp = self.state.get_map_sector_timestamp(None) # None as argument is useful even when not dealing with map-sectors
        if (len(station_ids) > 1) :
            for stationId in station_ids :
                timestamp = self.state.get_station_latest_timestamp_on_map(station_ids)
                if (timestamp is not None and timestamp > min_timestamp) :
                    min_timestamp = timestamp
                    
        if self.state.latest_time_travel_request is not None:
            if not self.state.is_stations_on_map(station_ids):
                return self.packet_repository.get_object_list_by_station_id_list_and_time_interval(
                    station_ids, min_timestamp, self.state.latest_time_travel_request
                )
        else:
            return self.packet_repository.get_object_list_by_station_id_list(station_ids, min_timestamp)

        return []
