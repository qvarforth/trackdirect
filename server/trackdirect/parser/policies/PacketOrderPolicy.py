class PacketOrderPolicy():
    """PacketOrderPolicy handles logic related to packet receive order
    """

    def __init__(self):
        """The __init__ method.
        """

    def isPacketInWrongOrder(self, packet, previousPacket):
        """Checks if current packet is received in the wrong order compared to the previous specified packet

        Note:
            We only care for packets in wrong order if station is moving

        Args:
            packet (Packet):          Packet that we want analyze
            previousPacket (Packet):  Packet objekt that represents the previous packet for this station

        Returns:
            True if this packet is received in the wrong order otherwise false
        """
        if (previousPacket is not None
                and previousPacket.isExistingObject()):
            if (previousPacket.reportedTimestamp is not None
                    and packet.reportedTimestamp is not None
                    and previousPacket.reportedTimestamp != 0
                    and previousPacket.senderId == packet.senderId
                    and packet.reportedTimestamp != 0
                    and previousPacket.isMoving == 1
                    and previousPacket.reportedTimestamp < (packet.timestamp + 60*60*24)
                    and packet.reportedTimestamp < (packet.timestamp + 60*60*24)
                    and previousPacket.reportedTimestamp > packet.reportedTimestamp):
                return True
        return False
