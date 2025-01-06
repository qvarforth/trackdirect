import time
from server.trackdirect.parser.policies.MapSectorPolicy import MapSectorPolicy


class PacketRelatedMapSectorsPolicy:
    """PacketRelatedMapSectorsPolicy handles logic related to map sectors for a packet."""

    def __init__(self, packet_repository):
        """
        Initialize the PacketRelatedMapSectorsPolicy class.

        Args:
            packet_repository (PacketRepository): PacketRepository instance.
        """
        self.packet_repository = packet_repository

    def get_all_related_map_sectors(self, packet, previous_packet):
        """
        Returns all related map sectors to the current packet.

        Note:
            A related map sector is a map-sector that is not the map sector of the current packet nor the previous packet,
            it is all the map-sectors in between the current packet and the previous packet.

        Args:
            packet (Packet): Packet that we want to analyze.
            previous_packet (Packet): Packet object that represents the previous packet for this station.

        Returns:
            list: Any related map sectors (as an array).
        """
        if not self._is_packet_likely_to_have_related_map_sectors(packet, previous_packet):
            return []

        related_map_sectors = []
        if previous_packet.map_id == 7:
            # When the previous packet is unconfirmed, add the path between prev-prev-packet and prev-packet also.
            min_timestamp = int(time.time()) - 86400  # 24 hours
            prev_previous_packet = self.packet_repository.get_latest_confirmed_moving_object_by_station_id(
                previous_packet.station_id, min_timestamp)
            if prev_previous_packet.is_existing_object() and prev_previous_packet.marker_counter > 1:
                # We found a confirmed prev-prev packet.
                related_map_sectors.extend(self._get_related_map_sectors(
                    previous_packet, prev_previous_packet))

        related_map_sectors.extend(
            self._get_related_map_sectors(packet, previous_packet))
        return related_map_sectors

    def _is_packet_likely_to_have_related_map_sectors(self, packet, previous_packet):
        """
        Returns true if the packet may be related to other map sectors than the map sector it's in.

        Args:
            packet (Packet): Packet that we want to analyze.
            previous_packet (Packet): Packet object that represents the previous packet for this station.

        Returns:
            bool: True if the packet may be related to other map sectors, otherwise false.
        """
        if (packet.is_moving == 1 and previous_packet.is_moving == 1 and packet.marker_id != 1):
            if packet.map_id == 1:
                if (previous_packet.marker_counter is not None and previous_packet.marker_counter > 1
                        or packet.marker_id == previous_packet.marker_id):
                    if previous_packet.map_id == 1 or packet.marker_id == previous_packet.marker_id:
                        return True
        return False

    def _get_related_map_sectors(self, packet1, packet2):
        """
        Get any related map sectors between specified packets.

        Note:
            A related map sector is a map-sector that is not the map sector of the current packet nor the previous packet,
            it is all the map-sectors in between the current packet and the previous packet.

        Args:
            packet1 (Packet): Primary packet object.
            packet2 (Packet): Previous packet object.

        Returns:
            list: Any related map sectors (as an array).
        """
        related_map_sectors = []
        distance = packet1.get_distance(packet2.latitude, packet2.longitude)
        if distance > 500000:
            # If the distance is longer than 500km, consider this station to be worldwide.
            related_map_sectors.append(99999999)
        else:
            min_lat, max_lat = sorted([packet1.latitude, packet2.latitude])
            min_lng, max_lng = sorted([packet1.longitude, packet2.longitude])

            map_sector_policy = MapSectorPolicy()
            min_lng = map_sector_policy.get_map_sector_lng_representation(min_lng)
            min_lat = map_sector_policy.get_map_sector_lat_representation(min_lat)
            max_lng = map_sector_policy.get_map_sector_lng_representation(max_lng + 0.5)
            max_lat = map_sector_policy.get_map_sector_lat_representation(max_lat + 0.2)
            prev_packet_area_code = map_sector_policy.get_map_sector(packet2.latitude, packet2.longitude)
            new_packet_area_code = map_sector_policy.get_map_sector(packet1.latitude, packet1.longitude)

            # lat interval: 0 - 18000000
            # lng interval: 0 - 00003600
            for lat in range(min_lat, max_lat, 20000):
                for lng in range(min_lng, max_lng, 5):
                    map_sector_area_code = lat + lng
                    if map_sector_area_code not in {prev_packet_area_code, new_packet_area_code}:
                        related_map_sectors.append(map_sector_area_code)
        return related_map_sectors