import logging
from twisted.python import log
import datetime
import time


class DatabaseObjectFinder():
    """The DatabaseObjectFinder class can be used to check if a database table exists or not
    """

    existingTables = {}

    def __init__(self, db):
        """The __init__ method.

        Args:
            db (psycopg2.Connection):  Database connection
        """
        self.db = db

    def setTableExists(self, tablename):
        """Mark a table as existing

        Args:
            tablename (str):  table to be marked as existing
        """
        DatabaseObjectFinder.existingTables[tablename] = True

    def checkTableExists(self, tablename):
        """Returns true if specified table exists in database

        Args:
            tablename (str):       Table that we want's to know if it exists or not

        Returns:
            Returns true if specified table exists in database otherwise false
        """
        todayDateStr = datetime.datetime.utcfromtimestamp(
            int(time.time())).strftime('%Y%m%d')
        yesterdayDateStr = datetime.datetime.utcfromtimestamp(
            int(time.time()) - 86400).strftime('%Y%m%d')

        if (todayDateStr in tablename or yesterdayDateStr in tablename):
            # We only trust cache for the latest two days
            if (tablename in DatabaseObjectFinder.existingTables):
                # we know table exists
                return True

        cur = self.db.cursor()
        cur.execute("""
            SELECT COUNT(*)
            FROM information_schema.tables
            WHERE table_name = '{0}'
            """.format(tablename.replace('\'', '\'\'')))
        if cur.fetchone()[0] == 1:
            DatabaseObjectFinder.existingTables[tablename] = True
            cur.close()
            return True
        else:
            cur.close()
            return False

    def checkIndexExists(self, index):
        """Returns true if specified index exists in database

        Args:
            index (str): index that we want's to know if it exists or not

        Returns:
            Returns true if specified index exists in database otherwise false
        """
        cur = self.db.cursor()
        cur.execute("""select to_regclass('{0}') \"name\"""".format(
            index.replace('\'', '\'\'')))
        record = cur.fetchone()
        if record and record['name'] == index.replace('\'', '\'\''):
            cur.close()
            return True
        else:
            cur.close()
            return False
