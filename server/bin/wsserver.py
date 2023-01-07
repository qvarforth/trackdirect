from autobahn.twisted.websocket import WebSocketServerFactory
from autobahn.twisted.resource import WebSocketResource
from autobahn.websocket.compress import PerMessageDeflateOffer, PerMessageDeflateOfferAccept
import trackdirect
import argparse
import psutil
import sys
import os.path
import logging
import logging.handlers
from twisted.internet import reactor
from twisted.web.server import Site
from twisted.web.static import File
from socket import AF_INET


def master(options, trackDirectLogger):
    """
    Start of the master process.
    """
    config = trackdirect.TrackDirectConfig()
    config.populate(options.config)

    workerPid = os.getpid()
    p = psutil.Process(workerPid)
    p.cpu_affinity([0])
    trackDirectLogger.warning("Starting master with PID " + str(workerPid) + " (on CPU id(s): " + ','.join(map(str, p.cpu_affinity())) + ")")

    try:
        factory = WebSocketServerFactory()
        factory.protocol = trackdirect.TrackDirectWebsocketServer

        resource = WebSocketResource(factory)
        root = File(".")
        root.putChild(b"ws", resource)
        site = Site(root)

        port = reactor.listenTCP(config.websocketPort, site)

        for i in range(1, options.workers):
            args = [sys.executable, "-u", __file__]
            args.extend(sys.argv[1:])
            args.extend(["--fd", str(port.fileno()), "--cpuid", str(i)])

            reactor.spawnProcess(
                None, sys.executable, args,
                childFDs={0: 0, 1: 1, 2: 2, port.fileno(): port.fileno()},
                env=os.environ)

        options.fd = port.fileno()
        listen(options, trackDirectLogger)

    except Exception as e:
        trackDirectLogger.error(e, exc_info=1)


def worker(options, trackDirectLogger):
    """
    Start background worker process.
    """
    config = trackdirect.TrackDirectConfig()
    config.populate(options.config)

    try:
        workerPid = os.getpid()
        p = psutil.Process(workerPid)
        p.cpu_affinity([options.cpuid])

        trackDirectLogger.warning("Starting worker with PID " + str(workerPid) + " (on CPU id(s): " + ','.join(map(str, p.cpu_affinity())) + ")")

        listen(options, trackDirectLogger)

    except Exception as e:
        trackDirectLogger.error(e, exc_info=1)


def listen(options, trackDirectLogger) :
    """
    Start to listen on websocket requests.
    """
    config = trackdirect.TrackDirectConfig()
    config.populate(options.config)

    factory = WebSocketServerFactory(
        "ws://" + config.websocketHostname + ":" + str(config.websocketPort),
        externalPort = config.websocketExternalPort)
    factory.protocol = trackdirect.TrackDirectWebsocketServer

    # Enable WebSocket extension "permessage-deflate".
    # Function to accept offers from the client ..
    def accept(offers):
        for offer in offers:
            if isinstance(offer, PerMessageDeflateOffer):
                return PerMessageDeflateOfferAccept(offer)
    factory.setProtocolOptions(perMessageCompressionAccept=accept)

    reactor.suggestThreadPoolSize(25)

    # Socket already created, just start listening and accepting
    reactor.adoptStreamPort(options.fd, AF_INET, factory)

    reactor.run()


if __name__ == '__main__':
    DEFAULT_WORKERS = psutil.cpu_count()

    parser = argparse.ArgumentParser(
        description='Track Direct WebSocket Server')
    parser.add_argument('--config', dest='config', type=str, default=None,
                        help='The Track Direct config file, e.g. trackdirect.ini')
    parser.add_argument('--workers', dest='workers', type=int, default=DEFAULT_WORKERS,
                        help='Number of workers to spawn - should fit the number of (physical) CPU cores.')
    parser.add_argument('--fd', dest='fd', type=int, default=None,
                        help='If given, this is a worker which will use provided FD and all other options are ignored.')
    parser.add_argument('--cpuid', dest='cpuid', type=int, default=None,
                        help='If given, this is a worker which will use provided CPU core to set its affinity.')

    options = parser.parse_args()
    config = trackdirect.TrackDirectConfig()
    config.populate(options.config)

    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    fh = logging.handlers.RotatingFileHandler(filename=os.path.expanduser(
        config.errorLog), mode='a', maxBytes=1000000, backupCount=10)
    fh.setFormatter(formatter)

    consoleHandler = logging.StreamHandler()
    consoleHandler.setFormatter(formatter)

    trackDirectLogger = logging.getLogger('trackdirect')
    trackDirectLogger.addHandler(fh)
    trackDirectLogger.addHandler(consoleHandler)
    trackDirectLogger.setLevel(logging.INFO)

    fh2 = logging.handlers.RotatingFileHandler(filename=os.path.expanduser(
        config.errorLog), mode='a', maxBytes=1000000, backupCount=10)
    # aprslib is logging non important "socket error on ..." using ERROR-level
    fh2.setFormatter(formatter)

    aprslibLogger = logging.getLogger('aprslib.IS')
    aprslibLogger.addHandler(fh2)
    aprslibLogger.addHandler(consoleHandler)
    aprslibLogger.setLevel(logging.INFO)

    if options.fd is not None:
        worker(options, trackDirectLogger)
    else:
        master(options, trackDirectLogger)
