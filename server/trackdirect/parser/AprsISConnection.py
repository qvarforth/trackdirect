import logging
from twisted.python import log
import aprslib
import collections
import psycopg2
import datetime
import time


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
        self.stationHashTimestamps = {}

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

    def filteredConsumer(self, callback, blocking=True, raw=False):
        """The filtered consume method

        Args:
            callback (boolean):    Method to call with result
            blocking (boolean):    Set to true if consume should be blocking
            raw (boolean):         Set to true if result should be raw
        """
        def filterCallback(line):
            try:
                line = line.replace('\x00', '')
                line.decode('utf-8', 'replace')
            except UnicodeError:
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

            latestTimestampOnMap = 0
            if (name in self.stationHashTimestamps):
                latestTimestampOnMap = self.stationHashTimestamps[name]

                if ((int(time.time()) - 1) - int(self.frequencyLimit) < latestTimestampOnMap):
                    # This sender is sending faster than config limit
                    return True
            self.stationHashTimestamps[name] = int(time.time()) - 1
        return False
