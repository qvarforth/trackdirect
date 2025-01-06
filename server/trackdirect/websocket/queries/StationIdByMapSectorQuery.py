import datetime, time, calendar
from server.trackdirect.database.DatabaseObjectFinder import DatabaseObjectFinder


class StationIdByMapSectorQuery:
    """A query class used to find station ids in a map sector."""

    def __init__(self, db):
        """The __init__ method.

        Args:
            db (psycopg2.Connection): Database connection
        """
        self.db = db
        self.db_object_finder = DatabaseObjectFinder(db)

    def get_station_id_list_by_map_sector(self, map_sector, start_packet_timestamp, end_packet_timestamp):
        """Returns a list of station ids based on the specified map sector and time interval.

        Args:
            map_sector (int): Map sector integer
            start_packet_timestamp (int): Min unix timestamp
            end_packet_timestamp (int): Max unix timestamp

        Returns:
            list: List of station ids
        """
        result = {}

        if end_packet_timestamp is None:
            end_packet_timestamp = int(time.time())
        end_date_time = datetime.datetime.utcfromtimestamp(int(end_packet_timestamp))
        end_date_time = end_date_time.replace(hour=0, minute=0, second=0, microsecond=0) + datetime.timedelta(days=1)
        end_timestamp = calendar.timegm(end_date_time.timetuple())

        packet_tables = [
            f'packet{datetime.datetime.utcfromtimestamp(ts).strftime("%Y%m%d")}'
            for ts in range(start_packet_timestamp, end_timestamp, 86400)
            if self.db_object_finder.check_table_exists(f'packet{datetime.datetime.utcfromtimestamp(ts).strftime("%Y%m%d")}')
        ]

        # Go through packet tables and search for stations
        with self.db.cursor() as select_cursor:
            for packet_table in reversed(packet_tables):
                sql1 = f"""
                    SELECT DISTINCT station_id AS id
                    FROM {packet_table}
                    WHERE map_sector = %s
                        AND timestamp > %s
                        AND timestamp <= %s
                        AND map_id IN (1, 5, 7, 9)
                """.format(packet_table)
                select_cursor.execute(sql1, (map_sector, start_packet_timestamp, end_packet_timestamp))
                for record in select_cursor:
                    if record is not None:
                        result[int(record["id"])] = True

                sql2 = f"""
                    SELECT DISTINCT station_id AS id
                    FROM {packet_table}
                    WHERE map_sector = %s
                        AND position_timestamp <= %s
                        AND timestamp > %s
                        AND map_id IN (12)
                """.format(packet_table)
                select_cursor.execute(sql2, (map_sector, end_packet_timestamp, start_packet_timestamp))
                for record in select_cursor:
                    if record is not None:
                        result[int(record["id"])] = True

        return list(result.keys())