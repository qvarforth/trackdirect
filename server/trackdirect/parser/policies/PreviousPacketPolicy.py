import logging
from twisted.python import log
import datetime
import time

from trackdirect.parser.policies.PacketAssumedMoveTypePolicy import PacketAssumedMoveTypePolicy
from trackdirect.parser.policies.PacketOrderPolicy import PacketOrderPolicy

from trackdirect.repositories.PacketRepository import PacketRepository
from trackdirect.repositories.StationRepository import StationRepository


class PreviousPacketPolicy():
    """The PreviousPacketPolicy class tries to find the most related previous packet for the same station
    """

    def __init__(self, packet, db):
        """The __init__ method.

        Args:
            packet (Packet):             Packet for that we want to find previous most related packet
            db (psycopg2.Connection):    Database connection
        """
        self.db = db
        self.packet = packet
        self.packetRepository = PacketRepository(db)
        self.stationRepository = StationRepository(db)

    def getPreviousPacket(self):
        """Tries to find the previous packet for the specified packet

        Returns:
            Packet
        """
        if (not self._mayPacketHavePreviousPacket()):
            return self.packetRepository.create()

        minTimestamp = int(time.time()) - 86400  # 24 hours
        latestPreviousPacket = self.packetRepository.getLatestObjectByStationId(self.packet.stationId, minTimestamp)

        if (not latestPreviousPacket.isExistingObject()):
            return latestPreviousPacket

        if (self.packet.mapId == 5):
            return self._getBestPreviousPacketForFaultyGpsPacket(latestPreviousPacket)
        else:
            packetAssumedMoveTypePolicy = PacketAssumedMoveTypePolicy(self.db)
            isMoving = packetAssumedMoveTypePolicy.getAssumedMoveType(self.packet, latestPreviousPacket)
            if (isMoving == 1):
                return self._getBestPreviousPacketForMovingStation(latestPreviousPacket, minTimestamp)
            else:
                return self._getBestPreviousPacketForStationaryStation(latestPreviousPacket)

    def _mayPacketHavePreviousPacket(self):
        """Returns true if current packet is ready for previous packet calculation

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

    def _getBestPreviousPacketForFaultyGpsPacket(self, latestPreviousPacket):
        """Find the previous packet that is best related to the current packet

        Args:
            latestPreviousPacket (Packet):  Packet object that represents the latest previous packet for this station

        Returns:
            Packet
        """
        if (latestPreviousPacket.mapId != self.packet.mapId
                or not self.packet.isPostitionEqual(latestPreviousPacket)
                or not self.packet.isSymbolEqual(latestPreviousPacket)):
            # Try to find prev packet
            prevPacketSamePos = self.packetRepository.getLatestObjectByStationIdAndPosition(
                self.packet.stationId,
                self.packet.latitude,
                self.packet.longitude,
                [self.packet.mapId],
                self.packet.symbol,
                self.packet.symbolTable,
                self.packet.timestamp - 86400
            )
            if (prevPacketSamePos.isExistingObject()):
                return prevPacketSamePos
        return latestPreviousPacket

    def _getBestPreviousPacketForStationaryStation(self, latestPreviousPacket):
        """Find the previous packet that is best related to the current packet

        Args:
            latestPreviousPacket (Packet):  Packet object that represents the latest previous packet for this station

        Returns:
            Packet
        """
        if (not self.packet.isPostitionEqual(latestPreviousPacket)
                or not self.packet.isSymbolEqual(latestPreviousPacket)
                or self.packet.isMoving != latestPreviousPacket.isMoving
                or latestPreviousPacket.mapId not in [1, 7]):
            # Try to find stationary marker for packet position
            previousPacketSamePos = self.packetRepository.getLatestObjectByStationIdAndPosition(
                self.packet.stationId,
                self.packet.latitude,
                self.packet.longitude,
                [1, 7],
                self.packet.symbol,
                self.packet.symbolTable,
                self.packet.timestamp - 86400
            )
            if (previousPacketSamePos.isExistingObject()):
                return previousPacketSamePos
        return latestPreviousPacket

    def _getBestPreviousPacketForMovingStation(self, latestPreviousPacket, minTimestamp):
        """Find the previous packet that is best related to the current packet

        Args:
            latestPreviousPacket (Packet):  Packet object that represents the latest previous packet for this station
            minTimestamp (int):             Oldest accepted timestamp (Unix timestamp)

        Returns:
            Packet
        """
        previousPacket = latestPreviousPacket
        if (previousPacket.isExistingObject()
                and (previousPacket.isMoving != 1
                     or previousPacket.mapId not in [1, 7])):
            # Current packet is assumed moving but previous is stationary, try to find last moving instead
            prevMovingPacket = self.packetRepository.getLatestMovingObjectByStationId(
                self.packet.stationId, minTimestamp)
            if (prevMovingPacket.isExistingObject()):
                previousPacket = prevMovingPacket

        packetOrderPolicy = PacketOrderPolicy()
        if (previousPacket.isExistingObject()
                and previousPacket.isMoving == 1
                and previousPacket.mapId == 7
                and not packetOrderPolicy.isPacketInWrongOrder(self.packet, previousPacket)):
            # previousPacket is not confirmed (see if we have a better alternative)
            prevConfirmedPacket = self.packetRepository.getLatestConfirmedMovingObjectByStationId(
                self.packet.stationId, minTimestamp)
            previousPacket = self._getClosestPacketObject(
                previousPacket, prevConfirmedPacket)

        return previousPacket

    def _getClosestPacketObject(self, previousPacket1, previousPacket2):
        """Returns the packet closest to the current position

        Args:
            previousPacket1 (Packet):  Packet object that represents one previous packet for current station
            previousPacket2 (Packet):  Packet object that represents one previous packet for current station

        Returns:
            Packet
        """
        if (not previousPacket1.isExistingObject()):
            return previousPacket2

        if (not previousPacket2.isExistingObject()):
            return previousPacket1

        prevPacket1CalculatedDistance = self.packet.getDistance(
            previousPacket1.latitude, previousPacket1.longitude)
        prevPacket2CalculatedDistance = self.packet.getDistance(
            previousPacket2.latitude, previousPacket2.longitude)

        if (prevPacket2CalculatedDistance < prevPacket1CalculatedDistance):
            return previousPacket2
        else:
            return previousPacket1
