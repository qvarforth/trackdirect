import sys
import os.path
import logging
import logging.handlers
import trackdirect

if __name__ == '__main__':

    if (len(sys.argv) < 3):
        print "\n" + sys.argv[0] + ' [config.ini] [/output/directory]'
        sys.exit()
    elif (sys.argv[1].startswith("/")):
        if (not os.path.isfile(sys.argv[1])):
            print "\n" + sys.argv[0] + ' [config.ini] [/output/directory]'
            sys.exit()
    elif (not os.path.isfile(os.path.expanduser('~/trackdirect/config/' + sys.argv[1]))):
        print "\n" + sys.argv[0] + ' [config.ini] [/output/directory]'
        sys.exit()

    config = trackdirect.TrackDirectConfig()
    config.populate(sys.argv[1])

    fh = logging.handlers.RotatingFileHandler(filename=os.path.expanduser(
        '~/trackdirect/server/log/heatmap.log'), mode='a', maxBytes=1000000, backupCount=10)

    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)

    consoleHandler = logging.StreamHandler()
    consoleHandler.setFormatter(formatter)

    trackDirectLogger = logging.getLogger('trackdirect')
    trackDirectLogger.addHandler(fh)
    trackDirectLogger.addHandler(consoleHandler)
    trackDirectLogger.setLevel(logging.INFO)

    trackDirectLogger.info("Starting (output directory: " + sys.argv[2] + ")")

    try:
        trackDirectHeatMapCreator = trackdirect.TrackDirectHeatMapCreator(
            sys.argv[2])
        trackDirectHeatMapCreator.run()
    except Exception as e:
        trackDirectLogger.error(e, exc_info=1)
