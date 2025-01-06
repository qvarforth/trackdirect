class PacketOrderPolicy:
    """PacketOrderPolicy handles logic related to packet receive order
    """

    def __init__(self):
        """The __init__ method.
        """
        pass

    def is_packet_in_wrong_order(self, packet, previous_packet):
        """Checks if current packet is received in the wrong order compared to the previous specified packet

        Note:
            We only care for packets in wrong order if station is moving

        Args:
            packet (Packet):          Packet that we want to analyze
            previous_packet (Packet):  Packet object that represents the previous packet for this station

        Returns:
            True if this packet is received in the wrong order otherwise false
        """
        if not self._is_valid_previous_packet(previous_packet, packet):
            return False

        if self._is_station_moving(previous_packet) and self._is_timestamp_in_wrong_order(previous_packet, packet):
            return True

        return False

    def _is_valid_previous_packet(self, previous_packet, packet):
        """Checks if the previous packet is valid for comparison"""
        return (previous_packet is not None
                and previous_packet.is_existing_object()
                and previous_packet.reported_timestamp is not None
                and packet.reported_timestamp is not None
                and previous_packet.reported_timestamp != 0
                and packet.reported_timestamp != 0
                and previous_packet.sender_id == packet.sender_id)

    def _is_station_moving(self, previous_packet):
        """Checks if the station is moving"""
        return previous_packet.is_moving == 1

    def _is_timestamp_in_wrong_order(self, previous_packet, packet):
        """Checks if the timestamps indicate the packets are in the wrong order"""
        return (previous_packet.reported_timestamp < (packet.timestamp + 60 * 60 * 24)
                and packet.reported_timestamp < (packet.timestamp + 60 * 60 * 24)
                and previous_packet.reported_timestamp > packet.reported_timestamp)