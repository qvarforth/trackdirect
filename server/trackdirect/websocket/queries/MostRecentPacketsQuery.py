import  time
from server.trackdirect.repositories.PacketRepository import PacketRepository
from server.trackdirect.websocket.queries.MissingPacketsQuery import MissingPacketsQuery


class MostRecentPacketsQuery:
    """This query class returns the latest packet for moving stations and the latest packet for every unique position for stationary stations.

    Note:
        If no packets are found, they will be simulated.
    """

    def __init__(self, state, db):
        """Initialize the MostRecentPacketsQuery.

        Args:
            state (WebsocketConnectionState): The current state for a websocket connection.
            db (psycopg2.Connection): Database connection.
        """
        self.state = state
        self.db = db
        self.packet_repository = PacketRepository(db)
        self.simulate_empty_station = False

    def enable_simulate_empty_station(self):
        """Enable simulation even if no packets are available from the station."""
        self.simulate_empty_station = True

    def get_packets(self, station_ids):
        """Fetch the most recent packets for the specified stations.
        Returns the latest packet for moving stations and the latest packet for every unique position for stationary stations.

        Args:
            station_ids (list): A list of station IDs for which packets are needed.

        Returns:
            list: A list of packets.
        """

        if self.state.latest_time_travel_request is not None:
            timestamp = int(self.state.latest_time_travel_request) - (int(self.state.latest_minutes_request) * 60)
            packets = self.packet_repository.get_most_recent_confirmed_object_list_by_station_id_list_and_time_interval(
                station_ids, timestamp, self.state.latest_time_travel_request
            )
        else:
            timestamp = int(time.time()) - (int(self.state.latest_minutes_request) * 60)
            packets = self.packet_repository.get_most_recent_confirmed_object_list_by_station_id_list(
                station_ids, timestamp
            )

        packet_ids = [p.station_id for p in packets]
        if len(packets) < len(station_ids) or not all(id in packet_ids for id in station_ids): # Checking on array size is not sufficient, we have to make sure we have all the requested ids.
            # If we have no recent markers, we just send the latest that we have
            query = MissingPacketsQuery(self.state, self.db)
            if self.simulate_empty_station:
                query.enable_simulate_empty_station()

            missing_packets = query.get_missing_packets(station_ids, packets)
            if missing_packets:
                packets.extend(missing_packets)

        return packets
