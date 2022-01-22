from trackdirect.parser.policies.PacketSpeedComputablePolicy import PacketSpeedComputablePolicy


class PacketMaxSpeedPolicy():
    """PacketMaxSpeedPolicy handles logic related to max possible speed (used to filter out faulty packets)
    """

    def __init__(self):
        """The __init__ method.
        """

    def getMaxLikelySpeed(self, packet, prevPacket):
        """Returns the max likely speed

        Args:
            packet (Packet):  Packet that we want analyze
            prevPacket (Packet):   Previous related packet for the same station

        Returns:
            Max likly speed as float
        """
        maxSpeed = self._getDefaultStationMaxSpeed(packet)

        if (packet.speed is not None and packet.speed > maxSpeed):
            # We allow 100% faster speed than the reported speed
            maxSpeed = packet.speed * 2

        if (prevPacket.isExistingObject()
                and prevPacket.speed is not None
                and prevPacket.speed > maxSpeed):
            # We allow 100% faster speed than the previous reported speed
            maxSpeed = prevPacket.speed * 2

        calculatedSpeed = 0
        if (prevPacket.isExistingObject()):
            calculatedSpeed = packet.getCalculatedSpeed(prevPacket)
        packetSpeedComputablePolicy = PacketSpeedComputablePolicy()
        if (packetSpeedComputablePolicy.isSpeedComputable(packet, prevPacket)
            and prevPacket.mapId == 7
                and calculatedSpeed > maxSpeed):
            # If last position is unconfirmed but still is closer to the last confirmed and calculated speed is trusted we accept that speed
            # This part is IMPORTANT to avoid that all packets get map_id == 7
            maxSpeed = calculatedSpeed

        maxSpeed = (maxSpeed * (1 + len(packet.stationIdPath)))
        return maxSpeed

    def _getDefaultStationMaxSpeed(self, packet):
        """Returns the station default max speed (not affected by or adaptive speed limit)

        Args:
            packet (Packet):  Packet that we want analyze

        Returns:
            Returns the station default max speed as int
        """
        # Bugatti Veyron Super Sport Record Edition 2010, the fastest production car can do 431 kmh (but a regular car usually drives a bit slower...)
        maxSpeed = 200
        if (packet.altitude is not None):
            highestLandAltitude = 5767  # Uturuncu, Bolivia, highest road altitude
            airPlaneMaxAltitude = 15240  # Very rare that airplanes go higher than 50.000 feet
            # Objects below approximately 160 kilometers (99 mi) will experience very rapid orbital decay and altitude loss.
            satelliteMinAltitude = 160000

            if (packet.altitude > satelliteMinAltitude):
                # Seems like this is an satellite
                # Until we know more we dont change anything
                maxSpeed = maxSpeed

            elif (packet.altitude > airPlaneMaxAltitude):
                # Higher than a normal airplane but not a satellite, could be a high altitude ballon
                maxSpeed = 50

            elif (packet.altitude > highestLandAltitude):
                # Seems like this is a airplane or a ballon
                # 394 kmh is the ground speed record for a hot air ballon
                # 950 kmh is a common upper crouse speed for regular airplanes
                maxSpeed = 950
        return maxSpeed
