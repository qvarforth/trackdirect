import logging
from server.trackdirect.TrackDirectConfig import TrackDirectConfig
from server.trackdirect.parser.AprsISConnection import AprsISConnection
from server.trackdirect.repositories.SenderRepository import SenderRepository

class AprsISReader:
    """The AprsISReader class will connect to an APRS-IS server and listen for APRS packets."""

    def __init__(self, state, db):
        """Initialize the AprsISReader.

        Args:
            state (ConnectionState): Instance of ConnectionState which contains the current state of the connection.
            db (psycopg2.Connection): Database connection (with autocommit).
        """
        self.state = state
        self.latest_real_time_filter = None
        self.sender_repository = SenderRepository(db)
        self.aprs_is_connection1 = None
        self.aprs_is_connection2 = None
        self.logger = logging.getLogger('trackdirect')
        self.config = TrackDirectConfig()

    def start(self):
        """Connect to APRS-IS servers based on current state."""
        self._connect()
        self._modify_filter()

    def read(self, callback):
        """Read data from the APRS-IS servers, specified callback will be called once for every waiting packet.

        Args:
            callback (method): Method to call when we read a packet from the APRS IS connection.

        Note:
            Callback function is expecting to take 2 arguments, the "packet raw" as a string and a "source id" as an integer.
        """
        try:
            if self.aprs_is_connection1 or self.aprs_is_connection2:
                def aprs_is_callback1(line):
                    callback(line, self.config.websocket_aprs_source_id1)

                def aprs_is_callback2(line):
                    callback(line, self.config.websocket_aprs_source_id2)

                if self.aprs_is_connection2:
                    self.aprs_is_connection2.filtered_consumer(aprs_is_callback2, False, True)

                if self.aprs_is_connection1:
                    self.aprs_is_connection1.filtered_consumer(aprs_is_callback1, False, True)
        except IOError:
            callback(None, None)
        except Exception as e:
            self.logger.error(f"Error reading from APRS-IS: {e}", exc_info=True)
            callback(None, None)

    def pause(self):
        """Pause without closing the AprsISConnection, we just set filter to nothing, that will result in no received packets."""
        self.latest_real_time_filter = None
        if self.aprs_is_connection1:
            self.aprs_is_connection1.set_filter('')
        if self.aprs_is_connection2:
            self.aprs_is_connection2.set_filter('')

    def stop(self):
        """Kill the connections to the APRS-IS servers."""
        if self.aprs_is_connection2:
            self.aprs_is_connection2.close()
            self.aprs_is_connection2 = None
        if self.aprs_is_connection1:
            self.aprs_is_connection1.close()
            self.aprs_is_connection1 = None

    def clear(self, limit=None):
        """Clear the socket from all waiting lines.

        Args:
            limit (int): Max number of packets to clear (per connection).
        """
        counter1 = 0
        counter2 = 0
        if self.aprs_is_connection2:
            for _ in self.aprs_is_connection2._socket_readlines(False):
                counter1 += 1
                if limit is not None and counter1 >= limit:
                    break
        if self.aprs_is_connection1:
            for _ in self.aprs_is_connection1._socket_readlines(False):
                counter2 += 1
                if limit is not None and counter2 >= limit:
                    break
        return counter1 + counter2

    def _connect(self):
        """Connect to APRS-IS servers (if not already connected)."""
        if self.aprs_is_connection1 is None :
            self.latest_real_time_filter = None
            # Avoid using a verified user since server will not accept two verified users with same name
            if self.config.websocket_aprs_host1 is not None :
                try:
                    self.aprs_is_connection1 = AprsISConnection("NOCALL", "-1", self.config.websocket_aprs_host1, self.config.websocket_aprs_port1)
                    if self.config.websocket_frequency_limit != 0 :
                        self.aprs_is_connection1.set_frequency_limit(self.config.websocket_frequency_limit)
                    self.aprs_is_connection1.connect()
                except Exception as e:
                    self.logger.error(e, exc_info=1)

        if self.aprs_is_connection2 is None :
            self.latest_real_time_filter = None
            # Avoid using a verified user since server will not accept two verified users with same name
            if self.config.websocket_aprs_host2 is not None :
                try:
                    self.aprs_is_connection2 = AprsISConnection("NOCALL", "-1", self.config.websocket_aprs_host2, self.config.websocket_aprs_port2)
                    if self.config.websocket_frequency_limit != 0 :
                        self.aprs_is_connection2.set_frequency_limit(self.config.websocket_frequency_limit)
                    self.aprs_is_connection2.connect()
                except Exception as e:
                    self.logger.error(e, exc_info=1)

    def _modify_filter(self):
        """Set a new filter for the APRS-IS connections according to the latest requested map bounds."""
        new_filter = self._get_new_filter()
        if self.latest_real_time_filter is not None and new_filter == self.latest_real_time_filter:
            return

        self.clear()
        self.latest_real_time_filter = new_filter
        if self.aprs_is_connection1:
            self.aprs_is_connection1.set_filter(new_filter)
        if self.aprs_is_connection2:
            self.aprs_is_connection2.set_filter(new_filter)

    def _get_new_filter(self):
        """Create new APRS-IS filter based on the latest requested map bounds."""
        if self.state.filter_station_id_dict:
            filter_str = "b"
            for station_id in self.state.filter_station_id_dict:
                sender = self.sender_repository.get_object_by_station_id(station_id)
                if sender.name:
                    filter_str += f"/{sender.name}"
        else:
            filter_str = f"a/{self.state.latest_ne_lat + 0.1}/{self.state.latest_sw_lng - 0.1}/" \
                         f"{self.state.latest_sw_lat - 0.1}/{self.state.latest_ne_lng + 0.1}"

        return filter_str