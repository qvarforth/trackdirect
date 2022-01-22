import datetime, time, calendar
from trackdirect.database.DatabaseObjectFinder import DatabaseObjectFinder


class StationIdByMapSectorQuery() :
    """A query class used to find station ids in a map sector
    """

    def __init__(self, db) :
        """The __init__ method.

        Args:
            db (psycopg2.Connection): Database connection
        """
        self.db = db
        self.dbObjectFinder = DatabaseObjectFinder(db)

    def getStationIdListByMapSector(self, mapSector, startPacketTimestamp, endPacketTimestamp) :
        """Returns a list station ids  based on the specified map sector and time interval

        Args:
            mapSector (int):                    Map sector integer
            startPacketTimestamp (int):         Min unix timestamp
            endPacketTimestamp (int):           Max unix timestamp

        Returns:
            array
        """
        result = {}
        selectCursor = self.db.cursor()

        # Create list of packet tables to look in
        # After testing I have realized that this query is faster if you query one child table at the time

        if (endPacketTimestamp is None):
            endPacketTimestamp = int(time.time())
        endDateTime = datetime.datetime.utcfromtimestamp(int(endPacketTimestamp))
        endDateTime = endDateTime.replace(hour=0, minute=0, second=0, microsecond=0) + datetime.timedelta(days=1)
        endTimestamp = calendar.timegm(endDateTime.timetuple())

        packetTables = []
        ts = startPacketTimestamp
        while (ts < endTimestamp) :
            date = datetime.datetime.utcfromtimestamp(int(ts)).strftime('%Y%m%d')
            datePacketTable = 'packet' + date
            if (self.dbObjectFinder.checkTableExists(datePacketTable)) :
                packetTables.append(datePacketTable)
            ts = ts + 86400 # 1 day in seconds

        # Go through packet tables and search for stations
        for packetTable in reversed(packetTables) :
            sql1 = selectCursor.mogrify("""select distinct station_id id
                from """ + packetTable + """
                where map_sector = %s
                    and timestamp > %s
                    and timestamp <= %s
                    and map_id in (1,5,7,9)""", (mapSector, startPacketTimestamp, endPacketTimestamp))

            selectCursor.execute(sql1)
            for record in selectCursor :
                if (record is not None) :
                    result[int(record["id"])] = True

            sql2 = selectCursor.mogrify("""select distinct station_id id
                from """ + packetTable + """
                where map_sector = %s
                    and position_timestamp <= %s
                    and timestamp > %s
                    and map_id in (12)""", (mapSector, endPacketTimestamp, startPacketTimestamp))

            selectCursor.execute(sql2)
            for record in selectCursor :
                if (record is not None) :
                    result[int(record["id"])] = True

        selectCursor.close()
        return list(result.keys())