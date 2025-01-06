from autobahn.twisted.websocket import WebSocketServerFactory

class TrackDirectWebSocketServerFactory(WebSocketServerFactory):
    """The TrackDirectWebsocketServer class handles the incoming requests."""

    config = None

    def __init__(self, config_file, *args, **kwargs):
        WebSocketServerFactory.__init__(self, *args, **kwargs)
        self.config_file = config_file