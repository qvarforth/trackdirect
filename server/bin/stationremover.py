import sys
import os.path
import logging
import logging.handlers
import datetime
import time
import trackdirect

from trackdirect.database.DatabaseConnection import DatabaseConnection
from trackdirect.database.DatabaseObjectFinder import DatabaseObjectFinder

if __name__ == '__main__':

    if (len(sys.argv) < 3):
        print("\n" + sys.argv[0] + ' [config.ini] [staion id]')
        sys.exit()
    elif (sys.argv[1].startswith("/")):
        if (not os.path.isfile(sys.argv[1])):
            print(f"\n File {sys.argv[1]} does not exists")
            print("\n" + sys.argv[0] + ' [config.ini] [staion id]')
            sys.exit()
    elif (not os.path.isfile(os.path.expanduser('~/trackdirect/config/' + sys.argv[1]))):
        print(f"\n File ~/trackdirect/config/{sys.argv[1]} does not exists")
        print("\n" + sys.argv[0] + ' [config.ini] [staion id]')
        sys.exit()

    stationId = sys.argv[2]

    config = trackdirect.TrackDirectConfig()
    config.populate(sys.argv[1])

    try:
        fh = logging.handlers.RotatingFileHandler(filename=os.path.expanduser(
            '~/trackdirect/server/log/stationremover.log'), mode='a', maxBytes=1000000, backupCount=10)

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

        trackDirectDb = DatabaseConnection()
        db = trackDirectDb.getConnection(True)
        db.set_isolation_level(0)
        cursor = db.cursor()
        cursor.execute("SET statement_timeout = '120s'")

        trackDirectDbObjectFinder = DatabaseObjectFinder(db)

        # If saving longer than 365 days, modify range
        for x in range(0, 365):
            prevDay = datetime.date.today() - datetime.timedelta(x)  # today minus x days
            prevDayTimestamp = prevDay.strftime("%s")
            prevDayFormat = datetime.datetime.utcfromtimestamp(
                int(prevDayTimestamp)).strftime('%Y%m%d')

            packetTable = "packet" + prevDayFormat
            packetPathTable = "packet" + prevDayFormat + "_path"
            packetWeatherTable = "packet" + prevDayFormat + "_weather"
            packetTelemetryTable = "packet" + prevDayFormat + "_telemetry"

            if (trackDirectDbObjectFinder.checkTableExists(packetPathTable)):

                # Delete paths for this station
                sql = """delete from """ + packetPathTable + \
                    """ where packet_id in (select id from """ + \
                    packetTable + """ where station_id = %s)"""
                cursor.execute(sql, (stationId,))
                trackDirectLogger.info("Deleted %s rows in %s" % (
                    cursor.rowcount or 0, packetPathTable))
                time.sleep(0.5)

                # Delete paths related to this station
                sql = """delete from """ + packetPathTable + """ where station_id = %s"""
                cursor.execute(sql, (stationId,))
                trackDirectLogger.info("Deleted %s related rows in %s" % (
                    cursor.rowcount or 0, packetPathTable))
                time.sleep(0.5)

            if (trackDirectDbObjectFinder.checkTableExists(packetTelemetryTable)):
                # Delete telemetry for this station
                sql = """delete from """ + packetTelemetryTable + """ where station_id = %s"""
                cursor.execute(sql, (stationId,))
                trackDirectLogger.info("Deleted %s rows in %s" % (
                    cursor.rowcount or 0, packetTelemetryTable))
                time.sleep(0.5)

            if (trackDirectDbObjectFinder.checkTableExists(packetWeatherTable)):
                # Delete weather for this station
                sql = """delete from """ + packetWeatherTable + """ where station_id = %s"""
                cursor.execute(sql, (stationId,))
                trackDirectLogger.info("Deleted %s rows in %s" % (
                    cursor.rowcount or 0, packetWeatherTable))
                time.sleep(0.5)

            if (trackDirectDbObjectFinder.checkTableExists(packetTable)):
                # Delete packets for this station
                sql = """delete from """ + packetTable + """ where station_id = %s"""
                cursor.execute(sql, (stationId,))
                trackDirectLogger.info("Deleted %s rows in %s" % (
                    cursor.rowcount or 0, packetTable))
                time.sleep(0.5)

        # Delete station
        sql = "delete from station where id = %s"
        cursor.execute(sql, (stationId,))
        trackDirectLogger.info(
            "Deleted %s rows from station" % (cursor.rowcount or 0))
        time.sleep(0.5)

        cursor.close()
        db.close()
        trackDirectLogger.info("Done!")

    except Exception as e:
        trackDirectLogger.error(e, exc_info=1)
