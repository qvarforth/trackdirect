class PacketSpeedComputablePolicy():
    """PacketSpeedComputablePolicy handles logic related to parameters that may cause errors in speed calculations
    """

    def __init__(self):
        """The __init__ method.
        """

    def isSpeedComputable(self, packet, prevPacket):
        """Returns true if speed is possible to calculate in a way that we can trust it

        Args:
            packet (Packet):        Packet that we want to know move typ for
            prevPacket (Packet):    Previous related packet for the same station

        Returns:
            Returns true if speed is possible to calculate
        """
        if (packet is None
                or prevPacket is None
                or prevPacket.isMoving != 1
                or prevPacket.mapId not in [1, 7]
                or packet.markerId == 1
                or packet.isMoving != 1):
            return False

        if (packet.reportedTimestamp is not None
                and prevPacket.reportedTimestamp is not None
                and packet.reportedTimestamp != 0
                and prevPacket.reportedTimestamp != 0
                and (packet.reportedTimestamp % 60 != 0 or prevPacket.reportedTimestamp % 60 != 0)
                and prevPacket.reportedTimestamp != packet.reportedTimestamp):
            return True
        else:
            calculatedDistance = packet.getDistance(
                prevPacket.latitude, prevPacket.longitude)
            if (len(packet.stationIdPath) < 1):
                # Packet was sent through internet, delay should be small
                return True
            elif (len(packet.stationIdPath) <= 1 and calculatedDistance > 5000):
                # Packet has not been digipeated (delay should not be extreme)
                # and distance is longer than 5km
                return True
            else:
                # Packet was digipeated (delay can be very long)
                # or distance was short, calculated speed can not be trusted
                return False
