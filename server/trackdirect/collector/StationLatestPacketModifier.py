from server.trackdirect.database.PacketTableCreator import PacketTableCreator
import psycopg2

class StationLatestPacketModifier:
    """The StationLatestPacketModifier class contains functionality to modify the station latest packet."""

    def __init__(self, db: psycopg2.extensions.connection):
        """The __init__ method.

        Args:
            db (psycopg2.extensions.connection): Database connection
        """
        self.db = db
        self.packet_table_creator = PacketTableCreator(db)

    def update_station_latest_confirmed_packet(self, packet_id_list, timestamp):
        """Updates several stations latest confirmed packet based on the specified list of packet id's.

        Args:
            packet_id_list (list): Array of packet id's that should be used to set the latest packets on related stations
            timestamp (int): Unix timestamp which is in the same date as the receive date of all packets (UTC)

        Returns:
            int: Number of updated stations
        """
        if packet_id_list:
            packet_table = self.packet_table_creator.get_table(timestamp)
            cur = self.db.cursor()
            sql = cur.mogrify(f"""
                UPDATE station SET latest_sender_id = packet.sender_id,
                    latest_confirmed_packet_id = packet.id,
                    latest_confirmed_marker_id = packet.marker_id,
                    latest_confirmed_packet_timestamp = packet.timestamp,
                    latest_confirmed_symbol = packet.symbol,
                    latest_confirmed_symbol_table = packet.symbol_table,
                    latest_confirmed_latitude = packet.latitude,
                    latest_confirmed_longitude = packet.longitude,
                    latest_location_packet_id = packet.id,
                    latest_location_packet_timestamp = packet.timestamp,
                    latest_packet_id = packet.id,
                    latest_packet_timestamp = packet.timestamp
                FROM {packet_table} packet
                WHERE packet.station_id = station.id
                AND packet.id IN %s""", (tuple(packet_id_list),))
            cur.execute(sql)
            row_count = cur.rowcount
            cur.close()
            return row_count
        return 0

    def update_station_latest_location_packet(self, packet_id_list, timestamp):
        """Updates several stations latest location packet based on the specified list of packet id's.

        Args:
            packet_id_list (list): Array of packet id's that should be used to set the latest packets on related stations
            timestamp (int): Unix timestamp which is in the same date as the receive date of all packets (UTC)

        Returns:
            int: Number of updated stations
        """
        if packet_id_list:
            packet_table = self.packet_table_creator.get_table(timestamp)
            cur = self.db.cursor()
            sql = cur.mogrify(f"""
                UPDATE station SET latest_location_packet_id = packet.id,
                    latest_location_packet_timestamp = packet.timestamp,
                    latest_packet_id = packet.id,
                    latest_packet_timestamp = packet.timestamp 
                FROM {packet_table} packet
                WHERE packet.station_id = station.id
                AND packet.id IN %s""", (tuple(packet_id_list),))
            cur.execute(sql)
            row_count = cur.rowcount
            cur.close()
            return row_count
        return 0

    def update_station_latest_packet(self, packet_id_list, timestamp):
        """Updates several stations latest packet based on the specified list of packet id's.

        Args:
            packet_id_list (list): Array of packet id's that should be used to set the latest packets on related stations
            timestamp (int): Unix timestamp which is in the same date as the receive date of all packets (UTC)

        Returns:
            int: Number of updated stations
        """
        if packet_id_list:
            packet_table = self.packet_table_creator.get_table(timestamp)
            cur = self.db.cursor()
            sql = cur.mogrify(f"""
                UPDATE station SET latest_packet_id = packet.id,
                    latest_packet_timestamp = packet.timestamp
                FROM {packet_table} packet
                WHERE packet.station_id = station.id
                AND packet.id IN %s""", (tuple(packet_id_list),))
            cur.execute(sql)
            row_count = cur.rowcount
            cur.close()
            return row_count
        return 0

    def update_station_latest_telemetry_packet(self, packet_id_list, timestamp):
        """Updates several stations latest telemetry packet based on the specified list of packet id's.

        Args:
            packet_id_list (list): Array of packet id's that should be used to set the latest packets on related stations
            timestamp (int): Unix timestamp which is in the same date as the receive date of all packets (UTC)

        Returns:
            int: Number of updated stations
        """
        if packet_id_list:
            packet_table = self.packet_table_creator.get_table(timestamp)
            cur = self.db.cursor()
            sql = cur.mogrify(f"""
                UPDATE station SET latest_telemetry_packet_id = packet.id,
                    latest_telemetry_packet_timestamp = packet.timestamp
                FROM {packet_table} packet
                WHERE packet.station_id = station.id
                AND packet.id IN %s""", (tuple(packet_id_list),))
            cur.execute(sql)
            row_count = cur.rowcount
            cur.close()
            return row_count
        return 0

    def update_station_latest_ogn_packet(self, packet_id_list, timestamp):
        """Updates several stations latest OGN packet based on the specified list of packet id's.

        Args:
            packet_id_list (list): Array of packet id's that should be used to set the latest packets on related stations
            timestamp (int): Unix timestamp which is in the same date as the receive date of all packets (UTC)

        Returns:
            int: Number of updated stations
        """
        if packet_id_list:
            packet_ogn_table = self.packet_table_creator.get_table(timestamp) + '_ogn'
            cur = self.db.cursor()
            sql = cur.mogrify(f"""
                UPDATE station SET latest_ogn_packet_id = packet_ogn.packet_id,
                    latest_ogn_packet_timestamp = packet_ogn.timestamp,
                    latest_ogn_sender_address = packet_ogn.ogn_sender_address,
                    latest_ogn_aircraft_type_id = packet_ogn.ogn_aircraft_type_id,
                    latest_ogn_address_type_id = packet_ogn.ogn_address_type_id
                FROM {packet_ogn_table} packet_ogn
                WHERE packet_ogn.station_id = station.id
                AND packet_ogn.packet_id IN %s""", (tuple(packet_id_list),))
            cur.execute(sql)
            row_count = cur.rowcount
            cur.close()
            return row_count
        return 0

    def update_station_latest_weather_packet(self, packet_id_list, timestamp):
        """Updates several stations latest weather packet based on the specified list of packet id's.

        Args:
            packet_id_list (list): Array of packet id's that should be used to set the latest packets on related stations
            timestamp (int): Unix timestamp which is in the same date as the receive date of all packets (UTC)

        Returns:
            int: Number of updated stations
        """
        if packet_id_list:
            packet_table = self.packet_table_creator.get_table(timestamp)
            cur = self.db.cursor()
            sql = cur.mogrify(f"""
                UPDATE station SET latest_weather_packet_id = packet.id,
                    latest_weather_packet_timestamp = packet.timestamp,
                    latest_weather_packet_comment = packet.comment
                FROM {packet_table} packet
                WHERE packet.station_id = station.id
                AND packet.id IN %s""", (tuple(packet_id_list),))
            cur.execute(sql)
            row_count = cur.rowcount
            cur.close()
            return row_count
        return 0