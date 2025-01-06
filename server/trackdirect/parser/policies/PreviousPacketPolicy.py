import time
from server.trackdirect.parser.policies.PacketAssumedMoveTypePolicy import PacketAssumedMoveTypePolicy
from server.trackdirect.parser.policies.PacketOrderPolicy import PacketOrderPolicy
from server.trackdirect.repositories.PacketRepository import PacketRepository
from server.trackdirect.repositories.StationRepository import StationRepository


class PreviousPacketPolicy:
    """The PreviousPacketPolicy class tries to find the most related previous packet for the same station."""

    def __init__(self, packet, db):
        """
        Initialize the PreviousPacketPolicy.

        Args:
            packet (Packet): Packet for which we want to find the most related previous packet.
            db (psycopg2.Connection): Database connection.
        """
        self.db = db
        self.packet = packet
        self.packet_repository = PacketRepository(db)
        self.station_repository = StationRepository(db)

    def get_previous_packet(self):
        """
        Try to find the previous packet for the specified packet.

        Returns:
            Packet: The most related previous packet.
        """
        if not self._may_packet_have_previous_packet():
            return self.packet_repository.create()

        min_timestamp = int(time.time()) - 86400  # 24 hours
        latest_previous_packet = self.packet_repository.get_latest_object_by_station_id(self.packet.station_id, min_timestamp)

        if not latest_previous_packet.is_existing_object():
            return latest_previous_packet

        if self.packet.map_id == 5:
            return self._get_best_previous_packet_for_faulty_gps_packet(latest_previous_packet)
        else:
            packet_assumed_move_type_policy = PacketAssumedMoveTypePolicy(self.db)
            is_moving = packet_assumed_move_type_policy.get_assumed_move_type(self.packet, latest_previous_packet)
            if is_moving == 1:
                return self._get_best_previous_packet_for_moving_station(latest_previous_packet, min_timestamp)
            else:
                return self._get_best_previous_packet_for_stationary_station(latest_previous_packet)

    def _may_packet_have_previous_packet(self):
        """
        Check if the current packet is ready for previous packet calculation.

        Returns:
            bool: True if the packet is ready, otherwise False.
        """
        return (
                self.packet.latitude is not None
                and self.packet.longitude is not None
                and isinstance(self.packet.latitude, float)
                and isinstance(self.packet.longitude, float)
                and self.packet.source_id != 3
                and self.packet.map_id in [1, 5, 7, 9]
        )

    def _get_best_previous_packet_for_faulty_gps_packet(self, latest_previous_packet):
        """
        Find the previous packet that is best related to the current packet for faulty GPS packets.

        Args:
            latest_previous_packet (Packet): The latest previous packet for this station.

        Returns:
            Packet: The best related previous packet.
        """
        if (
            latest_previous_packet.map_id != self.packet.map_id
            or not self.packet.is_position_equal(latest_previous_packet)
            or not self.packet.is_symbol_equal(latest_previous_packet)
        ):
            prev_packet_same_pos = self.packet_repository.get_latest_object_by_station_id_and_position(
                self.packet.station_id,
                self.packet.latitude,
                self.packet.longitude,
                [self.packet.map_id],
                self.packet.symbol,
                self.packet.symbol_table,
                self.packet.timestamp - 86400
            )
            if prev_packet_same_pos.is_existing_object():
                return prev_packet_same_pos
        return latest_previous_packet

    def _get_best_previous_packet_for_stationary_station(self, latest_previous_packet):
        """
        Find the previous packet that is best related to the current packet for stationary stations.

        Args:
            latest_previous_packet (Packet): The latest previous packet for this station.

        Returns:
            Packet: The best related previous packet.
        """
        if (
            not self.packet.is_position_equal(latest_previous_packet)
            or not self.packet.is_symbol_equal(latest_previous_packet)
            or self.packet.is_moving != latest_previous_packet.is_moving
            or latest_previous_packet.map_id not in [1, 7]
        ):
            previous_packet_same_pos = self.packet_repository.get_latest_object_by_station_id_and_position(
                self.packet.station_id,
                self.packet.latitude,
                self.packet.longitude,
                [1, 7],
                self.packet.symbol,
                self.packet.symbol_table,
                self.packet.timestamp - 86400
            )
            if previous_packet_same_pos.is_existing_object():
                return previous_packet_same_pos
        return latest_previous_packet

    def _get_best_previous_packet_for_moving_station(self, latest_previous_packet, min_timestamp):
        """
        Find the previous packet that is best related to the current packet for moving stations.

        Args:
            latest_previous_packet (Packet): The latest previous packet for this station.
            min_timestamp (int): The oldest accepted timestamp (Unix timestamp).

        Returns:
            Packet: The best related previous packet.
        """
        previous_packet = latest_previous_packet
        if (
            previous_packet.is_existing_object()
            and (previous_packet.is_moving != 1 or previous_packet.map_id not in [1, 7])
        ):
            prev_moving_packet = self.packet_repository.get_latest_moving_object_by_station_id(
                self.packet.station_id, min_timestamp)
            if prev_moving_packet.is_existing_object():
                previous_packet = prev_moving_packet

        packet_order_policy = PacketOrderPolicy()
        if (
            previous_packet.is_existing_object()
            and previous_packet.is_moving == 1
            and previous_packet.map_id == 7
            and not packet_order_policy.is_packet_in_wrong_order(self.packet, previous_packet)
        ):
            prev_confirmed_packet = self.packet_repository.get_latest_confirmed_moving_object_by_station_id(
                self.packet.station_id, min_timestamp)
            previous_packet = self._get_closest_packet_object(previous_packet, prev_confirmed_packet)

        return previous_packet

    def _get_closest_packet_object(self, previous_packet1, previous_packet2):
        """
        Return the packet closest to the current position.

        Args:
            previous_packet1 (Packet): One previous packet for the current station.
            previous_packet2 (Packet): Another previous packet for the current station.

        Returns:
            Packet: The closest packet to the current position.
        """
        if not previous_packet1.is_existing_object():
            return previous_packet2

        if not previous_packet2.is_existing_object():
            return previous_packet1

        prev_packet1_distance = self.packet.get_distance(previous_packet1.latitude, previous_packet1.longitude)
        prev_packet2_distance = self.packet.get_distance(previous_packet2.latitude, previous_packet2.longitude)

        return previous_packet2 if prev_packet2_distance < prev_packet1_distance else previous_packet1