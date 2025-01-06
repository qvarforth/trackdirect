import logging
import aprslib
import collections
import time
import re


class AprsISConnection(aprslib.IS):
    """Handles communication with the APRS-IS server."""

    def __init__(self, callsign, passwd="-1", host="rotate.aprs.net", port=10152):
        """
        Initialize the APRS-IS connection.

        Args:
            callsign (str): APRS-IS callsign.
            passwd (str): APRS-IS password.
            host (str): APRS-IS Server hostname.
            port (int): APRS-IS Server port.
        """
        super().__init__(callsign, passwd, host, port)
        self.logger = logging.getLogger("aprslib.IS")
        self.frequency_limit = None
        self.station_hash_timestamps = collections.OrderedDict()
        self.source_id = 1

    def set_frequency_limit(self, frequency_limit):
        """
        Set frequency limit.

        Args:
            frequency_limit (int): Hard frequency limit (in seconds).
        """
        self.frequency_limit = frequency_limit

    def get_frequency_limit(self):
        """
        Get frequency limit.

        Returns:
            int: The frequency limit.
        """
        return self.frequency_limit

    def set_source_id(self, source_id):
        """
        Set the source ID for the packet (APRS, CWOP, etc.).

        Args:
            source_id (int): ID that corresponds to ID in the source table.
        """
        self.source_id = source_id

    def filtered_consumer(self, callback, blocking=True, raw=False):
        """
        Consume packets with filtering.

        Args:
            callback (callable): Method to call with the result.
            blocking (bool): Set to True if consume should be blocking.
            raw (bool): Set to True if result should be raw.
        """
        def filter_callback(line):
            try:
                line = line.decode().replace('\x00', '')
            except UnicodeError:
                return

            if line.startswith('dup'):
                line = line[4:].strip()

            if self._is_sending_too_fast(line):
                return

            if raw:
                callback(line)
            else:
                callback(self._parse(line))

        self.consumer(filter_callback, blocking, False, True)

    def _is_sending_too_fast(self, line):
        """
        Check if sending frequency limit is too fast.

        Args:
            line (str): Packet string.

        Returns:
            bool: True if sending frequency limit is too fast, False otherwise.
        """
        if self.frequency_limit is not None:
            try:
                name, other = line.split('>', 1)
                head, body = other.split(':', 1)
            except ValueError:
                return False

            if not body:
                return False

            packet_type = body[0]
            body = body[1:]

            frequency_limit_to_apply = int(self.frequency_limit)
            if self.source_id == 5:
                match = re.search(r"(\+|\-)(\d\.\d)rot ", line)
                if match:
                    try:
                        turn_rate = abs(float(match.group(2)))
                        if turn_rate > 0:
                            frequency_limit_to_apply = int(frequency_limit_to_apply / (1 + turn_rate))
                    except ValueError:
                        pass

            latest_timestamp_on_map = self.station_hash_timestamps.get(name + packet_type, 0)
            current_time = int(time.time()) - 1

            if (current_time - frequency_limit_to_apply) < latest_timestamp_on_map:
                return True

            self.station_hash_timestamps[name + packet_type] = current_time
            self._cache_maintenance()

        return False

    def _cache_maintenance(self):
        """Ensure cache does not contain too many packets."""
        if self.frequency_limit is not None:
            max_packets = int(self.frequency_limit) * 1000
            while len(self.station_hash_timestamps) > max_packets:
                try:
                    self.station_hash_timestamps.popitem(last=False)
                except KeyError:
                    break