import sys
import os
import logging
import datetime
from server.trackdirect.TrackDirectConfig import TrackDirectConfig
from server.trackdirect.database.DatabaseConnection import DatabaseConnection
from server.trackdirect.database.DatabaseObjectFinder import DatabaseObjectFinder

if __name__ == '__main__':

    if len(sys.argv) < 3:
        print(f"\n{sys.argv[0]} [config.ini] [station id]")
        sys.exit()
    elif sys.argv[1].startswith("/"):
        if not os.path.isfile(sys.argv[1]):
            print(f"\nFile {sys.argv[1]} does not exist")
            print(f"\n{sys.argv[0]} [config.ini] [station id]")
            sys.exit()
    elif not os.path.isfile(os.path.expanduser(os.path.join('~/trackdirect/config', sys.argv[1]))):
        print(f"\nFile ~/trackdirect/config/{sys.argv[1]} does not exist")
        print(f"\n{sys.argv[0]} [config.ini] [station id]")
        sys.exit()

    stationId = sys.argv[2]

    config = TrackDirectConfig()
    config.populate(sys.argv[1])

    try:
        log_file_path = os.path.expanduser('~/trackdirect/server/log/stationremover.log')
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(),
                logging.handlers.RotatingFileHandler(
                    filename=log_file_path, mode='a', maxBytes=1000000, backupCount=10
                )
            ]
        )

        track_direct_logger = logging.getLogger('trackdirect')
        track_direct_logger.info("Starting")

        trackDirectDb = DatabaseConnection()
        db = trackDirectDb.get_connection(True)
        db.set_session(autocommit=True)
        cursor = db.cursor()
        cursor.execute("SET statement_timeout = '120s'")

        trackDirectDbObjectFinder = DatabaseObjectFinder(db)

        # If saving longer than 365 days, modify range
        for x in range(365):
            prevDay = datetime.date.today() - datetime.timedelta(days=x)
            prevDayFormat = prevDay.strftime('%Y%m%d')

            packetTable = f"packet{prevDayFormat}"
            packetPathTable = f"packet{prevDayFormat}_path"
            packetWeatherTable = f"packet{prevDayFormat}_weather"
            packetTelemetryTable = f"packet{prevDayFormat}_telemetry"

            if trackDirectDbObjectFinder.check_table_exists(packetPathTable):
                # Delete paths for this station
                sql = f"DELETE FROM {packetPathTable} WHERE packet_id IN (SELECT id FROM {packetTable} WHERE station_id = %s)"
                cursor.execute(sql, (stationId,))
                track_direct_logger.info(f"Deleted {cursor.rowcount or 0} rows in {packetPathTable}")

                # Delete paths related to this station
                sql = f"DELETE FROM {packetPathTable} WHERE station_id = %s"
                cursor.execute(sql, (stationId,))
                track_direct_logger.info(f"Deleted {cursor.rowcount or 0} related rows in {packetPathTable}")

            if trackDirectDbObjectFinder.check_table_exists(packetTelemetryTable):
                # Delete telemetry for this station
                sql = f"DELETE FROM {packetTelemetryTable} WHERE station_id = %s"
                cursor.execute(sql, (stationId,))
                track_direct_logger.info(f"Deleted {cursor.rowcount or 0} rows in {packetTelemetryTable}")

            if trackDirectDbObjectFinder.check_table_exists(packetWeatherTable):
                # Delete weather for this station
                sql = f"DELETE FROM {packetWeatherTable} WHERE station_id = %s"
                cursor.execute(sql, (stationId,))
                track_direct_logger.info(f"Deleted {cursor.rowcount or 0} rows in {packetWeatherTable}")

            if trackDirectDbObjectFinder.check_table_exists(packetTable):
                # Delete packets for this station
                sql = f"DELETE FROM {packetTable} WHERE station_id = %s"
                cursor.execute(sql, (stationId,))
                track_direct_logger.info(f"Deleted {cursor.rowcount or 0} rows in {packetTable}")

        # Delete station
        sql = "DELETE FROM station WHERE id = %s"
        cursor.execute(sql, (stationId,))
        track_direct_logger.info(f"Deleted {cursor.rowcount or 0} rows from station")

        cursor.close()
        db.close()
        track_direct_logger.info("Done!")

    except Exception as e:
        track_direct_logger.error(e, exc_info=True)