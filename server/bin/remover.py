import sys
import os
import logging
import logging.handlers
import datetime
import time
from server.trackdirect.TrackDirectConfig import TrackDirectConfig
from server.trackdirect.database.DatabaseConnection import DatabaseConnection
from server.trackdirect.database.DatabaseObjectFinder import DatabaseObjectFinder
from server.trackdirect.repositories.PacketRepository import PacketRepository

def setup_logging(db_name):
    log_file = os.path.expanduser(f'~/trackdirect/server/log/remover_{db_name}.log')
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.handlers.RotatingFileHandler(filename=log_file, mode='a', maxBytes=1000000, backupCount=10)
        ]
    )
    return logging.getLogger('trackdirect')

def validate_config_file(config_file):
    if not os.path.isfile(config_file):
        print(f"\n File {config_file} does not exist")
        print("\nUsage: script.py [config.ini]")
        sys.exit()

def drop_table_if_exists(cursor, dbobjfinder, table_name, logger):
    if dbobjfinder.check_table_exists(table_name):
        cursor.execute(f"DROP TABLE {table_name}")
        logger.info(f"Dropped table {table_name}")

def main():
    if len(sys.argv) < 2:
        print("\nUsage: script.py [config.ini]")
        sys.exit()

    config_file = sys.argv[1]
    if not config_file.startswith("/"):
        config_file = os.path.expanduser(f'~/trackdirect/config/{config_file}')
    validate_config_file(config_file)

    config = TrackDirectConfig()
    config.populate(config_file)

    logger = setup_logging(config.db_name)

    max_days_to_save_position_data = config.days_to_save_position_data
    max_days_to_save_station_data = config.days_to_save_station_data
    max_days_to_save_weather_data = config.days_to_save_weather_data
    max_days_to_save_telemetry_data = config.days_to_save_telemetry_data

    logger.info("Starting")
    logger.info(f"Saving position data for {max_days_to_save_position_data} days")
    logger.info(f"Saving station data for {max_days_to_save_station_data} days")
    logger.info(f"Saving weather data for {max_days_to_save_weather_data} days")
    logger.info(f"Saving telemetry data for {max_days_to_save_telemetry_data} days")

    try:
        track_direct_db = DatabaseConnection()
        db_no_auto_commit = track_direct_db.get_connection(False)
        db = track_direct_db.get_connection(True)
        db.set_isolation_level(0)
        cursor = db.cursor()
        cursor.execute("SET statement_timeout = '240s'")

        track_direct_db_object_finder = DatabaseObjectFinder(db)
        packet_repository = PacketRepository(db)

        # Loop over the latest days and delete packets that are not needed anymore
        for x in range(2, 16):
            prev_day = datetime.date.today() - datetime.timedelta(x)
            prev_day_timestamp = int(prev_day.strftime("%s"))
            prev_day_format = datetime.datetime.utcfromtimestamp(prev_day_timestamp).strftime('%Y%m%d')
            packet_table = f"packet{prev_day_format}"

            if track_direct_db_object_finder.check_table_exists(packet_table):
                deleted_rows = None
                do_full_vacuum = False
                while deleted_rows is None or deleted_rows >= 5000:
                    sql = f"""DELETE FROM {packet_table} WHERE id IN (
                              SELECT id FROM {packet_table} WHERE map_id NOT IN (1,12) LIMIT 5000)"""
                    cursor.execute(sql)
                    deleted_rows = cursor.rowcount
                    logger.info(f"Deleted {deleted_rows} from {packet_table}")
                    if deleted_rows > 0:
                        do_full_vacuum = True
                    time.sleep(0.5)
                if do_full_vacuum:
                    cursor.execute(f"VACUUM FULL {packet_table}_path")
                    cursor.execute(f"REINDEX TABLE {packet_table}_path")
                    cursor.execute(f"VACUUM FULL {packet_table}")
                    cursor.execute(f"REINDEX TABLE {packet_table}")

        # Drop packet_weather
        for x in range(max_days_to_save_weather_data, max_days_to_save_weather_data + 100):
            prev_day = datetime.date.today() - datetime.timedelta(x)
            prev_day_format = prev_day.strftime('%Y%m%d')
            packet_table = f"packet{prev_day_format}_weather"
            drop_table_if_exists(cursor,track_direct_db_object_finder, packet_table, logger)

        # Drop packet_telemetry
        for x in range(max_days_to_save_telemetry_data, max_days_to_save_telemetry_data + 100):
            prev_day = datetime.date.today() - datetime.timedelta(x)
            prev_day_format = prev_day.strftime('%Y%m%d')
            packet_table = f"packet{prev_day_format}_telemetry"
            drop_table_if_exists(cursor,track_direct_db_object_finder, packet_table, logger)

        # Drop packets
        for x in range(max_days_to_save_position_data, max_days_to_save_position_data + 100):
            prev_day = datetime.date.today() - datetime.timedelta(x)
            prev_day_format = prev_day.strftime('%Y%m%d')
            packet_table = f"packet{prev_day_format}"

            drop_table_if_exists(cursor, track_direct_db_object_finder, f"{packet_table}_ogn", logger)
            drop_table_if_exists(cursor, track_direct_db_object_finder, f"{packet_table}_path", logger)
            drop_table_if_exists(cursor, track_direct_db_object_finder, packet_table, logger)

        # Delete old stations
        timestamp_limit = int(time.time()) - (60 * 60 * 24 * max_days_to_save_station_data)
        deleted_rows = 0
        sql = """SELECT station.id, station.latest_sender_id, station.name
                 FROM station
                 WHERE latest_packet_timestamp < %s
                 AND (
                     EXISTS (
                         SELECT 1
                         FROM sender
                         WHERE sender.id = station.latest_sender_id
                         AND sender.name != station.name
                     )
                     OR
                     NOT EXISTS (
                         SELECT 1
                         FROM station station2, sender
                         WHERE sender.id = station.latest_sender_id
                         AND station2.latest_sender_id = sender.id
                         AND station2.name != sender.name
                     )
                 )
                 ORDER BY latest_packet_timestamp"""

        select_station_cursor = db.cursor()
        select_station_cursor.execute(sql, (timestamp_limit,))
        for record in select_station_cursor:
            logger.info(f"Trying to delete station {record['name']} ({record['id']})")
            delete_cursor = db_no_auto_commit.cursor()
            try:
                for table in ['station_telemetry_bits', 'station_telemetry_eqns', 'station_telemetry_param', 'station_telemetry_unit', 'station_city']:
                    delete_cursor.execute(f"DELETE FROM {table} WHERE station_id = %s", (record["id"],))

                delete_cursor.execute("DELETE FROM station WHERE id = %s", (record["id"],))
                delete_cursor.execute("DELETE FROM sender WHERE id = %s AND NOT EXISTS (SELECT 1 FROM station WHERE latest_sender_id = sender.id)", (record["latest_sender_id"],))

                db_no_auto_commit.commit()
                delete_cursor.close()
                deleted_rows += 1
                time.sleep(0.5)
            except Exception as e:
                logger.error(e, exc_info=1)
                db_no_auto_commit.rollback()
                delete_cursor.close()

        select_station_cursor.close()
        if deleted_rows > 0:
            logger.info(f"Deleted {deleted_rows} stations")

        cursor.execute("VACUUM ANALYZE station")
        cursor.execute("REINDEX TABLE station")
        cursor.execute("VACUUM ANALYZE sender")
        cursor.execute("REINDEX TABLE sender")

        # Close DB connection
        cursor.close()
        db.close()
        logger.info("Done!")

    except Exception as e:
        logger.error(e, exc_info=1)

if __name__ == '__main__':
    main()
