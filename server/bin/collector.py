import sys
import os.path
import logging.handlers
from server.trackdirect import TrackDirectConfig
from server.trackdirect import TrackDirectDataCollector

if __name__ == '__main__':

    if len(sys.argv) < 2:
        print("\n" + sys.argv[0] + ' [config.ini] [collector number]')
        sys.exit()
    elif sys.argv[1].startswith("/"):
        if not os.path.isfile(sys.argv[1]):
            print(f"\n File {sys.argv[1]} does not exists")
            print("\n" + sys.argv[0] + ' [config.ini] [collector number]')
            sys.exit()
    elif not os.path.isfile(os.path.expanduser('~/trackdirect/config/' + sys.argv[1])):
        print(f"\n File ~/trackdirect/config/{sys.argv[1]} does not exists")
        print("\n" + sys.argv[0] + ' [config.ini] [collector number]')
        sys.exit()

    config = TrackDirectConfig()
    config.populate(sys.argv[1])

    if len(sys.argv) < 3:
        collector_number = 0
    else:
        collector_number = int(sys.argv[2])
    collector_options = config.collector[collector_number]

    save_ogn_stations_with_missing_identity = False
    if config.save_ogn_stations_with_missing_identity:
        save_ogn_stations_with_missing_identity = True

    fh = logging.handlers.RotatingFileHandler(filename=os.path.expanduser(
        collector_options['error_log']), mode='a', maxBytes=1000000, backupCount=10)

    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    track_direct_logger = logging.getLogger('trackdirect')
    track_direct_logger.addHandler(fh)
    track_direct_logger.addHandler(console_handler)
    track_direct_logger.setLevel(logging.INFO)

    aprslib_logger = logging.getLogger('aprslib.IS')
    aprslib_logger.addHandler(fh)
    aprslib_logger.addHandler(console_handler)
    aprslib_logger.setLevel(logging.INFO)

    track_direct_logger.warning("Starting (Collecting from " + collector_options['host'] + ":" + str(
        collector_options['port_full']) + " using " + collector_options['callsign'] + " and " + str(collector_options['passcode']) + ")")

    try:
        track_direct_data_collector = TrackDirectDataCollector(
            collector_options,
            save_ogn_stations_with_missing_identity)
        track_direct_data_collector.run(sys.argv[1])
    except Exception as e:
        track_direct_logger.error(e, exc_info=1)
