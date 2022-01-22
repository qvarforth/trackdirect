class PacketTailPolicy():
    """PacketTailPolicy handles logic related to packet tail id
    """

    def __init__(self, packet, prevPacket):
        """The __init__ method.

        Args:
            packet (Packet):       Packet that we want analyze
            prevPacket (Packet):   Previous related packet for the same station
        """
        self.packet = packet
        self.prevPacket = prevPacket
        self.packetTailTimestamp = None

    def getPacketTailTimestamp(self):
        """Returns the current packet tail timestamp
        """
        if (self.packetTailTimestamp is None):
            self._findPacketTail()
        return self.packetTailTimestamp

    def _findPacketTail(self):
        """Finds the current packet tail
        """
        self.packetTailTimestamp = self.packet.timestamp

        if (self.prevPacket.isExistingObject()):
            # The packet_tail_id is used to get a faster map, no need to fetch older packets if a station has no tail.
            # It's not a big problem if packet_tail_id is "Has tail" but no tail exists (the opposite is worse)
            if (not self.packet.isPostitionEqual(self.prevPacket)):
                # Both moving and stationary has tail if packet with other position exists
                self.packetTailTimestamp = self.packet.timestamp

            if (self.packet.isMoving == 0 and not self.packet.isSymbolEqual(self.prevPacket)):
                # Stationary packet also has a tail if another symbol exists on same position
                self.packetTailTimestamp = self.packet.timestamp

            if (self.packetTailTimestamp == self.packet.timestamp):
                # We have not found any tail yet
                if (self.prevPacket.packetTailTimestamp < self.prevPacket.timestamp):
                    # prevous packet has a tail
                    dbMaxAge = 86400  # 1 day
                    if (self.prevPacket.packetTailTimestamp > (self.packet.timestamp - dbMaxAge)):
                        # Previous packet indicates that we have a tail and tail is not to old
                        self.packetTailTimestamp = self.prevPacket.timestamp
