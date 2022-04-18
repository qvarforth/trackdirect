import logging
from twisted.python import log

import collections
from trackdirect.exceptions.TrackDirectParseError import TrackDirectParseError


class PacketDuplicatePolicy():
    """Handles duplicate checks
    """

    # static class variables
    latestPacketsHashOrderedDict = collections.OrderedDict()

    def __init__(self, stationRepository):
        """The __init__ method.
        """
        self.minutesBackToLookForDuplicates = 30
        self.stationRepository = stationRepository

        self.logger = logging.getLogger('trackdirect')

    def isDuplicate(self, packet):
        """Method used to check if this packet is a duplicate

        Args:
            packet (Packet): Packet that may be a duplicate

        Returns:
            Boolean
        """
        if (packet.mapId in [1, 5, 7, 8, 9]
                and (packet.isMoving == 1 or packet.mapId == 8)
                and packet.latitude is not None
                and packet.longitude is not None):
            if (self._isPacketBodyInCache(packet)):
                # It looks like a duplicate, treat it as one if needed
                # (if position is equal to the latest confirmed position it doesn't matter if we treat it as a duplicate or not)
                if (self._isToBeTreateAsDuplicate(packet)):
                    return True
            self._addToCache(packet)

        elif (packet.sourceId == 3):
            # It is a duplicate (everything from this source is)
            return True

        return False

    def _isPacketBodyInCache(self, packet):
        """Returns true if packet body is in cache

        Args:
            packet (Packet):   Packet look for in cashe

        Returns:
            Boolean
        """
        packetHash = self._getPacketHash(packet)
        if (packetHash is None):
            return False

        if (packetHash in PacketDuplicatePolicy.latestPacketsHashOrderedDict):
            prevPacketValues = PacketDuplicatePolicy.latestPacketsHashOrderedDict[packetHash]
            if (packet.rawPath != prevPacketValues['path']
                    and prevPacketValues['timestamp'] > packet.timestamp - (60*self.minutesBackToLookForDuplicates)):
                return True
        return False

    def _isToBeTreateAsDuplicate(self, packet):
        """Returns true if packet should be treated as duplicate

        Args:
            packet (Packet):   Packet to check

        Returns:
            Boolean
        """
        station = self.stationRepository.getObjectById(packet.stationId)
        if (station.latestConfirmedLatitude is not None and station.latestConfirmedLongitude is not None):
            stationLatCmp = int(round(station.latestConfirmedLatitude*100000))
            stationLngCmp = int(round(station.latestConfirmedLongitude*100000))
        else:
            stationLatCmp = 0
            stationLngCmp = 0

        packetlatCmp = int(round(packet.latitude*100000))
        packetlngCmp = int(round(packet.longitude*100000))

        if (station.isExistingObject()
            and stationLatCmp != 0
            and stationLngCmp != 0
                and (packet.mapId == 8 or stationLatCmp != packetlatCmp or stationLngCmp != packetlngCmp)):

            # We treat this packet as a duplicate
            return True
        else:
            return False

    def _getPacketHash(self, packet):
        """Returns a hash value of the Packet object

        Args:
            packet (Packet): Packet to get hash for

        Returns:
            A string that contains the hash value
        """
        if (packet.raw is None or packet.raw == ''):
            return None

        packetString = packet.raw.split(':', 1)[1]
        if (packetString == ''):
            return None
        else:
            return hash(packetString.strip())

    def _addToCache(self, packet):
        """Add packet to cache

        Args:
            packet (Packet):  Packet to add to cache
        """
        packetHash = self._getPacketHash(packet)
        PacketDuplicatePolicy.latestPacketsHashOrderedDict[packetHash] = {
            'path': packet.rawPath,
            'timestamp': packet.timestamp
        }
        self._cacheMaintenance()

    def _cacheMaintenance(self):
        """Make sure cache does not contain to many packets
        """
        maxNumberOfPackets = self.minutesBackToLookForDuplicates * 60 * 100 # We assume that we have an average of 100 packets per second
        if (len(PacketDuplicatePolicy.latestPacketsHashOrderedDict) > maxNumberOfPackets):
            try:
                PacketDuplicatePolicy.latestPacketsHashOrderedDict.popitem(
                    last=False)
            except (KeyError, StopIteration) as e:
                pass
