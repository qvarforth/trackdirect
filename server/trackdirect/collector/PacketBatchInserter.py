import logging
import psycopg2
import psycopg2.extras
from server.trackdirect.collector.StationLatestPacketModifier import StationLatestPacketModifier
from server.trackdirect.collector.PacketMapIdModifier import PacketMapIdModifier
from server.trackdirect.database.PacketTableCreator import PacketTableCreator
from server.trackdirect.database.PacketPathTableCreator import PacketPathTableCreator
from server.trackdirect.database.PacketWeatherTableCreator import PacketWeatherTableCreator
from server.trackdirect.database.PacketTelemetryTableCreator import PacketTelemetryTableCreator
from server.trackdirect.database.PacketOgnTableCreator import PacketOgnTableCreator


class PacketBatchInserter:
    """PacketBatchInserter is used to add a list of packets to the database"""

    def __init__(self, db, db_no_auto_commit):
        """
        Args:
            db (psycopg2.Connection): Database connection (with autocommit)
            db_no_auto_commit (psycopg2.Connection): Database connection (without autocommit)
        """
        self.db = db
        self.db_no_auto_commit = db_no_auto_commit
        self.logger = logging.getLogger(__name__)

        self.packet_id_list = []
        self.weather_packet_id_list = []
        self.ogn_packet_id_list = []
        self.telemetry_packet_id_list = []
        self.path_packet_id_list = []
        self.position_packet_id_list = []
        self.confirmed_position_packet_id_list = []

    def insert(self, packets):
        """
        Insert these packets into database

        Args:
            packets (list): Packets to insert
        """
        cur = self.db_no_auto_commit.cursor()
        try:
            self._make_sure_tables_exist(packets)
            self._insert_telemetry_definitions(packets)

            PacketMapIdModifier(cur, PacketTableCreator(self.db)).execute(packets)

            self._insert_into_packet_tables(packets, cur)

            self.db_no_auto_commit.commit()
        except psycopg2.InterfaceError as e:
            self.db_no_auto_commit.rollback()
            raise e
        except Exception as e:
            self.logger.error(e, exc_info=True)
            self.db_no_auto_commit.rollback()
        finally:
            cur.close()

        self._perform_post_insert_actions(packets)

    def _make_sure_tables_exist(self, packets):
        """
        Make sure all tables needed to insert specified packets exist

        Args:
            packets (list): Packets to insert
        """
        timestamp = packets[0].timestamp

        PacketTableCreator(self.db).get_table(timestamp)
        PacketPathTableCreator(self.db).get_table(timestamp)
        PacketWeatherTableCreator(self.db).get_packet_weather_table(timestamp)
        PacketTelemetryTableCreator(self.db).get_table(timestamp)
        PacketOgnTableCreator(self.db).get_table(timestamp)

    def _perform_post_insert_actions(self, packets):
        """
        Perform post insert updates like updating station latest packet and related

        Args:
            packets (list): Packets to insert
        """
        timestamp = packets[0].timestamp
        latest_packet_modifier = StationLatestPacketModifier(self.db)
        latest_packet_modifier.update_station_latest_packet(self.packet_id_list, timestamp)
        latest_packet_modifier.update_station_latest_telemetry_packet(self.telemetry_packet_id_list, timestamp)
        latest_packet_modifier.update_station_latest_weather_packet(self.weather_packet_id_list, timestamp)
        latest_packet_modifier.update_station_latest_ogn_packet(self.ogn_packet_id_list, timestamp)
        latest_packet_modifier.update_station_latest_location_packet(self.position_packet_id_list, timestamp)
        latest_packet_modifier.update_station_latest_confirmed_packet(self.confirmed_position_packet_id_list, timestamp)

    def _insert_into_packet_tables(self, packets, cur):
        """
        Insert packets into the correct packet tables

        Args:
            packets (list): Packets to insert
            cur (cursor): Database cursor to use
        """
        self._insert_into_packet_table(packets, cur)
        self._insert_into_packet_path_table(packets, cur)
        self._insert_into_packet_weather_table(packets, cur)
        self._insert_into_packet_ogn_table(packets, cur)
        self._insert_into_packet_telemetry_table(packets, cur)

    def _insert_into_packet_table(self, packets, cur):
        """
        Insert packets into the correct packet table

        Args:
            packets (list): Packets to insert
            cur (cursor): Database cursor to use
        """
        timestamp = packets[0].timestamp
        packet_table_creator = PacketTableCreator(self.db)
        packet_table = packet_table_creator.get_table(timestamp)

        date_packet_tuples = []
        for packet in packets:
            date_packet_tuples.append((packet.station_id,
                                     packet.sender_id,
                                     packet.map_id,
                                     packet.source_id,
                                     packet.packet_type_id,
                                     packet.latitude,
                                     packet.longitude,
                                     packet.posambiguity,
                                     packet.symbol,
                                     packet.symbol_table,
                                     packet.map_sector,
                                     packet.related_map_sectors,
                                     packet.marker_id,
                                     packet.marker_counter,
                                     packet.speed,
                                     packet.course,
                                     packet.altitude,
                                     packet.rng,
                                     packet.phg,
                                     packet.latest_phg_timestamp,
                                     packet.latest_rng_timestamp,
                                     packet.timestamp,
                                     packet.packet_tail_timestamp,
                                     packet.is_moving,
                                     packet.reported_timestamp,
                                     packet.position_timestamp,
                                     packet.comment,
                                     packet.raw_path,
                                     packet.raw))

        try:
            arg_string = b','.join(cur.mogrify(
                "(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                x) for x in date_packet_tuples)
            sql = f"INSERT INTO {packet_table} (station_id, sender_id, map_id, source_id, packet_type_id, latitude, longitude, posambiguity, symbol, symbol_table, map_sector, related_map_sectors, marker_id, marker_counter, speed, course, altitude, rng, phg, latest_phg_timestamp, latest_rng_timestamp, timestamp, packet_tail_timestamp, is_moving, reported_timestamp, position_timestamp, comment, raw_path, raw) VALUES {arg_string.decode()} RETURNING id"
            cur.execute(sql)
        except psycopg2.InterfaceError as e:
            raise e
        except Exception as e:
            self.logger.error(e, exc_info=True)
            return

        i = 0
        for record in cur:
            if packets[i]:
                packets[i].id = record["id"]

                if packets[i].map_id in [1]:
                    self.confirmed_position_packet_id_list.append(record["id"])
                elif packets[i].map_id in [1, 5, 7, 9]:
                    self.position_packet_id_list.append(record["id"])
                else:
                    # We only need to add the packet to the packetIdList if not in the positionPacketIdList or confirmedPositionPacketIdList array's
                    self.packet_id_list.append(record["id"])
            i += 1

    def _insert_into_packet_path_table(self, packets, cur):
        """
        Insert packets into the correct packet path table

        Args:
            packets (list): Packets to insert
            cur (cursor): Database cursor to use
        """
        timestamp = packets[0].timestamp
        packet_path_table_creator = PacketPathTableCreator(self.db)
        packet_path_table = packet_path_table_creator.get_table(timestamp)

        path_tuples = []
        for packet in packets:
            if packet.station_id_path:
                self.path_packet_id_list.append(packet.id)
                number = 0
                for station_id in packet.station_id_path:
                    if (packet.station_location_path
                            and packet.station_location_path[number]):
                        latitude = packet.station_location_path[number][0]
                        longitude = packet.station_location_path[number][1]
                        distance = packet.get_transmit_distance()

                        path_tuples.append(
                            (packet.id, station_id, latitude, longitude, packet.timestamp, distance, number,
                             packet.station_id, packet.latitude, packet.longitude))
                        number += 1

        if path_tuples:
            try:
                arg_string = b','.join(cur.mogrify(
                    "(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", x) for x in path_tuples)
                cur.execute(f"INSERT INTO {packet_path_table} (packet_id, station_id, latitude, longitude, timestamp, distance, number, sending_station_id, sending_latitude, sending_longitude) VALUES {arg_string.decode()}")
            except psycopg2.InterfaceError as e:
                raise e
            except Exception as e:
                self.logger.error(e, exc_info=True)

    def _insert_into_packet_weather_table(self, packets, cur):
        """
        Insert packets into the correct packet weather table

        Args:
            packets (list): Packets to insert
            cur (cursor): Database cursor to use
        """
        timestamp = packets[0].timestamp
        packet_weather_table_creator = PacketWeatherTableCreator(self.db)
        packet_weather_table = packet_weather_table_creator.get_packet_weather_table(timestamp)

        weather_tuples = []
        for packet in packets:
            if packet.weather:
                self.weather_packet_id_list.append(packet.id)
                weather_tuples.append((packet.id,
                                      packet.station_id,
                                      packet.timestamp,
                                      packet.weather.humidity,
                                      packet.weather.pressure,
                                      packet.weather.rain1h,
                                      packet.weather.rain24h,
                                      packet.weather.rain_since_midnight,
                                      packet.weather.temperature,
                                      packet.weather.wind_direction,
                                      packet.weather.wind_gust,
                                      packet.weather.wind_speed,
                                      packet.weather.luminosity,
                                      packet.weather.snow,
                                      packet.weather.wx_raw_timestamp))

        if weather_tuples:
            try:
                arg_string = b','.join(cur.mogrify(
                    "(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", x) for x in weather_tuples)
                cur.execute(f"INSERT INTO {packet_weather_table} (packet_id, station_id, timestamp, humidity, pressure, rain_1h, rain_24h, rain_since_midnight, temperature, wind_direction, wind_gust, wind_speed, luminosity, snow, wx_raw_timestamp) VALUES {arg_string.decode()}")
            except psycopg2.InterfaceError as e:
                raise e
            except Exception as e:
                self.logger.error(e, exc_info=True)


    def _insert_into_packet_ogn_table(self, packets, cur):
        """
        Insert packets into the correct packet OGN table

        Args:
            packets (list): Packets to insert
            cur (cursor): Database cursor to use
        """
        timestamp = packets[0].timestamp
        packet_ogn_table_creator = PacketOgnTableCreator(self.db)
        packet_ogn_table = packet_ogn_table_creator.get_table(timestamp)

        ogn_tuples = []
        for packet in packets:
            if packet.ogn:
                self.ogn_packet_id_list.append(packet.id)
                ogn_tuples.append((packet.id,
                                  packet.station_id,
                                  packet.timestamp,
                                  packet.ogn.ogn_sender_address,
                                  packet.ogn.ogn_address_type_id,
                                  packet.ogn.ogn_aircraft_type_id,
                                  packet.ogn.ogn_climb_rate,
                                  packet.ogn.ogn_turn_rate,
                                  packet.ogn.ogn_signal_to_noise_ratio,
                                  packet.ogn.ogn_bit_errors_corrected,
                                  packet.ogn.ogn_frequency_offset))

        if ogn_tuples:
            try:
                arg_string = b','.join(cur.mogrify(
                    "(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", x) for x in ogn_tuples)
                cur.execute(f"INSERT INTO {packet_ogn_table} (packet_id, station_id, timestamp, ogn_sender_address, ogn_address_type_id, ogn_aircraft_type_id, ogn_climb_rate, ogn_turn_rate, ogn_signal_to_noise_ratio, ogn_bit_errors_corrected, ogn_frequency_offset) VALUES {arg_string.decode()}")
            except psycopg2.InterfaceError as e:
                raise e
            except Exception as e:
                self.logger.error(e, exc_info=True)

    def _insert_into_packet_telemetry_table(self, packets, cur):
        """
        Insert packets into the correct packet telemetry table

        Args:
            packets (list): Packets to insert
            cur (cursor): Database cursor to use
        """
        timestamp = packets[0].timestamp
        packet_telemetry_table_creator = PacketTelemetryTableCreator(self.db)
        packet_telemetry_table = packet_telemetry_table_creator.get_table(timestamp)

        telemetry_tuples = []
        for packet in packets:
            if packet.telemetry:
                self.telemetry_packet_id_list.append(packet.id)
                if not packet.telemetry.is_duplicate():
                    telemetry_tuples.append((packet.id,
                                            packet.station_id,
                                            packet.timestamp,
                                            packet.telemetry.val1,
                                            packet.telemetry.val2,
                                            packet.telemetry.val3,
                                            packet.telemetry.val4,
                                            packet.telemetry.val5,
                                            packet.telemetry.bits,
                                            packet.telemetry.seq))

        if telemetry_tuples:
            try:
                arg_string = b','.join(cur.mogrify(
                    "(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", x) for x in telemetry_tuples)
                cur.execute(
                    f"INSERT INTO {packet_telemetry_table} (packet_id, station_id, timestamp, val1, val2, val3, val4, val5, bits, seq) VALUES {arg_string.decode()} RETURNING id")
            except psycopg2.InterfaceError as e:
                raise e
            except Exception as e:
                self.logger.error(e, exc_info=True)

            packet_telemetry_ids = [record['id'] for record in cur.fetchall()]

            try:
                cur.execute(f"""UPDATE {packet_telemetry_table} packet_telemetry SET
                                        station_telemetry_param_id = (SELECT id FROM station_telemetry_param WHERE station_id = packet_telemetry.station_id AND valid_to_ts IS NULL),
                                        station_telemetry_unit_id = (SELECT id FROM station_telemetry_unit WHERE station_id = packet_telemetry.station_id AND valid_to_ts IS NULL),
                                        station_telemetry_eqns_id = (SELECT id FROM station_telemetry_eqns WHERE station_id = packet_telemetry.station_id AND valid_to_ts IS NULL),
                                        station_telemetry_bits_id = (SELECT id FROM station_telemetry_bits WHERE station_id = packet_telemetry.station_id AND valid_to_ts IS NULL)
                                    WHERE id IN %s""", (tuple(packet_telemetry_ids),))
            except psycopg2.InterfaceError as e:
                raise e
            except Exception as e:
                self.logger.error(e, exc_info=True)

    def _insert_telemetry_definitions(self, packets):
        """
        Insert telemetry definitions (PARAM, UNIT, EQNS, BITS) if any exist in current packets

        Args:
            packets (list): Packets to insert
        """
        for packet in packets:
            if packet.station_telemetry_bits:
                packet.station_telemetry_bits.save()
            if packet.station_telemetry_eqns:
                packet.station_telemetry_eqns.save()
            if packet.station_telemetry_param:
                packet.station_telemetry_param.save()
            if packet.station_telemetry_unit:
                packet.station_telemetry_unit.save()