import logging
import datetime
from server.trackdirect.repositories.PacketRepository import PacketRepository
from server.trackdirect.repositories.StationRepository import StationRepository
from server.trackdirect.repositories.PacketWeatherRepository import PacketWeatherRepository
from server.trackdirect.repositories.PacketOgnRepository import PacketOgnRepository
from server.trackdirect.repositories.OgnDeviceRepository import OgnDeviceRepository
from server.trackdirect.database.DatabaseObjectFinder import DatabaseObjectFinder
from server.trackdirect.websocket.queries.MostRecentPacketsQuery import MostRecentPacketsQuery


class ResponseDataConverter:
    """An instance of ResponseDataConverter is used to create response content data based on packet objects."""

    def __init__(self, state, db):
        """Initialize the ResponseDataConverter.

        Args:
            state (WebsocketConnectionState): The current state for a websocket connection.
            db (psycopg2.Connection): Database connection (with autocommit).
        """
        self.state = state
        self.logger = logging.getLogger('trackdirect')
        self.db = db
        self.packet_repository = PacketRepository(db)
        self.station_repository = StationRepository(db)
        self.packet_weather_repository = PacketWeatherRepository(db)
        self.db_object_finder = DatabaseObjectFinder(db)
        self.packet_ogn_repository = PacketOgnRepository(db)
        self.ogn_device_repository = OgnDeviceRepository(db)

    def get_response_data(self, packets, map_sector_list=None, flags=None, iteration_counter=0):
        """Create response data based on specified packets.

        Args:
            packets (list): An array of the Packet's that should be converted to packet dict responses.
            map_sector_list (list, optional): An array of the current handled map sectors.
            flags (list, optional): An array with additional flags (like "realtime", "latest").
            iteration_counter (int): This functionality will call itself to find related packets, this argument is used to remember the number of iterations.

        Returns:
            list: An array of packet dicts.
        """
        if flags is None:
            flags = []

        response_data = []
        for index, packet in enumerate(packets):
            packet_dict = packet.get_dict(True)
            packet_dict['packet_order_id'] = self._get_packet_order_id(packets, index, flags)

            self._update_state(packet, map_sector_list, flags)
            self._add_overwrite_status(packet_dict)
            if ("latest" not in flags and "realtime" not in flags) or self.state.is_station_history_on_map(packet.station_id):
                if packet_dict['packet_order_id'] == 1:
                    self._add_station_weather_data(packet_dict)
                    self._add_station_telemetry_data(packet_dict)
                    if packet.source_id == 5:
                        self._add_station_ogn_data(packet_dict)
                if packet.source_id == 5:
                    self._add_station_ogn_device_data(packet_dict)
                self._add_packet_phg_rng(packet_dict)

            if "realtime" not in flags:
                self._add_station_id_path(packet_dict)

            self._set_flags(packet_dict, flags)
            response_data.append(packet_dict)
        return self._extend_response_with_more_packets(response_data, flags, iteration_counter)

    def _get_packet_order_id(self, packets, index, flags):
        """Returns the order id of the packet at specified index.

        Args:
            packets (list): An array of the Packet's that should be converted to packet dict responses.
            index (int): Index of the packet that we want an order id for.
            flags (list): An array with additional flags (like "realtime", "latest").

        Returns:
            int: The order id of the packet.
        """
        if "realtime" in flags:
            return 1
        elif len(packets) - 1 == index:
            return 1  # Last packet in response for this marker
        elif packets[index].marker_id != packets[index + 1].marker_id:
            return 1  # Last packet in response for this marker
        elif index == 0 or packets[index].marker_id != packets[index - 1].marker_id:
            return 3  # First packet in response for this marker
        else:
            return 2  # Middle packet in response for this marker

    def _update_state(self, packet, map_sector_list, flags):
        """Update connection state based on packet on the way to client.

        Args:
            packet (Packet): The packet that is on the way to client.
            map_sector_list (list): An array of the current handled map sectors.
            flags (list): An array with additional flags (like "realtime", "latest").
        """
        self.state.set_station_latest_timestamp(packet.station_id, packet.timestamp)

        if packet.station_id not in self.state.stations_on_map_dict:
            self.state.stations_on_map_dict[packet.station_id] = True

        if self.state.is_station_history_on_map(packet.station_id):
            self.state.set_complete_station_latest_timestamp(packet.station_id, packet.timestamp)
        elif "latest" not in flags and "realtime" not in flags and "related" not in flags:
            self.state.set_complete_station_latest_timestamp(packet.station_id, packet.timestamp)
        elif "related" in flags and packet.packet_tail_timestamp == packet.timestamp:
            self.state.set_complete_station_latest_timestamp(packet.station_id, packet.timestamp)

        if map_sector_list and packet.map_sector is not None and packet.map_sector in map_sector_list:
            if "latest" not in flags:
                self.state.set_map_sector_latest_time_stamp(packet.map_sector, packet.timestamp)
            else:
                self.state.set_map_sector_latest_overwrite_time_stamp(packet.map_sector, packet.timestamp)

    def _set_flags(self, packet_dict, flags):
        """Set additional flags that will tell client a bit more about the packet.

        Args:
            packet_dict (dict): The packet to which we should modify.
            flags (list): An array with additional flags (like "realtime", "latest").
        """
        packet_dict["db"] = 0 if "realtime" in flags else 1
        packet_dict["realtime"] = 1 if "realtime" in flags else 0

    def _add_overwrite_status(self, packet_dict):
        """Set packet overwrite status.

        Args:
            packet_dict (dict): The packet to which we should modify.
        """
        packet_dict['overwrite'] = 0

        if not self.state.is_station_history_on_map(packet_dict["station_id"]):
            packet_dict['overwrite'] = 1

    def _add_packet_phg_rng(self, packet_dict):
        """Add previous reported phg and rng to the specified packet.

        Args:
            packet_dict (dict): The packet to which we should modify.
        """
        if 'phg' in packet_dict and 'rng' in packet_dict:
            if packet_dict['phg'] is None and packet_dict['latest_phg_timestamp'] is not None and packet_dict['latest_phg_timestamp'] < packet_dict['timestamp']:
                related_packet = self.packet_repository.get_object_by_station_id_and_timestamp(packet_dict['station_id'], packet_dict['latest_phg_timestamp'])
                if related_packet.phg is not None and related_packet.marker_id == packet_dict['marker_id']:
                    packet_dict['phg'] = related_packet.phg

            if packet_dict['rng'] is None and packet_dict['latest_rng_timestamp'] is not None and packet_dict['latest_rng_timestamp'] < packet_dict['timestamp']:
                related_packet = self.packet_repository.get_object_by_station_id_and_timestamp(packet_dict['station_id'], packet_dict['latest_rng_timestamp'])
                if related_packet.rng is not None and related_packet.marker_id == packet_dict['marker_id']:
                    packet_dict['rng'] = related_packet.rng

    def _add_station_ogn_data(self, packet_dict):
        """Add OGN data to packet.

        Args:
            packet_dict (dict): The packet to which we should add the related data.
        """
        if 'ogn' not in packet_dict or packet_dict['ogn'] is None:
            station = self.station_repository.get_object_by_id(packet_dict['station_id'])
            ts = int(packet_dict['timestamp']) - (24 * 60 * 60)
            if station.latest_ogn_packet_timestamp is not None and station.latest_ogn_packet_timestamp > ts:
                packet_dict['latest_ogn_packet_timestamp'] = station.latest_ogn_packet_timestamp

                related_packet_dict = None
                if station.latest_ogn_packet_id == packet_dict['id']:
                    related_packet_dict = packet_dict
                else:
                    related_packet = self.packet_repository.get_object_by_id_and_timestamp(station.latest_ogn_packet_id, station.latest_ogn_packet_timestamp)
                    if related_packet.is_existing_object():
                        related_packet_dict = related_packet.get_dict()

                if related_packet_dict is not None:
                    if related_packet_dict['marker_id'] is not None and related_packet_dict['marker_id'] == packet_dict['marker_id']:
                        packet_ogn = self.packet_ogn_repository.get_object_by_packet_id_and_timestamp(station.latest_ogn_packet_id, station.latest_ogn_packet_timestamp)
                        if packet_ogn.is_existing_object():
                            packet_dict['ogn'] = packet_ogn.get_dict()

    def _add_station_ogn_device_data(self, packet_dict):
        """Add OGN device data to packet.

        Args:
            packet_dict (dict): The packet to which we should add the related data.
        """
        station = self.station_repository.get_object_by_id(packet_dict['station_id'])
        if station.latest_ogn_sender_address is not None:
            ogn_device = self.ogn_device_repository.get_object_by_device_id(station.latest_ogn_sender_address)
            if ogn_device.is_existing_object():
                packet_dict['ogn_device'] = ogn_device.get_dict()

    def _add_station_weather_data(self, packet_dict):
        """Add weather data to packet.

        Args:
            packet_dict (dict): The packet to which we should add the related data.
        """
        if 'weather' not in packet_dict or packet_dict['weather'] is None:
            station = self.station_repository.get_object_by_id(packet_dict['station_id'])
            ts = int(packet_dict['timestamp']) - (24 * 60 * 60)
            if station.latest_weather_packet_timestamp is not None and station.latest_weather_packet_timestamp > ts:
                packet_dict['latest_weather_packet_timestamp'] = station.latest_weather_packet_timestamp

                related_packet_dict = None
                if station.latest_weather_packet_id == packet_dict['id']:
                    related_packet_dict = packet_dict
                else:
                    related_packet = self.packet_repository.get_object_by_id_and_timestamp(station.latest_weather_packet_id, station.latest_weather_packet_timestamp)
                    if related_packet.is_existing_object():
                        related_packet_dict = related_packet.get_dict()

                if related_packet_dict is not None:
                    if related_packet_dict['marker_id'] is not None and related_packet_dict['marker_id'] == packet_dict['marker_id']:
                        packet_weather = self.packet_weather_repository.get_object_by_packet_id_and_timestamp(station.latest_weather_packet_id, station.latest_weather_packet_timestamp)
                        if packet_weather.is_existing_object():
                            packet_dict['weather'] = packet_weather.get_dict()

    def _add_station_telemetry_data(self, packet_dict):
        """Add telemetry data to packet.

        Args:
            packet_dict (dict): The packet to which we should add the related data.
        """
        if 'telemetry' not in packet_dict or packet_dict['telemetry'] is None:
            station = self.station_repository.get_object_by_id(packet_dict['station_id'])
            ts = int(packet_dict['timestamp']) - (24 * 60 * 60)
            if station.latest_telemetry_packet_timestamp is not None and station.latest_telemetry_packet_timestamp > ts:
                packet_dict['latest_telemetry_packet_timestamp'] = station.latest_telemetry_packet_timestamp

    def _add_station_id_path(self, packet_dict):
        """Add the station id path to the specified packet.

        Args:
            packet_dict (dict): The packet to which we should add the related station id path.
        """
        station_id_path = []
        station_name_path = []
        station_location_path = []

        if packet_dict['raw_path'] is not None and "TCPIP*" not in packet_dict['raw_path'] and "TCPXX*" not in packet_dict['raw_path']:
            packet_date = datetime.datetime.utcfromtimestamp(int(packet_dict['timestamp'])).strftime('%Y%m%d')
            date_packet_table = 'packet' + packet_date
            date_packet_path_table = date_packet_table + '_path'

            if self.db_object_finder.check_table_exists(date_packet_path_table):
                with self.db.cursor() as select_cursor:
                    sql = """SELECT station_id, station.name station_name, latitude, longitude 
                             FROM {} 
                             JOIN station ON station.id = station_id 
                             WHERE packet_id = %s 
                             ORDER BY number""".format(date_packet_path_table)
                    select_cursor.execute(sql, (packet_dict['id'],))

                    for record in select_cursor:
                        station_id_path.append(record[0])
                        station_name_path.append(record[1])
                        station_location_path.append([record[2], record[3]])

        packet_dict['station_id_path'] = station_id_path
        packet_dict['station_name_path'] = station_name_path
        packet_dict['station_location_path'] = station_location_path

    def get_dict_list_from_packet_list(self, packets):
        """Returns a packet dict list from a packet list.

        Args:
            packets (list): Array of Packet instances.

        Returns:
            list: An array of packet dicts.
        """
        return [packet.get_dict() for packet in packets]

    def _extend_response_with_more_packets(self, packet_dicts, flags, iteration_counter):
        """Extend the specified array with related packets.

        Args:
            packet_dicts (list): An array of the packet response dicts.
            flags (list): An array with additional flags (like "realtime", "latest").
            iteration_counter (int): This functionality will call itself to find related packets, this argument is used to remember the number of iterations.

        Returns:
            list: The modified packet array.
        """
        all_packet_dicts = []

        if packet_dicts:
            related_station_ids = {}
            for packet_dict in packet_dicts:
                if packet_dict['is_moving'] == 1 or packet_dict['packet_order_id'] == 1:
                    if packet_dict['station_id_path']:
                        for station_id in packet_dict['station_id_path']:
                            if station_id not in self.state.stations_on_map_dict:
                                related_station_ids[station_id] = True

            for packet_dict in packet_dicts:
                if packet_dict['station_id'] in related_station_ids:
                    del related_station_ids[packet_dict['station_id']]

            if related_station_ids:
                related_station_packets = self._get_related_station_packets_by_station_ids(list(related_station_ids.keys()))

                for related_station_id in related_station_ids.keys():
                    if related_station_id not in self.state.stations_on_map_dict:
                        self.state.stations_on_map_dict[related_station_id] = True

                if related_station_packets:
                    related_station_packet_dicts = self.get_response_data(
                        related_station_packets, None, ["latest", "related"] if "latest" in flags else ["related"], iteration_counter + 1
                    )
                    all_packet_dicts.extend(related_station_packet_dicts)

        all_packet_dicts.extend(packet_dicts)
        return all_packet_dicts

    def _get_related_station_packets_by_station_ids(self, related_station_id_list):
        """Returns a list of the latest packet for the specified stations.

        Args:
            related_station_id_list (list): Array of related station id's.

        Returns:
            list: An array of the latest packet for the specified stations.
        """
        if related_station_id_list:
            query = MostRecentPacketsQuery(self.state, self.db)
            query.enable_simulate_empty_station()
            return query.get_packets(related_station_id_list)
        return []
