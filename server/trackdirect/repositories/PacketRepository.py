
from trackdirect.common.Repository import Repository
from trackdirect.objects.Packet import Packet
from trackdirect.database.PacketTableCreator import PacketTableCreator
from trackdirect.exceptions.TrackDirectMissingTableError import TrackDirectMissingTableError
from trackdirect.database.DatabaseObjectFinder import DatabaseObjectFinder


class PacketRepository(Repository):
    """The PacketRepository class contains different method that creates Packet instances
    """

    def __init__(self, db):
        """The __init__ method.

        Args:
            db (psycopg2.Connection):  Database connection (with autocommit)
        """
        self.db = db

        # After testing I have realized that several queries are faster if you query one packet child at the time
        # That is why we are using packetTableCreator to fetch childtables instead of using the parent packet table
        self.packetTableCreator = PacketTableCreator(self.db)
        self.packetTableCreator.disableCreateIfMissing()
        self.dbObjectFinder = DatabaseObjectFinder(db)

    def getObjectById(self, id):
        """The getObjectById method is supposed to return an object based on the specified id in database

        Args:
            id (int):  Database row id

        Returns:
            Packet
        """
        selectCursor = self.db.cursor()
        selectCursor.execute("""select * from packet where id = %s""", (id,))
        record = selectCursor.fetchone()
        selectCursor.close()
        return self.getObjectFromRecord(record)

    def getObjectByIdAndTimestamp(self, id, timestamp):
        """Returns an object based on the specified id in database

        Args:
            id (int):         Database row id
            timestamp (int):  Unix timestamp for requested packet

        Returns:
            Packet
        """
        try:
            packetTable = self.packetTableCreator.getPacketTable(timestamp)
        except TrackDirectMissingTableError as e:
            return Packet(self.db)

        selectCursor = self.db.cursor()
        selectCursor.execute("""select * from """ +
                             packetTable + """ where id = %s""", (id,))
        record = selectCursor.fetchone()
        selectCursor.close()
        return self.getObjectFromRecord(record)

    def getObjectByStationIdAndTimestamp(self, stationId, timestamp):
        """Returns an object based on the specified stationId in database

        Args:
            stationId (int):  Station id
            timestamp (int):  Unix timestamp for requested packet

        Returns:
            Packet
        """
        try:
            packetTable = self.packetTableCreator.getPacketTable(timestamp)
            selectCursor = self.db.cursor()
            selectCursor.execute("""select * from """ + packetTable +
                                 """ where station_id = %s and timestamp = %s order by id limit 1""", (stationId, timestamp, ))
            record = selectCursor.fetchone()

            selectCursor.close()
            return self.getObjectFromRecord(record)
        except TrackDirectMissingTableError as e:
            return self.create()

    def getLatestObjectListByStationIdListAndTimeInterval(self, stationIdList, minPacketTimestamp, maxPacketTimestamp, onlyConfirmed=True):
        """Returns an array of Packet's specified by station id's
        Args:
            stationIdList (array):     Station id's to look for
            minPacketTimestamp (int):  Min requested unix timestamp
            maxPacketTimestamp (int):  Max requested unix timestamp

        Returns:
            Array
        """
        if (len(stationIdList) == 0):
            return []

        selectCursor = self.db.cursor()
        result = []
        foundStationIdList = []
        packetTables = self.packetTableCreator.getPacketTables(
            minPacketTimestamp, maxPacketTimestamp)
        mapIdList = [1, 2, 12]
        if (not onlyConfirmed):
            mapIdList = [1, 2, 5, 7, 9, 12]

        for packetTable in reversed(packetTables):
            stationIdListToFind = tuple(
                list(set(stationIdList) - set(foundStationIdList)))

            if (len(stationIdListToFind) > 0):
                sql1 = selectCursor.mogrify("""select *
                    from """ + packetTable + """ packet
                    where id in (
                        select max(id)
                        from """ + packetTable + """ packet
                        where map_id in %s
                            and station_id in %s
                            and timestamp > %s
                            and timestamp <= %s
                        group by station_id
                    )
                    order by packet.marker_id desc, packet.id desc""", (tuple(mapIdList), tuple(stationIdListToFind), int(minPacketTimestamp), int(maxPacketTimestamp)))
                # Sort by marker_id first and packet as second, otherwise client might render it wrong

                selectCursor.execute(sql1)
                for record in selectCursor:
                    if (record is not None):
                        if (record['station_id'] not in foundStationIdList):
                            dbObject = self.getObjectFromRecord(record)
                            result.append(dbObject)
                            foundStationIdList.append(record['station_id'])
            if (len(foundStationIdList) >= len(stationIdList)):
                break

        if (len(foundStationIdList) < len(stationIdList)):
            for packetTable in reversed(packetTables):
                stationIdListToFind = tuple(
                    list(set(stationIdList) - set(foundStationIdList)))

                if (len(stationIdListToFind) > 0):
                    sql2 = selectCursor.mogrify("""select *
                        from """ + packetTable + """ packet
                        where map_id = 12
                            and station_id in %s
                            and position_timestamp <= %s
                            and timestamp > %s
                        order by packet.marker_id desc, packet.id desc""", (tuple(stationIdListToFind), int(maxPacketTimestamp), int(minPacketTimestamp)))
                    # Sort by marker_id first and packet as second, otherwise client might render it wrong

                    selectCursor.execute(sql2)
                    for record in selectCursor:
                        if (record is not None):
                            if (record['station_id'] not in foundStationIdList):
                                dbObject = self.getObjectFromRecord(record)
                                result.append(dbObject)
                                foundStationIdList.append(record['station_id'])

                if (len(foundStationIdList) >= len(stationIdList)):
                    break

        selectCursor.close()
        return result

    def getObjectListByStationIdListAndTimeInterval(self, stationIdList, minPacketTimestamp, maxPacketTimestamp):
        """Returns an array of Packet's specified by station id's
        Args:
            stationIdList (array):     Station id's to look for
            minPacketTimestamp (int):  Min requested unix timestamp
            maxPacketTimestamp (int):  Max requested unix timestamp

        Returns:
            Array
        """
        if (len(stationIdList) == 0):
            return []

        selectCursor = self.db.cursor()

        result = []
        packetTables = self.packetTableCreator.getPacketTables(
            minPacketTimestamp, maxPacketTimestamp)

        for packetTable in packetTables:
            sql1 = selectCursor.mogrify("""select *
                from """ + packetTable + """ packet
                where map_id in (1,2,5,7,9,12)
                    and station_id in %s
                    and timestamp > %s
                    and timestamp <= %s
                order by packet.marker_id, packet.id""", (tuple(stationIdList), int(minPacketTimestamp), int(maxPacketTimestamp)))
            # Sort by marker_id first and packet as second, otherwise client might render it wrong

            selectCursor.execute(sql1)
            for record in selectCursor:
                if (record is not None):
                    dbObject = self.getObjectFromRecord(record)
                    result.append(dbObject)

            # Also add packets that has been replace but where position_timestamp was in or before period
            sql2 = selectCursor.mogrify("""select *
                from """ + packetTable + """ packet
                where map_id = 12
                    and station_id in %s
                    and position_timestamp <= %s
                    and timestamp > %s
                order by packet.marker_id, packet.id""", (tuple(stationIdList), int(maxPacketTimestamp), int(maxPacketTimestamp)))
            # Sort by marker_id first and packet as second, otherwise client might render it wrong

            selectCursor.execute(sql2)
            for record in selectCursor:
                if (record is not None):
                    dbObject = self.getObjectFromRecord(record)
                    result.append(dbObject)

        selectCursor.close()
        return result

    def getObjectListByStationIdList(self, stationIdList, minPacketTimestamp):
        """Returns an array of Packet's specified by station id's
        Args:
            stationIdList (array):     Station id's to look for
            minPacketTimestamp (int):  Min requested unix timestamp

        Returns:
            Array
        """
        if (len(stationIdList) == 0):
            return []
        selectCursor = self.db.cursor()
        result = []

        packetTables = self.packetTableCreator.getPacketTables(
            minPacketTimestamp)
        for packetTable in packetTables:
            sql = selectCursor.mogrify("""select *
                from """ + packetTable + """ packet
                where map_id in (1,5,7,9)
                    and station_id in %s""", (tuple(stationIdList),))

            if (minPacketTimestamp != 0):
                sql = sql + \
                    selectCursor.mogrify(
                        """ and timestamp > %s""", (int(minPacketTimestamp),))

            sql = sql + \
                selectCursor.mogrify(
                    """ order by packet.marker_id, packet.id""")
            # Sort by marker_id first and packet as second, otherwise client might render it wrong
            selectCursor.execute(sql)

            for record in selectCursor:
                if (record is not None):
                    dbObject = self.getObjectFromRecord(record)
                    result.append(dbObject)
        selectCursor.close()
        return result

    def getLatestObjectByStationIdAndPosition(self, stationId, latitude, longitude, mapIdList, symbol=None, symbolTable=None, minTimestamp=0):
        """Returns a packet object specified by station id and position (and map id, symbol and symbol table)
        Args:
            stationId (int):     Station id to look for
            latitude (double):   Latitude
            longitude (double):  Longitude
            mapIdList (int):     Array of map id's to look for
            symbol (str):        Symbol char
            symbolTable (str):   Symbol table char
            minTimestamp (int):  Min requested unix timestamp

        Returns:
            Packet
        """
        selectCursor = self.db.cursor()
        packetTables = self.packetTableCreator.getPacketTables(minTimestamp)
        for packetTable in reversed(packetTables):
            sql = selectCursor.mogrify("""select *
                from """ + packetTable + """
                where station_id = %s
                    and latitude = %s
                    and longitude = %s
                    and map_id in %s""", (stationId, latitude, longitude, tuple(mapIdList),))

            if (minTimestamp != 0):
                sql = sql + \
                    selectCursor.mogrify(
                        """ and timestamp > %s""", (int(minTimestamp),))

            if (symbol is not None):
                sql = sql + \
                    selectCursor.mogrify(""" and symbol = %s""", (symbol,))

            if (symbolTable is not None):
                sql = sql + \
                    selectCursor.mogrify(
                        """ and symbol_table = %s""", (symbolTable,))

            sql = sql + \
                selectCursor.mogrify(
                    """ order by marker_id desc, id desc limit 1""")
            # Sort by marker_id first and packet as second, otherwise client might render it wrong

            selectCursor.execute(sql)
            record = selectCursor.fetchone()

            if (record is not None):
                selectCursor.close()
                return self.getObjectFromRecord(record)
        selectCursor.close()
        return self.create()

    def getLatestConfirmedMovingObjectByStationId(self, stationId, minTimestamp=0):
        """Returns the latest confirmed moving Packet specified by station id
        Args:
            stationId (int):     Station id to look for
            minTimestamp (int):  Min requested unix timestamp

        Returns:
            Packet
        """
        selectCursor = self.db.cursor()
        packetTables = self.packetTableCreator.getPacketTables(minTimestamp)
        for packetTable in reversed(packetTables):
            sql = selectCursor.mogrify("""select *
                from """ + packetTable + """
                where station_id = %s
                    and is_moving = 1
                    and map_id = 1""", (stationId,))

            if (minTimestamp != 0):
                sql = sql + \
                    selectCursor.mogrify(
                        """ and timestamp > %s""", (int(minTimestamp),))

            sql = sql + \
                selectCursor.mogrify(
                    """ order by marker_id desc, id desc limit 1""")
            # Sort by marker_id first and packet as second, otherwise client might render it wrong

            selectCursor.execute(sql)
            record = selectCursor.fetchone()

            if (record is not None):
                selectCursor.close()
                return self.getObjectFromRecord(record)
        selectCursor.close()
        return self.create()

    def getLatestMovingObjectByStationId(self, stationId, minTimestamp=0):
        """Returns the latest moving Packet specified by station id
        Args:
            stationId (int):     Station id to look for
            minTimestamp (int):  Min requested unix timestamp

        Returns:
            Packet
        """
        selectCursor = self.db.cursor()
        packetTables = self.packetTableCreator.getPacketTables(minTimestamp)
        for packetTable in reversed(packetTables):
            # We only look for map id 1 and 7 since we use this method to extend a moving marker
            sql = selectCursor.mogrify("""select *
                from """ + packetTable + """ packet
                where station_id = %s
                    and is_moving = 1
                    and map_id in (1,7)""", (stationId,))

            if (minTimestamp != 0):
                sql = sql + \
                    selectCursor.mogrify(
                        """ and timestamp > %s""", (int(minTimestamp),))

            sql = sql + \
                selectCursor.mogrify(
                    """ order by marker_id desc, id desc limit 1""")
            # Sort by marker_id first and packet as second, otherwise client might render it wrong

            selectCursor.execute(sql)

            record = selectCursor.fetchone()
            if (record is not None):
                selectCursor.close()
                return self.getObjectFromRecord(record)
        selectCursor.close()
        return self.create()

    def getLatestConfirmedObjectByStationId(self, stationId, minTimestamp=0):
        """Returns the latest confirmed packet object specified by station id
        Args:
            stationId (int):     Station id to look for
            minTimestamp (int):  Min requested unix timestamp

        Returns:
            Packet
        """
        selectCursor = self.db.cursor()

        sql = selectCursor.mogrify("""select *
            from station
            where station.id = %s""", (stationId,))

        selectCursor.execute(sql)
        record = selectCursor.fetchone()
        selectCursor.close()

        if (record is not None and record["latest_confirmed_packet_timestamp"] is not None and record["latest_confirmed_packet_timestamp"] >= minTimestamp):
            return self.getObjectByIdAndTimestamp(record["latest_confirmed_packet_id"], record["latest_confirmed_packet_timestamp"])
        else:
            return self.create()

    def getLatestObjectByStationId(self, stationId, minTimestamp=0):
        """Returns the latest Packet specified by station id (that has a location)
        Args:
            stationId (int):     Station id to look for
            minTimestamp (int):  Min requested unix timestamp

        Returns:
            Packet
        """
        selectCursor = self.db.cursor()

        sql = selectCursor.mogrify("""select *
            from station
            where station.id = %s""", (stationId,))

        selectCursor.execute(sql)
        record = selectCursor.fetchone()
        selectCursor.close()

        if (record is not None and record["latest_location_packet_timestamp"] is not None and record["latest_location_packet_timestamp"] >= minTimestamp):
            return self.getObjectByIdAndTimestamp(record["latest_location_packet_id"], record["latest_location_packet_timestamp"])
        else:
            return self.create()

    def getMostRecentConfirmedObjectListByStationIdList(self, stationIdList, minTimestamp):
        """Returns an array of the most recent confirmed Packet's specified by station id's

        Note:
            This method returnes the latest packet for moving stations and the latest packet for every uniqe position for stationary stations.

        Args:
            stationIdList (array): Station id's to look for
            minTimestamp (int):    Min requested unix timestamp

        Returns:
            Array
        """
        if (len(stationIdList) == 0):
            return []
        selectCursor = self.db.cursor()
        result = []

        # Stationary objects
        packetTables = self.packetTableCreator.getPacketTables(minTimestamp)
        for packetTable in packetTables:
            sql = selectCursor.mogrify("""select *
                from """ + packetTable + """
                where station_id in %s
                    and timestamp > %s
                    and is_moving = 0
                    and map_id = 1""", (tuple(stationIdList), int(minTimestamp),))
            # Since we only should get one moving and all other should be stationary an "order by" should not be nessecery
            selectCursor.execute(sql)

            for record in selectCursor:
                if (record is not None):
                    packet = self.getObjectFromRecord(record)
                    result.append(packet)

        # Moving objects
        for stationId in stationIdList:
            packet = self.getLatestConfirmedMovingObjectByStationId(
                stationId, minTimestamp)
            if (packet.isExistingObject()):
                result.append(packet)

        selectCursor.close()
        return result

    def getMostRecentConfirmedObjectListByStationIdListAndTimeInterval(self, stationIdList, minTimestamp, maxTimestamp):
        """Returns an array of the most recent confirmed Packet's specified by station id's

        Note:
            This method returnes the latest packet for moving stations and the latest packet for every uniqe position for stationary stations.

        Args:
            stationIdList (array): Station id's to look for
            minTimestamp (int):    Min requested unix timestamp
            maxTimestamp (int):    Max requested unix timestamp

        Returns:
            Array
        """
        if (len(stationIdList) == 0):
            return []

        minTimestampRoundedQuarter = int(
            minTimestamp) - (int(minTimestamp) % 900)
        minTimestampRoundedDay = int(
            minTimestamp) - (int(minTimestamp) % 86400)

        selectCursor = self.db.cursor()
        result = []
        foundStationaryMarkerHashList = []
        foundMovingMarkerStationIdList = []

        packetTables = self.packetTableCreator.getPacketTables(
            minTimestamp, maxTimestamp)
        for packetTable in reversed(packetTables):
            # Stationary objects
            sql = selectCursor.mogrify("""select *
                from """ + packetTable + """ packet
                where id in (
                    select max(id)
                    from """ + packetTable + """ packet
                    where station_id in %s
                        and timestamp > %s
                        and timestamp <= %s
                        and is_moving = 0
                        and map_id in (1,2,12)
                    group by station_id, latitude, longitude, symbol, symbol_table
                )""", (tuple(stationIdList), int(minTimestamp), int(maxTimestamp)))
            # Since we only should get one moving and all other should be stationary an "order by" should not be nessecery
            selectCursor.execute(sql)
            for record in selectCursor:
                if (record is not None):
                    markerHash = hash(str(record['station_id']) + ';' + str(record['station_id']) + ';' + str(
                        record['latitude']) + ';' + str(record['longitude']) + ';' + record['symbol'] + ';' + record['symbol_table'])
                    if (markerHash not in foundStationaryMarkerHashList):
                        foundStationaryMarkerHashList.append(markerHash)
                        packet = self.getObjectFromRecord(record)
                        result.append(packet)

            # Moving objects
            sql = selectCursor.mogrify("""select packet.*
                from """ + packetTable + """ packet
                where id in (
                    select max(id)
                    from """ + packetTable + """ packet
                    where station_id in %s
                        and map_id in (1,2,12)
                        and packet.timestamp > %s
                        and packet.timestamp <= %s
                        and packet.is_moving = 1
                    group by station_id
                )""", (tuple(stationIdList), int(minTimestamp), int(maxTimestamp)))
            # Since we only should get one moving and all other should be stationary an "order by" should not be nessecery

            selectCursor.execute(sql)
            for record in selectCursor:
                if (record is not None):
                    if (record['station_id'] not in foundMovingMarkerStationIdList):
                        foundMovingMarkerStationIdList.append(
                            record['station_id'])

                        packet = self.getObjectFromRecord(record)
                        result.append(packet)
        selectCursor.close()
        return result

    def getLatestConfirmedObjectListByStationIdList(self, stationIdList, minTimestamp=0):
        """Returns an array of the latest confirmed packet objects with specified station id's

        Args:
            stationIdList (array): station id's to look for
            minTimestamp (int):    Min requested unix timestamp

        Returns:
            Array
        """
        if (len(stationIdList) == 0):
            return []

        result = []
        if (minTimestamp == 0):
            # Apperantly we are looking for the latest no matter the age
            for stationId in stationIdList:
                packet = self.getLatestConfirmedObjectByStationId(stationId)
                if (packet.isExistingObject()):
                    result.append(packet)
        else:
            selectCursor = self.db.cursor()
            packetTables = self.packetTableCreator.getPacketTables(
                minTimestamp)

            for packetTable in reversed(packetTables):
                sql = selectCursor.mogrify("""select packet.*
                    from """ + packetTable + """ packet, station
                    where station.id in %s
                        and station.latest_confirmed_packet_id = packet.id
                        and station.latest_confirmed_packet_timestamp = packet.timestamp """, (tuple(stationIdList),))

                if (minTimestamp != 0):
                    sql = sql + selectCursor.mogrify(
                        """ and station.latest_confirmed_packet_timestamp > %s""" % (int(minTimestamp),))

                sql = sql + \
                    selectCursor.mogrify(
                        """ order by packet.marker_id, packet.id""")
                # Sort by marker_id first and packet as second, otherwise client might render it wrong

                selectCursor.execute(sql)

                for record in selectCursor:
                    if (record is not None):
                        result.append(self.getObjectFromRecord(record))

                if (len(result) >= len(stationIdList)):
                    break

            selectCursor.close()
        return result

    def getLatestObjectListByStationIdList(self, stationIdList, minTimestamp=0):
        """Returns an array of the latest Packet's (that has a location) with specified station id's

        Args:
            stationIdList (array): station id's to look for
            minTimestamp (int):    Min requested unix timestamp

        Returns:
            Array
        """
        if (len(stationIdList) == 0):
            return []

        result = []
        if (minTimestamp == 0):
            # Apperantly we are looking for the latest no matter the age
            for stationId in stationIdList:
                packet = self.getLatestObjectByStationId(stationId)
                if (packet.isExistingObject()):
                    result.append(packet)

        else:
            selectCursor = self.db.cursor()
            packetTables = self.packetTableCreator.getPacketTables(
                minTimestamp)
            for packetTable in reversed(packetTables):
                sql = selectCursor.mogrify("""select packet.*
                    from """ + packetTable + """ packet, station
                    where station.id in %s
                        and station.latest_location_packet_id = packet.id
                        and station.latest_confirmed_packet_timestamp = packet.timestamp """, (tuple(stationIdList),))

                if (minTimestamp != 0):
                    sql = sql + selectCursor.mogrify(
                        """ and station.latest_location_packet_timestamp > %s""" % (int(minTimestamp),))

                selectCursor.execute(sql)

                for record in selectCursor:
                    if (record is not None):
                        result.append(self.getObjectFromRecord(record))

                if (len(result) >= len(stationIdList)):
                    break

            selectCursor.close()
        return result

    def getObjectFromRecord(self, record):
        """Returns a packet object from a record

        Args:
            record (dict):  Database record dict to convert to a packet object

        Returns:
            Packet
        """
        dbObject = self.create()
        if (record is not None):
            dbObject.id = record["id"]
            dbObject.stationId = int(record["station_id"])
            dbObject.senderId = int(record["sender_id"])
            dbObject.packetTypeId = record["packet_type_id"]
            dbObject.timestamp = int(record["timestamp"])

            if (record["latitude"] is not None):
                dbObject.latitude = float(record["latitude"])
            else:
                dbObject.latitude = None

            if (record["longitude"] is not None):
                dbObject.longitude = float(record["longitude"])
            else:
                dbObject.longitude = None

            dbObject.posambiguity = record['posambiguity']
            dbObject.symbol = record["symbol"]
            dbObject.symbolTable = record["symbol_table"]
            dbObject.mapSector = record["map_sector"]
            dbObject.relatedMapSectors = record["related_map_sectors"]
            dbObject.mapId = record["map_id"]
            dbObject.sourceId = record["source_id"]
            dbObject.markerId = record["marker_id"]
            dbObject.speed = record["speed"]
            dbObject.course = record["course"]
            dbObject.altitude = record["altitude"]
            dbObject.isMoving = record['is_moving']

            if (record["reported_timestamp"] is not None):
                dbObject.reportedTimestamp = int(record["reported_timestamp"])
            else:
                dbObject.reportedTimestamp = record["reported_timestamp"]

            if (record["position_timestamp"] is not None):
                dbObject.positionTimestamp = int(record["position_timestamp"])
            else:
                dbObject.positionTimestamp = record["position_timestamp"]

            if ("packet_tail_timestamp" in record):
                dbObject.packetTailTimestamp = record['packet_tail_timestamp']
            else:
                dbObject.packetTailTimestamp = dbObject.timestamp

            if ("marker_counter" in record):
                dbObject.markerCounter = record['marker_counter']
            else:
                dbObject.markerCounter = 1

            if ("comment" in record):
                dbObject.comment = record['comment']
            else:
                dbObject.comment = None

            if ("raw_path" in record):
                dbObject.rawPath = record['raw_path']
            else:
                dbObject.rawPath = None

            if ("raw" in record):
                dbObject.raw = record['raw']
            else:
                dbObject.raw = None

            if ("phg" in record):
                dbObject.phg = record['phg']
            else:
                dbObject.phg = None

            if ("rng" in record):
                dbObject.rng = record['rng']
            else:
                dbObject.rng = None

            if ("latest_phg_timestamp" in record):
                dbObject.latestPhgTimestamp = record['latest_phg_timestamp']
            else:
                dbObject.latestPhgTimestamp = None

            if ("latest_rng_timestamp" in record):
                dbObject.latestRngTimestamp = record['latest_rng_timestamp']
            else:
                dbObject.latestRngTimestamp = None
        return dbObject

    def create(self):
        """Creates an empty Packet

        Returns:
            Packet
        """
        return Packet(self.db)
