from autobahn.twisted.websocket import WebSocketServerFactory
from autobahn.twisted.resource import WebSocketResource
from autobahn.websocket.compress import PerMessageDeflateOffer, PerMessageDeflateOfferAccept
from server.trackdirect.TrackDirectConfig import TrackDirectConfig
from server.trackdirect.TrackDirectWebsocketServer import TrackDirectWebsocketServer
from server.trackdirect.TrackDirectWebSocketServerFactory import TrackDirectWebSocketServerFactory
import argparse
import psutil
import sys
import os.path
import logging.handlers
from twisted.internet import reactor
from twisted.web.server import Site
from twisted.web.static import File
from socket import AF_INET

LOG_FILE_MAX_BYTES = 1000000
LOG_FILE_BACKUP_COUNT = 10


def setup_logger(name, log_file, level=logging.INFO):
    """Setup logger with file and console handlers."""
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    file_handler = logging.handlers.RotatingFileHandler(
        filename=os.path.expanduser(log_file), mode='a',
        maxBytes=LOG_FILE_MAX_BYTES, backupCount=LOG_FILE_BACKUP_COUNT)
    file_handler.setFormatter(formatter)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    logger.setLevel(level)

    return logger


def master(options, config_file, track_direct_logger):
    """Start of the master process."""
    worker_pid = os.getpid()
    p = psutil.Process(worker_pid)
    p.cpu_affinity([0])
    track_direct_logger.info(
        f"Starting master with PID {worker_pid} (on CPU id(s): {','.join(map(str, p.cpu_affinity()))})")

    try:
        factory = TrackDirectWebSocketServerFactory(config_file)
        factory.protocol = TrackDirectWebsocketServer

        resource = WebSocketResource(factory)
        root = File(".")
        root.putChild(b"ws", resource)
        site = Site(root)

        config = TrackDirectConfig()
        port = reactor.listenTCP(config.websocket_port, site)

        for i in range(1, options.workers):
            args = [sys.executable, "-u", __file__]
            args.extend(sys.argv[1:])
            args.extend(["--fd", str(port.fileno()), "--cpuid", str(i)])

            reactor.spawnProcess(
                None, sys.executable, args,
                childFDs={0: 0, 1: 1, 2: 2, port.fileno(): port.fileno()},
                env=os.environ)

        options.fd = port.fileno()
        listen(options, config_file)

    except Exception as e:
        track_direct_logger.error(f"Error in master process: {e}", exc_info=True)


def worker(options, config_file, track_direct_logger):
    """Start background worker process."""
    try:
        worker_pid = os.getpid()
        p = psutil.Process(worker_pid)
        p.cpu_affinity([options.cpuid])

        track_direct_logger.info(
            f"Starting worker with PID {worker_pid} (on CPU id(s): {','.join(map(str, p.cpu_affinity()))})")

        listen(options, config_file)

    except Exception as e:
        track_direct_logger.error(f"Error in worker process: {e}", exc_info=True)


def listen(options, config_file):
    """Start to listen on websocket requests."""
    config = TrackDirectConfig()
    factory = TrackDirectWebSocketServerFactory(
        config_file,
        f"ws://{config.websocket_hostname}:{config.websocket_port}",
        externalPort=config.websocket_external_port)
    factory.protocol = TrackDirectWebsocketServer

    # Enable WebSocket extension "permessage-deflate".
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

    parser = argparse.ArgumentParser(description='Track Direct WebSocket Server')
    parser.add_argument('--config', dest='config_file', type=str, default=None,
                        help='The Track Direct config file, e.g. trackdirect.ini')
    parser.add_argument('--workers', dest='workers', type=int, default=DEFAULT_WORKERS,
                        help='Number of workers to spawn - should fit the number of (physical) CPU cores.')
    parser.add_argument('--fd', dest='fd', type=int, default=None,
                        help='If given, this is a worker which will use provided FD and all other options are ignored.')
    parser.add_argument('--cpuid', dest='cpuid', type=int, default=None,
                        help='If given, this is a worker which will use provided CPU core to set its affinity.')

    options = parser.parse_args()
    config = TrackDirectConfig()
    config.populate(options.config_file)

    track_direct_logger = setup_logger('trackdirect', config.error_log)
    #aprslib_logger = setup_logger('aprslib.IS', config.error_log)

    if options.fd is not None:
        worker(options, options.config_file, track_direct_logger)
    else:
        master(options, options.config_file, track_direct_logger)