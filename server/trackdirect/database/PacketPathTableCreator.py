import logging
from twisted.python import log
import psycopg2
import psycopg2.extras
import datetime
import time
import calendar

from trackdirect.database.DatabaseObjectFinder import DatabaseObjectFinder
from trackdirect.exceptions.TrackDirectMissingTableError import TrackDirectMissingTableError


class PacketPathTableCreator():
    """The PacketPathTableCreator class handles packet table name logic

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

    def disableCreateIfMissing(self):
        """Disable feature that creates new tables if missing
        """
        self.createIfMissing = False

    def getPacketPathTable(self, packetTimestamp):
        """Returns the name of the path packet table

        Args:
            packetTimestamp (int): Unix timestamp that we need the table for

        Returns:
            Returns the name of the path packet table as a string
        """
        date = datetime.datetime.utcfromtimestamp(
            packetTimestamp).strftime('%Y%m%d')
        packetTable = 'packet' + date
        packetPathTable = 'packet' + date + '_path'
        if (not self.dbObjectFinder.checkTableExists(packetPathTable)):
            if(self.createIfMissing):
                minTimestamp = packetTimestamp // (24*60*60) * (24*60*60)
                maxTimestamp = minTimestamp + (24*60*60)
                self._createPacketPathTable(
                    packetPathTable, minTimestamp, maxTimestamp)
                self.dbObjectFinder.setTableExists(packetPathTable)
            else:
                raise TrackDirectMissingTableError(
                    'Database table does not exists')
        return packetPathTable

    def _createPacketPathTable(self, tablename, minTimestamp, maxTimestamp):
        """Create a packet path table with the specified name

        Args:
            tablename (str):        Name of the packet path table to create
            minTimestamp (int):     Min Unix timestamp for this table
            maxTimestamp (int):     Max Unix timestamp for this table
        """
        try:
            cur = self.db.cursor()
            sql = """
                create table %s () inherits (packet_path)""" % (tablename)
            cur.execute(sql)

            sql = """alter table %s add constraint timestamp_range_check check(timestamp >= %d and timestamp < %d)""" % (tablename, minTimestamp, maxTimestamp)
            cur.execute(sql)

            sql = """create index %s_pkey on %s using btree (id)""" % (
                tablename, tablename)
            cur.execute(sql)

            sql = """create index %s_packet_id_idx on %s(packet_id, number)""" % (
                tablename, tablename)
            cur.execute(sql)

            sql = """create index %s_station_id_idx on %s(station_id, timestamp)""" % (
                tablename, tablename)
            cur.execute(sql)

            sql = """create index %s_sending_station_id_idx on %s(sending_station_id, timestamp)""" % (
                tablename, tablename)
            cur.execute(sql)

            cur.close()

        except (psycopg2.IntegrityError, psycopg2.ProgrammingError) as e:
            # Probably the other collector created the table at the same time (might happen when you run multiple collectors), just go on...
            if ('already exists' not in str(e)):
                self.logger.error(e, exc_info=1)

            # Do some sleep and let the other process create all related tables (if other table failes we will do it after sleep)
            time.sleep(10)
            return

        except Exception as e:
            self.logger.error(e, exc_info=1)

            # Do some sleep and let the other process create all related tables (if other table failes we will do it after sleep)
            time.sleep(10)
            return
