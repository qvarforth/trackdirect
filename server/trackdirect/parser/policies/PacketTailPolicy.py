class PacketTailPolicy:
    """PacketTailPolicy handles logic related to packet tail id."""

    def __init__(self, packet, prev_packet):
        """
        The __init__ method.

        Args:
            packet (Packet):       Packet that we want to analyze
            prev_packet (Packet):  Previous related packet for the same station
        """
        self.packet = packet
        self.prev_packet = prev_packet
        self.packet_tail_timestamp = None

    def get_packet_tail_timestamp(self):
        """Returns the current packet tail timestamp."""
        if self.packet_tail_timestamp is None:
            self._find_packet_tail()
        return self.packet_tail_timestamp

    def _find_packet_tail(self):
        """Finds the current packet tail."""
        self.packet_tail_timestamp = self.packet.timestamp

        if not self.prev_packet.is_existing_object():
            return

        if not self.packet.is_position_equal(self.prev_packet):
            self.packet_tail_timestamp = self.packet.timestamp
            return

        if self.packet.is_moving == 0 and not self.packet.is_symbol_equal(self.prev_packet):
            self.packet_tail_timestamp = self.packet.timestamp
            return

        if self.packet_tail_timestamp == self.packet.timestamp:
            if self.prev_packet.packet_tail_timestamp < self.prev_packet.timestamp:
                db_max_age = 86400  # 1 day
                if self.prev_packet.packet_tail_timestamp > (self.packet.timestamp - db_max_age):
                    self.packet_tail_timestamp = self.prev_packet.timestamp