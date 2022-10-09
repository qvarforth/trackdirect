import sys
import os.path
import logging
import logging.handlers
import datetime
import time
import trackdirect

from trackdirect.database.DatabaseConnection import DatabaseConnection
from trackdirect.database.DatabaseObjectFinder import DatabaseObjectFinder
from trackdirect.repositories.PacketRepository import PacketRepository

if __name__ == '__main__':

    if (len(sys.argv) < 2):
        print("\n" + sys.argv[0] + ' [config.ini]')
        sys.exit()
    elif (sys.argv[1].startswith("/")):
        if (not os.path.isfile(sys.argv[1])):
            print(f"\n File {sys.argv[1]} does not exists")
            print("\n" + sys.argv[0] + ' [config.ini]')
            sys.exit()
    elif (not os.path.isfile(os.path.expanduser('~/trackdirect/config/' + sys.argv[1]))):
        print(f"\n File ~/trackdirect/config/{sys.argv[1]} does not exists")
        print("\n" + sys.argv[0] + ' [config.ini]')
        sys.exit()

    config = trackdirect.TrackDirectConfig()
    config.populate(sys.argv[1])

    maxDaysToSavePositionData = int(config.daysToSavePositionData)
    maxDaysToSaveStationData = int(config.daysToSaveStationData)
    maxDaysToSaveWeatherData = int(config.daysToSaveWeatherData)
    maxDaysToSaveTelemetryData = int(config.daysToSaveTelemetryData)

    try:
        fh = logging.handlers.RotatingFileHandler(filename=os.path.expanduser(
            '~/trackdirect/server/log/remover_' + config.dbName + '.log'), mode='a', maxBytes=1000000, backupCount=10)

        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)

        consoleHandler = logging.StreamHandler()
        consoleHandler.setFormatter(formatter)

        trackDirectLogger = logging.getLogger('trackdirect')
        trackDirectLogger.addHandler(fh)
        trackDirectLogger.addHandler(consoleHandler)
        trackDirectLogger.setLevel(logging.INFO)

        trackDirectLogger.info("Starting")
        trackDirectLogger.info(
            "Saving position data for %s days" % (maxDaysToSavePositionData))
        trackDirectLogger.info(
            "Saving station data for %s days" % (maxDaysToSaveStationData))
        trackDirectLogger.info(
            "Saving weather data for %s days" % (maxDaysToSaveWeatherData))
        trackDirectLogger.info(
            "Saving telemetry data for %s days" % (maxDaysToSaveTelemetryData))

        trackDirectDb = DatabaseConnection()
        dbNoAutoCommit = trackDirectDb.getConnection(False)
        db = trackDirectDb.getConnection(True)
        db.set_isolation_level(0)
        cursor = db.cursor()
        cursor.execute("SET statement_timeout = '240s'")

        trackDirectDbObjectFinder = DatabaseObjectFinder(db)

        packetRepository = PacketRepository(db)

        #
        # Loop over the latest days and delete packets that is not needed any more
        #
        for x in range(2, 16):
            prevDay = datetime.date.today() - datetime.timedelta(x)  # today minus x days
            prevDayTimestamp = prevDay.strftime("%s")
            prevDayFormat = datetime.datetime.utcfromtimestamp(
                int(prevDayTimestamp)).strftime('%Y%m%d')
            packetTable = "packet" + prevDayFormat

            if (trackDirectDbObjectFinder.checkTableExists(packetTable)):
                deletedRows = None
                doFullVacuum = False
                while (deletedRows is None or deletedRows >= 5000):
                    sql = """delete from """ + packetTable + \
                        """ where id in (select id from """ + packetTable + \
                        """ where map_id not in (1,12) limit 5000)"""
                    cursor.execute(sql)
                    deletedRows = cursor.rowcount
                    trackDirectLogger.info(
                        "Deleted %s %s" % (deletedRows, packetTable))
                    if (deletedRows > 0):
                        doFullVacuum = True
                    time.sleep(0.5)
                if (doFullVacuum):
                    cursor.execute("""VACUUM FULL """ +
                                   packetTable + """_path""")
                    cursor.execute("""REINDEX TABLE """ +
                                   packetTable + """_path""")
                    cursor.execute("""VACUUM FULL """ + packetTable)
                    cursor.execute("""REINDEX TABLE """ + packetTable)

        #
        # Drop packet_weather
        #
        for x in range(maxDaysToSaveWeatherData, maxDaysToSaveWeatherData+100):
            prevDay = datetime.date.today() - datetime.timedelta(x)  # today minus x days
            prevDayTimestamp = prevDay.strftime("%s")
            prevDayFormat = datetime.datetime.utcfromtimestamp(
                int(prevDayTimestamp)).strftime('%Y%m%d')
            packetTable = "packet" + prevDayFormat

            if (trackDirectDbObjectFinder.checkTableExists(packetTable + "_weather")):
                cursor.execute("""drop table """ +
                               packetTable + """_weather""")
                trackDirectLogger.info(
                    "Dropped table %s_weather" % (packetTable))

        #
        # Drop packet_telemetry
        #
        for x in range(maxDaysToSaveTelemetryData, maxDaysToSaveTelemetryData+100):
            prevDay = datetime.date.today() - datetime.timedelta(x)  # today minus x days
            prevDayTimestamp = prevDay.strftime("%s")
            prevDayFormat = datetime.datetime.utcfromtimestamp(
                int(prevDayTimestamp)).strftime('%Y%m%d')
            packetTable = "packet" + prevDayFormat

            if (trackDirectDbObjectFinder.checkTableExists(packetTable + "_telemetry")):
                cursor.execute("""drop table """ +
                               packetTable + """_telemetry""")
                trackDirectLogger.info(
                    "Dropped table %s_telemetry" % (packetTable))

        #
        # Drop packets
        #
        for x in range(maxDaysToSavePositionData, maxDaysToSavePositionData+100):
            prevDay = datetime.date.today() - datetime.timedelta(x)  # today minus x days
            prevDayTimestamp = prevDay.strftime("%s")
            prevDayFormat = datetime.datetime.utcfromtimestamp(
                int(prevDayTimestamp)).strftime('%Y%m%d')
            packetTable = "packet" + prevDayFormat

            # Drop packet_ogn table
            if (trackDirectDbObjectFinder.checkTableExists(packetTable + "_ogn")):
                cursor.execute("""drop table """ + packetTable + """_ogn""")
                trackDirectLogger.info("Dropped table %s_ogn" % (packetTable))

            #
            # Drop packet_path table
            #
            if (trackDirectDbObjectFinder.checkTableExists(packetTable + "_path")):
                cursor.execute("""drop table """ + packetTable + """_path""")
                trackDirectLogger.info("Dropped table %s_path" % (packetTable))

            #
            # Drop packet table
            #
            if (trackDirectDbObjectFinder.checkTableExists(packetTable)):
                cursor.execute("""drop table """ + packetTable)
                trackDirectLogger.info("Dropped table %s" % (packetTable))

        #
        # Delete old stations
        #
        timestampLimit = int(time.time()) - (60*60*24*maxDaysToSaveStationData)
        deletedRows = 0
        sql = """select station.id, station.latest_sender_id, station.name
            from station
            where latest_packet_timestamp < %s
                and (
                    exists (
                        select 1
                        from sender
                        where sender.id = station.latest_sender_id
                            and sender.name != station.name
                    )
                    or
                    not exists (
                        select 1
                        from station station2, sender
                        where sender.id = station.latest_sender_id
                            and station2.latest_sender_id = sender.id
                            and station2.name != sender.name
                    )
                )
            order by latest_packet_timestamp"""

        selectStationCursor = db.cursor()
        selectStationCursor.execute(sql, (timestampLimit,))
        for record in selectStationCursor:
            trackDirectLogger.info("Trying to delete station %s (%s)" % (
                record["name"], record["id"]))
            try:
                deleteCursor = dbNoAutoCommit.cursor()

                sql = """delete from station_telemetry_bits where station_id = %s"""
                deleteCursor.execute(sql, (record["id"],))

                sql = """delete from station_telemetry_eqns where station_id = %s"""
                deleteCursor.execute(sql, (record["id"],))

                sql = """delete from station_telemetry_param where station_id = %s"""
                deleteCursor.execute(sql, (record["id"],))

                sql = """delete from station_telemetry_unit where station_id = %s"""
                deleteCursor.execute(sql, (record["id"],))

                sql = """delete from station_city where station_id = %s"""
                deleteCursor.execute(sql, (record["id"],))

                sql = """delete from station where id = %s"""
                deleteCursor.execute(sql, (record["id"],))

                sql = """delete from sender where id = %s and not exists (select 1 from station where latest_sender_id = sender.id)"""
                deleteCursor.execute(sql, (record["latest_sender_id"],))

                dbNoAutoCommit.commit()
                deleteCursor.close()
                deletedRows += 1
                time.sleep(0.5)
            except Exception as e:
                # Something went wrong
                #trackDirectLogger.error(e, exc_info=1)
                dbNoAutoCommit.rollback()
                deleteCursor.close()

        selectStationCursor.close()
        if (deletedRows > 0):
            trackDirectLogger.info("Deleted %s stations" % (deletedRows))

        cursor.execute("""VACUUM ANALYZE station""")
        cursor.execute("""REINDEX TABLE station""")
        cursor.execute("""VACUUM ANALYZE sender""")
        cursor.execute("""REINDEX TABLE sender""")

        #
        # Close DB connection
        #
        cursor.close()
        db.close()
        trackDirectLogger.info("Done!")

    except Exception as e:
        trackDirectLogger.error(e, exc_info=1)
