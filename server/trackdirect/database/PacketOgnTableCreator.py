import logging
import psycopg2
import psycopg2.extras
import datetime
import time
from server.trackdirect.database.DatabaseObjectFinder import DatabaseObjectFinder
from server.trackdirect.exceptions.TrackDirectMissingTableError import TrackDirectMissingTableError


class PacketOgnTableCreator:
    """The PacketOgnTableCreator class handles packet OGN table name logic

    Note:
        Packets are stored in different tables depending on what day they are received,
        new packet tables are created by this class.
    """

    def __init__(self, db):
        """The __init__ method.

        Args:
            db (psycopg2.Connection): Database connection
        """
        self.db = db
        self.dbObjectFinder = DatabaseObjectFinder(db)
        self.logger = logging.getLogger('trackdirect')
        self.createIfMissing = True

    def disable_create_if_missing(self):
        """Disable feature that creates new tables if missing
        """
        self.createIfMissing = False

    def get_table(self, packet_timestamp):
        """Returns the name of the OGN packet table

        Args:
            packet_timestamp (int): Unix timestamp that we need the table for

        Returns:
            the name of the OGN packet table as a string
        """
        date = datetime.datetime.utcfromtimestamp(packet_timestamp).strftime('%Y%m%d')
        packet_ogn_table = f'packet{date}_ogn'
        if not self.dbObjectFinder.check_table_exists(packet_ogn_table):
            if self.createIfMissing:
                min_timestamp = packet_timestamp // (24 * 60 * 60) * (24 * 60 * 60)
                max_timestamp = min_timestamp + (24 * 60 * 60)
                self._create_table(packet_ogn_table, min_timestamp, max_timestamp)
                self.dbObjectFinder.set_table_exists(packet_ogn_table)
            else:
                raise TrackDirectMissingTableError('Database table does not exist')
        return packet_ogn_table

    def _create_table(self, table_name, min_timestamp, max_timestamp):
        """Create a packet OGN table with the specified name

        Args:
            table_name (str):        Name of the packet OGN table to create
            min_timestamp (int):     Min Unix timestamp for this table
            max_timestamp (int):     Max Unix timestamp for this table
        """
        try:
            cur = self.db.cursor()
            sql_statements = [
                f"CREATE TABLE {table_name} () INHERITS (packet_ogn)",
                f"ALTER TABLE {table_name} ADD CONSTRAINT timestamp_range_check CHECK (timestamp >= {min_timestamp} AND timestamp < {max_timestamp})",
                f"CREATE INDEX {table_name}_pkey ON {table_name} USING btree (id)",
                f"CREATE INDEX {table_name}_packet_id_idx ON {table_name} (packet_id)",
                f"CREATE INDEX {table_name}_station_id_idx ON {table_name} (station_id, timestamp)"
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