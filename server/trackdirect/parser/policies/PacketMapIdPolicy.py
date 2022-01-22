from trackdirect.parser.policies.PacketOrderPolicy import PacketOrderPolicy
from trackdirect.parser.policies.PacketMaxSpeedPolicy import PacketMaxSpeedPolicy


class PacketMapIdPolicy():
    """PacketMapIdPolicy tries to find the best mapId for the current packet
    """

    def __init__(self, packet, prevPacket):
        """The __init__ method.

        Args:
            packet (Packet):  Packet that we want analyze
        """
        self.packet = packet
        self.prevPacket = prevPacket
        self.hasKillCharacter = False
        # Marker will be confirmed when we receive the third packet
        self.markerCounterConfirmLimit = 3

        # Results
        self.mapId = None
        self.markerId = None
        self.isReplacingPrevPacket = False
        self.isConfirmingPrevPacket = False
        self.isKillingPrevPacket = False

    def enableHavingKillCharacter(self):
        """Treat this packet as having a kill character
        """
        self.hasKillCharacter = True

    def getMapId(self):
        """Returns the map id that corresponds to the found marker id

        Returns:
            int
        """
        self._findMapId()
        return self.mapId

    def getMarkerId(self):
        """Returns the found marker id

        Returns:
            int
        """
        self._findMapId()
        return self.markerId

    def isReplacingPreviousPacket(self):
        """Returns true if packet replaces previous packet

        Returns:
            boolean
        """
        self._findMapId()
        return self.isReplacingPrevPacket

    def isConfirmingPreviousPacket(self):
        """Returns true if packet confirmes previous packet

        Returns:
            boolean
        """
        self._findMapId()
        return self.isConfirmingPrevPacket

    def isKillingPreviousPacket(self):
        """Returns true if packet kills previous packet

        Returns:
            boolean
        """
        self._findMapId()
        return self.isKillingPrevPacket

    def _findMapId(self):
        """Find a suitable marker id for the current packet and set correponding attribute (and related attributes)
        """
        if (self.mapId is None):
            packetOrderPolicy = PacketOrderPolicy()
            if (self.packet.sourceId == 2 and len(self.packet.stationIdPath) > 0):
                # A CWOP-station is allways sending directly
                self.mapId = 16
                self.markerId = 1
            elif (not self._isPacketOnMap()):
                self.mapId = 10
                self.markerId = 1
            elif (packetOrderPolicy.isPacketInWrongOrder(self.packet, self.prevPacket)):
                self.mapId = 6
                self.markerId = 1
            elif (self._isFaultyGpsPosition()):
                self._findMapIdForFaultyGpsPosition()
            elif (self.packet.isMoving == 1):
                self._findMapIdForMovingStation()
            else:
                self._findMapIdForStationaryStation()

    def _isPacketOnMap(self):
        """Returns true if current packet will be on map

        Returns:
            boolean
        """
        if (self.packet.latitude is not None
                and self.packet.longitude is not None
                and type(self.packet.latitude) == float
                and type(self.packet.longitude) == float
                and self.packet.sourceId != 3
                and self.packet.mapId in [1, 5, 7, 9]):
            return True
        else:
            return False

    def _findMapIdForStationaryStation(self):
        """Find a suitable marker id for the current packet (assumes it is a stationary station) and set correponding attribute (and related attributes)
        """
        if (self.prevPacket.isExistingObject()
                and self.packet.isPostitionEqual(self.prevPacket)
                and self.packet.isSymbolEqual(self.prevPacket)
                and self.packet.isMoving == self.prevPacket.isMoving
                and self.prevPacket.mapId in [1, 7]):
            # Same position and same symbol
            self.mapId = 1
            self.markerId = self.prevPacket.markerId
            if (self.hasKillCharacter):
                # This station we can actually kill (it's stationary), let the markerId be
                self.mapId = 14

            # Also mark this to replace previous packet
            self.isReplacingPrevPacket = True
        elif (self.hasKillCharacter):
            # We found nothing to kill
            self.markerId = 1
            self.mapId = 4
        else:
            # Seems to be a new stationary station (or at least a new symbol for an existing station)
            self.mapId = 1
            self.markerId = None

    def _findMapIdForMovingStation(self):
        """Find a suitable marker id for the current packet (assumes it is a moving station) and set correponding attribute (and related attributes)
        """
        if (self.hasKillCharacter):
            # Makes no sense in handling kill characters for moving
            self.mapId = 4
            self.markerId = 1

        elif (self.prevPacket.isExistingObject()
                and self.prevPacket.isMoving == 1
                and self.prevPacket.mapId in [1, 7]):
            calculatedDistance = self.packet.getDistance(
                self.prevPacket.latitude, self.prevPacket.longitude)
            calculatedSpeed = self.packet.getCalculatedSpeed(self.prevPacket)
            packetMaxSpeedPolicy = PacketMaxSpeedPolicy()
            maxSpeed = packetMaxSpeedPolicy.getMaxLikelySpeed(
                self.packet, self.prevPacket)
            # distance is likely if distance is shorter than 50km (map performance is bad with to long polylines)
            absoluteMaxDistance = 50000
            # speed may be likely but if it is faster than absoluteMaxSpeed we create a new marker any way
            absoluteMaxSpeed = 2000

            if (self.packet.isPostitionEqual(self.prevPacket)):
                # Same position
                self._findMapIdForMovingStationWithSamePosition()

            elif (calculatedDistance < 5000 and calculatedSpeed <= absoluteMaxSpeed):
                # Distance is very short (shorter than 5km)
                self._findMapIdForMovingStationWithLikelySpeed()

            elif (calculatedSpeed <= maxSpeed and calculatedSpeed <= absoluteMaxSpeed and calculatedDistance <= absoluteMaxDistance):
                # Speed and distance is likely
                self._findMapIdForMovingStationWithLikelySpeed()

            elif (calculatedSpeed <= maxSpeed and calculatedDistance > absoluteMaxDistance):
                # Speed is likly but distance is to long or speed is very fast
                self._findMapIdForMovingStationWithToLongDistance()

            else:
                # No suitable marker id
                self.mapId = 7
                self.markerId = None
        else:
            if (self.prevPacket.isExistingObject()
                and self.prevPacket.isMoving == 0
                    and self.packet.isSymbolEqual(self.prevPacket)):
                # We previously made a mistake, previous packet should have been marked as moving, just mark previous as abnormal (ghost marker)
                self.isKillingPrevPacket = True

            # Seems to be a new station
            self.mapId = 1
            self.markerId = None

    def _findMapIdForMovingStationWithToLongDistance(self):
        """Sets a suitable marker id for the current packet based on prevPacket and assumes that distance is to long between them
        """
        if (self.prevPacket.markerCounter == 1):
            # Previous packet is not related to any previous and it is not related to this, mark it as abnormal
            self.isKillingPrevPacket = True

        # This is kind of a special case, we have no requirements on the previous packet
        # Station is either sending few packets or is moving very fast, we accept everything as long as speed is likely
        # Create new marker
        self.mapId = 1
        self.markerId = None

    def _findMapIdForMovingStationWithLikelySpeed(self):
        """Sets a suitable marker id for the current packet based on prevPacket and assumes that speed is likly
        """
        self.markerId = self.prevPacket.markerId
        if (self.prevPacket.mapId == 1
                or (self.prevPacket.markerCounter + 1) >= self.markerCounterConfirmLimit):
            self.mapId = 1
        else:
            self.mapId = self.prevPacket.mapId

        if (self.mapId == 1
                and self.prevPacket.mapId == 7):
            # To mark a previous packet as confirmed is not important since client should handle it anyway when a connected packet that is confirmed is recived
            # But we do it when possible to make things easier for the client (currently we are not doiong it if several previous packets is unconfirmed)
            self.isConfirmingPrevPacket = True

    def _findMapIdForMovingStationWithSamePosition(self):
        """Sets a suitable marker id for the current packet based on prevPacket and assumes that position is equal
        """
        # Also mark this to replace previous packet
        # If this packet is converted to a 12 it will be treated as confirmed in history
        # (we kind of assumes that markerCounterConfirmLimit == 2, maybe a TODO?)
        self.markerId = self.prevPacket.markerId
        self.isReplacingPrevPacket = True
        if (self.prevPacket.mapId == 1
                or (self.prevPacket.markerCounter + 1) >= self.markerCounterConfirmLimit):
            self.mapId = 1
        else:
            self.mapId = self.prevPacket.mapId

    def _findMapIdForFaultyGpsPosition(self):
        """Sets a suitable marker id for the current packet based on prevPacket and assumes that gps position is faulty (mapId 5)
        """
        if (self.hasKillCharacter):
            # No point in killing a ghost-marker
            self.mapId = 4
            self.markerId = 1
        elif (self.prevPacket.mapId == self.mapId
                and self.packet.isPostitionEqual(self.prevPacket)
                and self.packet.isSymbolEqual(self.prevPacket)):
            # Same mapId and position and same symbol
            # Also mark this to replace previous packet
            self.isReplacingPrevPacket = True
            self.mapId = 5  # it is still 5
            self.markerId = self.prevPacket.markerId
        else:
            # Seems to be a new stationary station (or at least a new symbol for an existing station)
            self.mapId = 5
            self.markerId = None

    def _isFaultyGpsPosition(self):
        """Parse the packet and modify the mapId attribute if position is faulty
        """
        packetlatCmp = int(round(self.packet.latitude*100000))
        packetlngCmp = int(round(self.packet.longitude*100000))

        if (packetlatCmp == int(0) and packetlngCmp == int(0)):
            return True

        if (packetlatCmp == int(1*100000) and packetlngCmp == int(1*100000)):
            return True

        if (packetlatCmp == int(36*100000) and packetlngCmp == int(136*100000)):
            # Some gps units seems to use this position as default until they find the real position
            # Maybe it is the position of a gps manufacturer?
            return True

        if (packetlatCmp == int(-48*100000) and packetlngCmp == int(0)):
            # Some gps units seems to use this position as default until they find the real position
            return True
        return False
