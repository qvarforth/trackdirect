import logging
import collections

class PacketDuplicatePolicy:
    """Handles duplicate checks."""

    # Static class variables
    latest_packets_hash_ordered_dict = collections.OrderedDict()

    def __init__(self, station_repository):
        """Initialize PacketDuplicatePolicy.

        Args:
            station_repository: Repository to access station data.
        """
        self.minutes_back_to_look_for_duplicates = 30
        self.station_repository = station_repository
        self.logger = logging.getLogger('trackdirect')

    def is_duplicate(self, packet):
        """Check if the packet is a duplicate.

        Args:
            packet (Packet): Packet that may be a duplicate.

        Returns:
            bool: True if the packet is a duplicate, False otherwise.
        """
        if (packet.map_id in [1, 5, 7, 8, 9]
                and (packet.is_moving == 1 or packet.map_id == 8)
                and packet.latitude is not None
                and packet.longitude is not None):
            if self._is_packet_body_in_cache(packet):
                if self._is_to_be_treated_as_duplicate(packet):
                    return True
            self._add_to_cache(packet)
        elif packet.source_id == 3:
            return True
        return False

    def _is_packet_body_in_cache(self, packet):
        """Check if the packet body is in cache.

        Args:
            packet (Packet): Packet to look for in cache.

        Returns:
            bool: True if packet body is in cache, False otherwise.
        """
        packet_hash = self._get_packet_hash(packet)
        if packet_hash is None:
            return False

        if packet_hash in PacketDuplicatePolicy.latest_packets_hash_ordered_dict:
            prev_packet_values = PacketDuplicatePolicy.latest_packets_hash_ordered_dict[packet_hash]
            if (packet.raw_path != prev_packet_values['path']
                    and prev_packet_values['timestamp'] > packet.timestamp - (60 * self.minutes_back_to_look_for_duplicates)):
                return True
        return False

    def _is_to_be_treated_as_duplicate(self, packet):
        """Check if the packet should be treated as a duplicate.

        Args:
            packet (Packet): Packet to check.

        Returns:
            bool: True if packet should be treated as duplicate, False otherwise.
        """
        station = self.station_repository.get_object_by_id(packet.station_id)
        if station.latest_confirmed_latitude is not None and station.latest_confirmed_longitude is not None:
            station_lat_cmp = int(round(station.latest_confirmed_latitude * 100000))
            station_lng_cmp = int(round(station.latest_confirmed_longitude * 100000))
        else:
            station_lat_cmp = 0
            station_lng_cmp = 0

        packet_lat_cmp = int(round(packet.latitude * 100000))
        packet_lng_cmp = int(round(packet.longitude * 100000))

        if (station.is_existing_object()
            and station_lat_cmp != 0
            and station_lng_cmp != 0
            and (packet.map_id == 8 or station_lat_cmp != packet_lat_cmp or station_lng_cmp != packet_lng_cmp)):
            return True
        return False

    def _get_packet_hash(self, packet):
        """Get a hash value of the Packet object.

        Args:
            packet (Packet): Packet to get hash for.

        Returns:
            str: Hash value of the packet.
        """
        if not packet.raw:
            return None

        packet_string = packet.raw.split(':', 1)[1]
        if not packet_string:
            return None
        return hash(packet_string.strip())

    def _add_to_cache(self, packet):
        """Add packet to cache.

        Args:
            packet (Packet): Packet to add to cache.
        """
        packet_hash = self._get_packet_hash(packet)
        PacketDuplicatePolicy.latest_packets_hash_ordered_dict[packet_hash] = {
            'path': packet.raw_path,
            'timestamp': packet.timestamp
        }
        self._cache_maintenance()

    def _cache_maintenance(self):
        """Ensure cache does not contain too many packets."""
        max_number_of_packets = self.minutes_back_to_look_for_duplicates * 60 * 100  # Assume an average of 100 packets per second
        if len(PacketDuplicatePolicy.latest_packets_hash_ordered_dict) > max_number_of_packets:
            try:
                PacketDuplicatePolicy.latest_packets_hash_ordered_dict.popitem(last=False)
            except (KeyError, StopIteration):
                pass