import logging
from twisted.python import log
import psycopg2
import psycopg2.extras
import datetime
import time
import calendar

from trackdirect.database.DatabaseObjectFinder import DatabaseObjectFinder
from trackdirect.exceptions.TrackDirectMissingTableError import TrackDirectMissingTableError


class PacketTableCreator():
    """The PacketTableCreator class handles packet table name logic

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

    def enableCreateIfMissing(self):
        """Enable feature that creates new tables if missing
        """
        self.createIfMissing = True

    def getPacketTable(self, packetTimestamp):
        """Returns the name of the packet table

        Args:
            packetTimestamp (int): Unix timestamp that we need the table for

        Returns:
            Returns the name of the packet table as a string
        """
        date = datetime.datetime.utcfromtimestamp(
            packetTimestamp).strftime('%Y%m%d')
        packetTable = 'packet' + date
        if (not self.dbObjectFinder.checkTableExists(packetTable)):
            if(self.createIfMissing):
                minTimestamp = packetTimestamp // (24*60*60) * (24*60*60)
                maxTimestamp = minTimestamp + (24*60*60)
                self._createPacketTable(
                    packetTable, minTimestamp, maxTimestamp)
                self.dbObjectFinder.setTableExists(packetTable)
            else:
                raise TrackDirectMissingTableError(
                    'Database table ' + packetTable + ' does not exists')
        return packetTable

    def getPacketTables(self, startTimestamp, endTimestamp=None):
        """Returns an array of packet table names based on the specified timestamp range

        Note:
            If table does not exist we will not include the packet table name in array

        Args:
            startTimestamp (int):  Start unix timestamp for requested packet tables
            endTimestamp (int):    End unix timestamp for requested packet tables

        Returns:
            Array of packet table names
        """
        if (endTimestamp is None):
            endTimestamp = int(time.time())

        # We allways want to include
        endDateTime = datetime.datetime.utcfromtimestamp(int(endTimestamp))
        endDateTime = endDateTime.replace(
            hour=0, minute=0, second=0, microsecond=0) + datetime.timedelta(days=1)
        endTimestamp = calendar.timegm(endDateTime.timetuple())

        result = []
        if (startTimestamp == 0):
            # Go back 1 year
            ts = int(time.time()) - (60*60*24*366)
        else:
            ts = startTimestamp
        while (ts < endTimestamp):
            date = datetime.datetime.utcfromtimestamp(
                int(ts)).strftime('%Y%m%d')
            datePacketTable = 'packet' + date
            if (self.dbObjectFinder.checkTableExists(datePacketTable)):
                result.append(datePacketTable)

            ts = ts + 86400  # 1 day in seconds
        return result

    def _createPacketTable(self, tablename, minTimestamp, maxTimestamp):
        """Create a packet table with the specified name

        Args:
            tablename (str): Name of the packet table to create
            minTimestamp (int):     Min Unix timestamp for this table
            maxTimestamp (int):     Max Unix timestamp for this table
        """
        try:
            cur = self.db.cursor()
            sql = """
                create table %s () inherits (packet)""" % (tablename)
            cur.execute(sql)

            sql = """alter table %s add constraint timestamp_range_check check(timestamp >= %d and timestamp < %d)""" % (tablename, minTimestamp, maxTimestamp)
            cur.execute(sql)

            # The regular primary key index
            sql = """create index %s_pkey on %s using btree (id)""" % (
                tablename, tablename)
            cur.execute(sql)

            # This index is magic for multiple methods in PacketRepository
            sql = """create index %s_station_id_idx on %s(station_id, map_id, marker_id, timestamp)""" % (
                tablename, tablename)
            cur.execute(sql)

            # This should be good when using the time-travel functionality
            sql = """create index %s_map_sector_idx on %s(map_sector, timestamp, map_id)""" % (
                tablename, tablename)
            cur.execute(sql)

            # Used by remover
            sql = """create index %s_sender_id_idx on %s(sender_id)""" % (
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
