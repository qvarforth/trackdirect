import logging
import aprslib
import collections
import time
import re


class AprsISConnection(aprslib.IS):
    """Handles communication with the APRS-IS server
    """

    def __init__(self, callsign, passwd="-1", host="rotate.aprs.net", port=10152):
        """The __init__ method.

        Args:
            callsign (string):               APRS-IS callsign
            passwd (string):                 APRS-IS password
            host (string):                   APRS-IS Server hostname
            port (int):                      APRS-IS Server port
        """
        aprslib.IS.__init__(self, callsign, passwd, host, port)

        self.logger = logging.getLogger("aprslib.IS")
        self.frequencyLimit = None
        self.stationHashTimestamps = collections.OrderedDict()
        self.sourceId = 1

    def setFrequencyLimit(self, frequencyLimit):
        """Set frequency limit

        Args:
            frequencyLimit (int):  Hard frequency limit (in seconds)
        """
        self.frequencyLimit = frequencyLimit

    def getFrequencyLimit(self):
        """Get frequency limit

        Return:
            int
        """
        return self.frequencyLimit

    def setSourceId(self, sourceId):
        """Set what source packet is from (APRS, CWOP ...)

        Args:
            sourceId (int):  Id that corresponds to id in source-table
        """
        self.sourceId = sourceId

    def filteredConsumer(self, callback, blocking=True, raw=False):
        """The filtered consume method

        Args:
            callback (boolean):    Method to call with result
            blocking (boolean):    Set to true if consume should be blocking
            raw (boolean):         Set to true if result should be raw
        """
        def filterCallback(line):
            try:
                # decode first then replace
                line = line.decode()
                line = line.replace('\x00', '')
            except UnicodeError as e:
                # string is not UTF-8
                return

            if line.startswith('dup'):
                line = line[4:].strip()

            if (self._isSendingToFast(line)):
                return

            if raw:
                callback(line)
            else:
                callback(self._parse(line))

        self.consumer(filterCallback, blocking, False, True)

    def _isSendingToFast(self, line):
        """Simple check that returns True if sending frequency limit is to fast

        Args:
            line (string):         Packet string

        Returns:
            True if sending frequency limit is to fast
        """
        if (self.frequencyLimit is not None):
            try:
                (name, other) = line.split('>', 1)
            except:
                return False

            # Divide into body and head
            try:
                (head, body) = other.split(':', 1)
            except:
                return False

            if len(body) == 0:
                return False

            packetType = body[0]
            body = body[1:]

            # Try to find turn rate and reduce frequency limit if high turn rate
            frequencyLimitToApply = int(self.frequencyLimit)
            if (self.sourceId == 5) :
                match = re.search("(\+|\-)(\d\.\d)rot ", line)
                try:
                    turnRate = abs(float(match.group(2)))
                    if (turnRate > 0) :
                        frequencyLimitToApply = int(frequencyLimitToApply / (1+turnRate))
                except:
                    pass

            latestTimestampOnMap = 0
            if (name + packetType in self.stationHashTimestamps):
                latestTimestampOnMap = self.stationHashTimestamps[name + packetType]

                if (((int(time.time()) - 1) - frequencyLimitToApply) < latestTimestampOnMap):
                    # This sender is sending faster than config limit
                    return True
            self.stationHashTimestamps[name + packetType] = int(time.time()) - 1
            self._cacheMaintenance()
        return False

    def _cacheMaintenance(self):
        """Make sure cache does not contain to many packets
        """
        frequencyLimitToApply = int(self.frequencyLimit)
        maxNumberOfPackets =  frequencyLimitToApply * 1000 # We assume that we never have more than 1000 packets per second
        if (len(self.stationHashTimestamps) > maxNumberOfPackets):
            try:
                self.stationHashTimestamps.popitem(last=False)
            except (KeyError, StopIteration) as e:
                pass
