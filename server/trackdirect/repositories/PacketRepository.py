from server.trackdirect.common.Repository import Repository
from server.trackdirect.objects.Packet import Packet
from server.trackdirect.database.PacketTableCreator import PacketTableCreator
from server.trackdirect.exceptions.TrackDirectMissingTableError import TrackDirectMissingTableError
from server.trackdirect.database.DatabaseObjectFinder import DatabaseObjectFinder


class PacketRepository(Repository):
    """The PacketRepository class contains different methods that create Packet instances."""

    def __init__(self, db):
        """Initialize PacketRepository with a database connection."""
        super().__init__(db)
        self.packet_table_creator = PacketTableCreator(self.db)
        self.packet_table_creator.disable_create_if_missing()
        self.db_object_finder = DatabaseObjectFinder(db)

    def get_object_by_id(self, id):
        """Return a Packet object based on the specified id in the database."""
        with self.db.cursor() as cursor:
            cursor.execute("SELECT * FROM packet WHERE id = %s", (id,))
            record = cursor.fetchone()
        return self.get_object_from_record(record)

    def get_object_by_id_and_timestamp(self, id, timestamp):
        """Return a Packet object based on the specified id and timestamp."""
        try:
            packet_table = self.packet_table_creator.get_table(timestamp)
            with self.db.cursor() as cursor:
                cursor.execute(f"SELECT * FROM {packet_table} WHERE id = %s", (id,))
                record = cursor.fetchone()
            return self.get_object_from_record(record)
        except TrackDirectMissingTableError:
            return self.create()

    def get_object_by_station_id_and_timestamp(self, station_id, timestamp):
        """Return a Packet object based on the specified station_id and timestamp."""
        try:
            packet_table = self.packet_table_creator.get_table(timestamp)
            with self.db.cursor() as cursor:
                cursor.execute(f"""
                    SELECT * FROM {packet_table}
                    WHERE station_id = %s AND timestamp = %s
                    ORDER BY id LIMIT 1
                """, (station_id, timestamp))
                record = cursor.fetchone()
            return self.get_object_from_record(record)
        except TrackDirectMissingTableError:
            return self.create()

    def get_latest_object_list_by_station_id_list_and_time_interval(self, station_id_list, min_packet_timestamp, max_packet_timestamp, only_confirmed=True):
        """Return an array of the latest Packet objects specified by station ids."""
        if not station_id_list:
            return []

        result = []
        found_station_id_list = []
        packet_tables = self.packet_table_creator.get_tables(min_packet_timestamp, max_packet_timestamp)
        map_id_list = [1, 2, 12] if only_confirmed else [1, 2, 5, 7, 9, 12]

        with self.db.cursor() as cursor:
            for packet_table in reversed(packet_tables):
                station_id_list_to_find = tuple(set(station_id_list) - set(found_station_id_list))
                if station_id_list_to_find:
                    cursor.execute(f"""
                        SELECT * FROM {packet_table} packet
                        WHERE id IN (
                            SELECT MAX(id)
                            FROM {packet_table} packet
                            WHERE map_id IN %s
                                AND station_id IN %s
                                AND timestamp > %s
                                AND timestamp <= %s
                            GROUP BY station_id
                        )
                        ORDER BY packet.marker_id DESC, packet.id DESC
                    """, (tuple(map_id_list), station_id_list_to_find, min_packet_timestamp, max_packet_timestamp))

                    for record in cursor:
                        if record and record['station_id'] not in found_station_id_list:
                            result.append(self.get_object_from_record(record))
                            found_station_id_list.append(record['station_id'])

                if len(found_station_id_list) >= len(station_id_list):
                    break

        return result

    def get_object_list_by_station_id_list_and_time_interval(self, station_id_list, min_packet_timestamp, max_packet_timestamp):
        """Return an array of Packet objects specified by station ids."""
        if not station_id_list:
            return []

        result = []
        packet_tables = self.packet_table_creator.get_tables(min_packet_timestamp, max_packet_timestamp)

        with self.db.cursor() as cursor:
            for packet_table in packet_tables:
                cursor.execute(f"""
                    SELECT * FROM {packet_table} packet
                    WHERE map_id IN (1, 2, 5, 7, 9, 12)
                        AND station_id IN %s
                        AND timestamp > %s
                        AND timestamp <= %s
                    ORDER BY packet.marker_id, packet.id
                """, (tuple(station_id_list), min_packet_timestamp, max_packet_timestamp))

                for record in cursor:
                    if record:
                        result.append(self.get_object_from_record(record))

                cursor.execute(f"""
                    SELECT * FROM {packet_table} packet
                    WHERE map_id = 12
                        AND station_id IN %s
                        AND position_timestamp <= %s
                        AND timestamp > %s
                    ORDER BY packet.marker_id, packet.id
                """, (tuple(station_id_list), max_packet_timestamp, min_packet_timestamp))

                for record in cursor:
                    if record:
                        result.append(self.get_object_from_record(record))

        return result

    def get_object_list_by_station_id_list(self, station_id_list, min_packet_timestamp):
        """Return an array of Packet objects specified by station ids."""
        if not station_id_list:
            return []

        result = []
        packet_tables = self.packet_table_creator.get_tables(min_packet_timestamp)

        with self.db.cursor() as cursor:
            for packet_table in packet_tables:
                cursor.execute(f"""
                    SELECT * FROM {packet_table} packet
                    WHERE map_id IN (1, 5, 7, 9)
                        AND station_id IN %s
                        AND timestamp > %s
                    ORDER BY packet.marker_id, packet.id
                """, (tuple(station_id_list), min_packet_timestamp))

                for record in cursor:
                    if record:
                        result.append(self.get_object_from_record(record))

        return result

    def get_latest_object_by_station_id_and_position(self, station_id, latitude, longitude, map_id_list, symbol=None, symbol_table=None, min_timestamp=0):
        """Return a Packet object specified by station id and position."""
        packet_tables = self.packet_table_creator.get_tables(min_timestamp)

        with self.db.cursor() as cursor:
            for packet_table in reversed(packet_tables):
                cursor.execute(f"""
                    SELECT * FROM {packet_table}
                    WHERE station_id = %s
                        AND latitude = %s
                        AND longitude = %s
                        AND map_id IN %s
                        AND timestamp > %s
                        {f"AND symbol = %s" if symbol else ""}
                        {f"AND symbol_table = %s" if symbol_table else ""}
                    ORDER BY marker_id DESC, id DESC LIMIT 1
                """, (station_id, latitude, longitude, tuple(map_id_list), min_timestamp, symbol, symbol_table))

                record = cursor.fetchone()
                if record:
                    return self.get_object_from_record(record)

        return self.create()

    def get_latest_confirmed_moving_object_by_station_id(self, station_id, min_timestamp=0):
        """Return the latest confirmed moving Packet specified by station id."""
        packet_tables = self.packet_table_creator.get_tables(min_timestamp)

        with self.db.cursor() as cursor:
            for packet_table in reversed(packet_tables):
                cursor.execute(f"""
                    SELECT * FROM {packet_table}
                    WHERE station_id = %s
                        AND is_moving = 1
                        AND map_id = 1
                        AND timestamp > %s
                    ORDER BY marker_id DESC, id DESC LIMIT 1
                """, (station_id, min_timestamp))

                record = cursor.fetchone()
                if record:
                    return self.get_object_from_record(record)

        return self.create()

    def get_latest_moving_object_by_station_id(self, station_id, min_timestamp=0):
        """Return the latest moving Packet specified by station id."""
        packet_tables = self.packet_table_creator.get_tables(min_timestamp)

        with self.db.cursor() as cursor:
            for packet_table in reversed(packet_tables):
                cursor.execute(f"""
                    SELECT * FROM {packet_table} packet
                    WHERE station_id = %s
                        AND is_moving = 1
                        AND map_id IN (1, 7)
                        AND timestamp > %s
                    ORDER BY marker_id DESC, id DESC LIMIT 1
                """, (station_id, min_timestamp))

                record = cursor.fetchone()
                if record:
                    return self.get_object_from_record(record)

        return self.create()

    def get_latest_confirmed_object_by_station_id(self, station_id, min_timestamp=0):
        """Return the latest confirmed Packet object specified by station id."""
        with self.db.cursor() as cursor:
            cursor.execute("""
                SELECT * FROM station
                WHERE id = %s
            """, (station_id,))
            record = cursor.fetchone()

        if record and record["latest_confirmed_packet_timestamp"] is not None and record["latest_confirmed_packet_timestamp"] >= min_timestamp:
            return self.get_object_by_id_and_timestamp(record["latest_confirmed_packet_id"], record["latest_confirmed_packet_timestamp"])
        return self.create()

    def get_latest_object_by_station_id(self, station_id, min_timestamp=0):
        """Return the latest Packet specified by station id."""
        with self.db.cursor() as cursor:
            cursor.execute("""
                SELECT * FROM station
                WHERE id = %s
            """, (station_id,))
            record = cursor.fetchone()

        if record and record["latest_location_packet_timestamp"] is not None and record["latest_location_packet_timestamp"] >= min_timestamp:
            return self.get_object_by_id_and_timestamp(record["latest_location_packet_id"], record["latest_location_packet_timestamp"])
        return self.create()

    def get_most_recent_confirmed_object_list_by_station_id_list(self, station_id_list, min_timestamp):
        """Return an array of the most recent confirmed Packet objects specified by station ids."""
        if not station_id_list:
            return []

        result = []
        packet_tables = self.packet_table_creator.get_tables(min_timestamp)

        with self.db.cursor() as cursor:
            for packet_table in packet_tables:
                cursor.execute(f"""
                    SELECT * FROM {packet_table}
                    WHERE station_id IN %s
                        AND timestamp > %s
                        AND is_moving = 0
                        AND map_id = 1
                """, (tuple(station_id_list), min_timestamp))

                for record in cursor:
                    if record:
                        result.append(self.get_object_from_record(record))

            for station_id in station_id_list:
                packet = self.get_latest_confirmed_moving_object_by_station_id(station_id, min_timestamp)
                if packet.is_existing_object():
                    result.append(packet)

        return result

    def get_most_recent_confirmed_object_list_by_station_id_list_and_time_interval(self, station_id_list, min_timestamp, max_timestamp):
        """Return an array of the most recent confirmed Packet objects specified by station ids."""
        if not station_id_list:
            return []

        result = []
        found_stationary_marker_hash_list = []
        found_moving_marker_station_id_list = []
        packet_tables = self.packet_table_creator.get_tables(min_timestamp, max_timestamp)

        with self.db.cursor() as cursor:
            for packet_table in reversed(packet_tables):
                cursor.execute(f"""
                    SELECT * FROM {packet_table} packet
                    WHERE id IN (
                        SELECT MAX(id)
                        FROM {packet_table} packet
                        WHERE station_id IN %s
                            AND timestamp > %s
                            AND timestamp <= %s
                            AND is_moving = 0
                            AND map_id IN (1, 2, 12)
                        GROUP BY station_id, latitude, longitude, symbol, symbol_table
                    )
                """, (tuple(station_id_list), min_timestamp, max_timestamp))

                for record in cursor:
                    if record:
                        marker_hash = hash(f"{record['station_id']};{record['latitude']};{record['longitude']};{record['symbol']};{record['symbol_table']}")
                        if marker_hash not in found_stationary_marker_hash_list:
                            found_stationary_marker_hash_list.append(marker_hash)
                            result.append(self.get_object_from_record(record))

                cursor.execute(f"""
                    SELECT packet.* FROM {packet_table} packet
                    WHERE id IN (
                        SELECT MAX(id)
                        FROM {packet_table} packet
                        WHERE station_id IN %s
                            AND map_id IN (1, 2, 12)
                            AND timestamp > %s
                            AND timestamp <= %s
                            AND is_moving = 1
                        GROUP BY station_id
                    )
                """, (tuple(station_id_list), min_timestamp, max_timestamp))

                for record in cursor:
                    if record and record['station_id'] not in found_moving_marker_station_id_list:
                        found_moving_marker_station_id_list.append(record['station_id'])
                        result.append(self.get_object_from_record(record))

        return result

    def get_latest_confirmed_object_list_by_station_id_list(self, station_id_list, min_timestamp=0):
        """Return an array of the latest confirmed Packet objects specified by station ids."""
        if not station_id_list:
            return []

        result = []
        if min_timestamp == 0:
            for station_id in station_id_list:
                packet = self.get_latest_confirmed_object_by_station_id(station_id)
                if packet.is_existing_object():
                    result.append(packet)
        else:
            packet_tables = self.packet_table_creator.get_tables(min_timestamp)

            with self.db.cursor() as cursor:
                for packet_table in reversed(packet_tables):
                    cursor.execute(f"""
                        SELECT packet.* FROM {packet_table} packet, station
                        WHERE station.id IN %s
                            AND station.latest_confirmed_packet_id = packet.id
                            AND station.latest_confirmed_packet_timestamp = packet.timestamp
                            AND station.latest_confirmed_packet_timestamp > %s
                        ORDER BY packet.marker_id, packet.id
                    """, (tuple(station_id_list), min_timestamp))

                    for record in cursor:
                        if record:
                            result.append(self.get_object_from_record(record))

                    if len(result) >= len(station_id_list):
                        break

        return result

    def get_latest_object_list_by_station_id_list(self, station_id_list, min_timestamp=0):
        """Return an array of the latest Packet objects specified by station ids."""
        if not station_id_list:
            return []

        result = []
        if min_timestamp == 0:
            for station_id in station_id_list:
                packet = self.get_latest_object_by_station_id(station_id)
                if packet.is_existing_object():
                    result.append(packet)
        else:
            packet_tables = self.packet_table_creator.get_tables(min_timestamp)

            with self.db.cursor() as cursor:
                for packet_table in reversed(packet_tables):
                    cursor.execute(f"""
                        SELECT packet.* FROM {packet_table} packet, station
                        WHERE station.id IN %s
                            AND station.latest_location_packet_id = packet.id
                            AND station.latest_confirmed_packet_timestamp = packet.timestamp
                            AND station.latest_location_packet_timestamp > %s
                    """, (tuple(station_id_list), min_timestamp))

                    for record in cursor:
                        if record:
                            result.append(self.get_object_from_record(record))

                    if len(result) >= len(station_id_list):
                        break

        return result

    def get_object_from_record(self, record):
        """Return a Packet object from a database record."""
        db_object = self.create()
        if record:
            db_object.id = record["id"]
            db_object.station_id = int(record["station_id"])
            db_object.sender_id = int(record["sender_id"])
            db_object.packet_type_id = record["packet_type_id"]
            db_object.timestamp = int(record["timestamp"])
            db_object.latitude = float(record["latitude"]) if record["latitude"] is not None else None
            db_object.longitude = float(record["longitude"]) if record["longitude"] is not None else None
            db_object.posambiguity = record['posambiguity']
            db_object.symbol = record["symbol"]
            db_object.symbol_table = record["symbol_table"]
            db_object.map_sector = record["map_sector"]
            db_object.related_map_sectors = record["related_map_sectors"]
            db_object.map_id = record["map_id"]
            db_object.source_id = record["source_id"]
            db_object.marker_id = record["marker_id"]
            db_object.speed = record["speed"]
            db_object.course = record["course"]
            db_object.altitude = record["altitude"]
            db_object.is_moving = record['is_moving']
            db_object.reported_timestamp = int(record["reported_timestamp"]) if record["reported_timestamp"] is not None else None
            db_object.position_timestamp = int(record["position_timestamp"]) if record["position_timestamp"] is not None else None
            db_object.packet_tail_timestamp = record.get('packet_tail_timestamp', db_object.timestamp)
            db_object.marker_counter = record.get('marker_counter', 1)
            db_object.comment = record.get('comment')
            db_object.raw_path = record.get('raw_path')
            db_object.raw = record.get('raw')
            db_object.phg = record.get('phg')
            db_object.rng = record.get('rng')
            db_object.latest_phg_timestamp = record.get('latest_phg_timestamp')
            db_object.latest_rng_timestamp = record.get('latest_rng_timestamp')
        return db_object

    def create(self):
        """Create an empty Packet."""
        return Packet(self.db)