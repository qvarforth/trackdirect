import logging
import trackdirect

from trackdirect.parser.AprsISConnection import AprsISConnection
from trackdirect.repositories.SenderRepository import SenderRepository

class AprsISReader():
    """The AprsISReader class will connect to a APRS-IS server and listen for APRS-packets
    """


    def __init__(self, state, db):
        """The __init__ method.

        Args:
            state (ConnectionState):   Instance of ConnectionState which contains the current state of the connection
            db (psycopg2.Connection):  Database connection (with autocommit)
        """
        self.state = state
        self.latestRealTimeFilter = None

        self.senderRepository = SenderRepository(db)

        self.aprsISConnection1 = None
        self.aprsISConnection2 = None

        self.logger = logging.getLogger('trackdirect')
        self.config = trackdirect.TrackDirectConfig()


    def start(self):
        """Connect to APRS-IS servers based on current state
        """
        self._connect()
        self._modifyFilter()


    def read(self, callback) :
        """Read data from the APRS-IS servers, specified callback will be called once for every waiting packet

        Args:
            callback (method):    Method to call when we read a packet from the APRS IS connection

        Note:
            Callback function is expecting to take 2 arguments, the "packet raw" as a string and a "source id" as an integer
        """
        try :
            if (self.aprsISConnection1 is not None or self.aprsISConnection2 is not None) :
                def aprsISCallback1(line) :
                    callback(line, self.config.websocketAprsSourceId1)

                def aprsISCallback2(line) :
                    callback(line, self.config.websocketAprsSourceId2)

                if (self.aprsISConnection2 is not None) :
                    self.aprsISConnection2.filteredConsumer(aprsISCallback2, False, True)

                if (self.aprsISConnection1 is not None) :
                    self.aprsISConnection1.filteredConsumer(aprsISCallback1, False, True)
        except IOError as e:
            callback(None, None)
        except Exception as e:
            self.logger.error(e, exc_info=1)
            callback(None, None)


    def pause(self) :
        """Pause without closing the aprsISConnection, we just set filter to nothing, that will result in no received packets
        """
        if (self.aprsISConnection1 is not None) :
            self.latestRealTimeFilter = None
            self.aprsISConnection1.set_filter('')

        if (self.aprsISConnection2 is not None) :
            self.latestRealTimeFilter = None
            self.aprsISConnection2.set_filter('')


    def stop(self):
        """Kill the connections to the APRS-IS servers
        """
        if (self.aprsISConnection2 is not None) :
            self.aprsISConnection2.close()
            self.aprsISConnection2 = None

        if (self.aprsISConnection1 is not None) :
            self.aprsISConnection1.close()
            self.aprsISConnection1 = None


    def clear(self, limit = None):
        """Clear the socket from all waiting lines

        Args:
            limit (int):  Max number of packets to clear (per connection)
        """
        counter1 = 0
        counter2 = 0
        if (self.aprsISConnection2 is not None) :
            for line in self.aprsISConnection1._socket_readlines(False):
                counter1 += 1
                if (limit is not None and counter1 >= limit) :
                    break
        if (self.aprsISConnection1 is not None) :
            for line in self.aprsISConnection1._socket_readlines(False):
                counter2 += 1
                if (limit is not None and counter2 >= limit) :
                    break
        return counter1 + counter2


    def _connect(self):
        """Connect to APRS-IS servers (if not allready connected)
        """
        if (self.aprsISConnection1 is None) :
            self.latestRealTimeFilter = None
            # Avoid using a verified user since server will not accept two verfied users with same name
            if (self.config.websocketAprsHost1 is not None) :
                try:
                    self.aprsISConnection1 = AprsISConnection("NOCALL", "-1", self.config.websocketAprsHost1, self.config.websocketAprsPort1)
                    if (self.config.websocketFrequencyLimit != 0) :
                        self.aprsISConnection1.setFrequencyLimit(self.config.websocketFrequencyLimit)
                    self.aprsISConnection1.connect()
                except Exception as e:
                    self.logger.error(e, exc_info=1)

        if (self.aprsISConnection2 is None) :
            self.latestRealTimeFilter = None
            # Avoid using a verified user since server will not accept two verfied users with same name
            if (self.config.websocketAprsHost2 is not None) :
                try:
                    self.aprsISConnection2 = AprsISConnection("NOCALL", "-1", self.config.websocketAprsHost2, self.config.websocketAprsPort2)
                    if (self.config.websocketFrequencyLimit != 0) :
                        self.aprsISConnection2.setFrequencyLimit(self.config.websocketFrequencyLimit)
                    self.aprsISConnection2.connect()
                except Exception as e:
                    self.logger.error(e, exc_info=1)


    def _modifyFilter(self) :
        """Set a new filter for the APRS-IS connections according to the latest requested map bounds
        """
        newFilter = self._getNewFilter()
        if (self.latestRealTimeFilter is not None and newFilter == self.latestRealTimeFilter) :
            # If new filter is equal to latest, do not do anything
            return

        # Just empty any waiting data on socket
        self.clear()

        self.latestRealTimeFilter = newFilter
        if (self.aprsISConnection1 is not None) :
            self.aprsISConnection1.set_filter(newFilter)

        if (self.aprsISConnection2 is not None) :
            self.aprsISConnection2.set_filter(newFilter)


    def _getNewFilter(self) :
        """Create new APRS-IS filter based latest requested map bounds
        """
        if (len(self.state.filterStationIdDict) > 0) :
            filter = "b"
            for stationId in self.state.filterStationIdDict:
                sender = self.senderRepository.getObjectByStationId(stationId)
                if (sender.name is not None) :
                    call, sep, ssid = sender.name.partition('-')
                    filter = filter + "/" + sender.name
        else :
            # We add some area arround current view
            #filter = "a/" + str(self.state.latestNeLat+1) + "/" + str(self.state.latestSwLng-2) + "/" + str(self.state.latestSwLat-1) + "/" + str(self.state.latestNeLng+2)
            filter = "a/" + str(self.state.latestNeLat+0.1) + "/" + str(self.state.latestSwLng-0.1) + "/" + str(self.state.latestSwLat-0.1) + "/" + str(self.state.latestNeLng+0.1)

        return filter
