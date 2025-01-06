import logging
import psycopg2
import psycopg2.extras
import datetime
import time
import calendar
from server.trackdirect.database.DatabaseObjectFinder import DatabaseObjectFinder
from server.trackdirect.exceptions.TrackDirectMissingTableError import TrackDirectMissingTableError


class PacketTableCreator:
    """The PacketTableCreator class handles packet table name logic.

    Note:
        Packets are stored in different tables depending on what day they are received,
        new packet tables are created by this class.
    """

    def __init__(self, db: psycopg2.extensions.connection):
        """The __init__ method.

        Args:
            db (psycopg2.extensions.connection): Database connection
        """
        self.db = db
        self.dbObjectFinder = DatabaseObjectFinder(db)
        self.logger = logging.getLogger('trackdirect')
        self.createIfMissing = True

    def disable_create_if_missing(self) -> None:
        """Disable feature that creates new tables if missing."""
        self.createIfMissing = False

    def enable_create_if_missing(self) -> None:
        """Enable feature that creates new tables if missing."""
        self.createIfMissing = True

    def get_table(self, timestamp: int) -> str:
        """Returns the name of the packet table.

        Args:
            timestamp (int): Unix timestamp that we need the table for

        Returns:
            str: The name of the packet table
        """
        date = datetime.datetime.utcfromtimestamp(timestamp).strftime('%Y%m%d')
        packet_table = f'packet{date}'

        if not self.dbObjectFinder.check_table_exists(packet_table):
            if self.createIfMissing:
                min_timestamp = timestamp // (24 * 60 * 60) * (24 * 60 * 60)
                max_timestamp = min_timestamp + (24 * 60 * 60)
                self._create_packet_table(packet_table, min_timestamp, max_timestamp)
                self.dbObjectFinder.set_table_exists(packet_table)
            else:
                raise TrackDirectMissingTableError(f'Database table {packet_table} does not exist')

        return packet_table

    def get_tables(self, start_timestamp: int, end_timestamp: int = None) -> list[str]:
        """Returns an array of packet table names based on the specified timestamp range.

        Note:
            If table does not exist we will not include the packet table name in array.

        Args:
            start_timestamp (int): Start unix timestamp for requested packet tables
            end_timestamp (int): End unix timestamp for requested packet tables

        Returns:
            list[str]: Array of packet table names
        """
        if end_timestamp is None:
            end_timestamp = int(time.time())

        end_date_time = datetime.datetime.utcfromtimestamp(end_timestamp)
        end_date_time = end_date_time.replace(hour=0, minute=0, second=0, microsecond=0) + datetime.timedelta(days=1)
        end_timestamp = calendar.timegm(end_date_time.timetuple())

        result = []
        ts = start_timestamp if start_timestamp is not None and start_timestamp != 0 else int(time.time()) - (60 * 60 * 24 * 366)

        while ts < end_timestamp:
            date = datetime.datetime.utcfromtimestamp(ts).strftime('%Y%m%d')
            date_packet_table = f'packet{date}'
            if self.dbObjectFinder.check_table_exists(date_packet_table):
                result.append(date_packet_table)
            ts += 86400  # 1 day in seconds

        return result

    def _create_packet_table(self, table_name: str, min_timestamp: int, max_timestamp: int) -> None:
        """Create a packet table with the specified name.

        Args:
            table_name (str): Name of the packet table to create
            min_timestamp (int): Min Unix timestamp for this table
            max_timestamp (int): Max Unix timestamp for this table
        """
        try:
            cur = self.db.cursor()
            sql_statements = [
                f"CREATE TABLE {table_name} () INHERITS (packet)",
                f"ALTER TABLE {table_name} ADD CONSTRAINT timestamp_range_check CHECK (timestamp >= {min_timestamp} AND timestamp < {max_timestamp})",
                f"CREATE INDEX {table_name}_pkey ON {table_name} USING btree (id)",
                f"CREATE INDEX {table_name}_station_id_idx ON {table_name} (station_id, map_id, marker_id, timestamp)",
                f"CREATE INDEX {table_name}_map_sector_idx ON {table_name} (map_sector, timestamp, map_id)",
                f"CREATE INDEX {table_name}_sender_id_idx ON {table_name} (sender_id)"
            ]

            for sql in sql_statements:
                cur.execute(sql)

            cur.close()

        except (psycopg2.IntegrityError, psycopg2.ProgrammingError) as e:
            if 'already exists' not in str(e):
                self.logger.error(e, exc_info=1)
            time.sleep(10)

        except Exception as e:
            self.logger.error(e, exc_info=1)
            time.sleep(10)