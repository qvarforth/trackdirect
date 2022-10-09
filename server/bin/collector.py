import sys
import os.path
import logging
import logging.handlers
import trackdirect

if __name__ == '__main__':

    if (len(sys.argv) < 2):
        print("\n" + sys.argv[0] + ' [config.ini] [collector number]')
        sys.exit()
    elif (sys.argv[1].startswith("/")):
        if (not os.path.isfile(sys.argv[1])):
            print(f"\n File {sys.argv[1]} does not exists")
            print("\n" + sys.argv[0] + ' [config.ini] [collector number]')
            sys.exit()
    elif (not os.path.isfile(os.path.expanduser('~/trackdirect/config/' + sys.argv[1]))):
        print(f"\n File ~/trackdirect/config/{sys.argv[1]} does not exists")
        print("\n" + sys.argv[0] + ' [config.ini] [collector number]')
        sys.exit()

    config = trackdirect.TrackDirectConfig()
    config.populate(sys.argv[1])

    if (len(sys.argv) < 3):
        collectorNumber = 0
    else:
        collectorNumber = int(sys.argv[2])
    collectorOptions = config.collector[collectorNumber]

    saveOgnStationsWithMissingIdentity = False
    if (config.saveOgnStationsWithMissingIdentity):
        saveOgnStationsWithMissingIdentity = True

    fh = logging.handlers.RotatingFileHandler(filename=os.path.expanduser(
        collectorOptions['error_log']), mode='a', maxBytes=1000000, backupCount=10)

    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)

    consoleHandler = logging.StreamHandler()
    consoleHandler.setFormatter(formatter)

    trackDirectLogger = logging.getLogger('trackdirect')
    trackDirectLogger.addHandler(fh)
    trackDirectLogger.addHandler(consoleHandler)
    trackDirectLogger.setLevel(logging.INFO)

    aprslibLogger = logging.getLogger('aprslib.IS')
    aprslibLogger.addHandler(fh)
    aprslibLogger.addHandler(consoleHandler)
    aprslibLogger.setLevel(logging.INFO)

    trackDirectLogger.warning("Starting (Collecting from " + collectorOptions['host'] + ":" + str(
        collectorOptions['port_full']) + " using " + collectorOptions['callsign'] + " and " + str(collectorOptions['passcode']) + ")")

    try:
        trackDirectDataCollector = trackdirect.TrackDirectDataCollector(
            collectorOptions,
            saveOgnStationsWithMissingIdentity)
        trackDirectDataCollector.run()
    except Exception as e:
        trackDirectLogger.error(e, exc_info=1)
