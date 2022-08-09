import time

from trackdirect.parser.policies.MapSectorPolicy import MapSectorPolicy


class PacketRelatedMapSectorsPolicy():
    """PacketRelatedMapSectorsPolicy handles logic related to map sectors for a packet
    """

    def __init__(self, packetRepository):
        """The __init__ method.

        Args:
            packetRepository (PacketRepository):   PacketRepository instance
        """
        self.packetRepository = packetRepository

    def getAllRelatedMapSectors(self, packet, previousPacket):
        """Returns all related map sectors to current packet

        Note:
            A related map sector is a map-sector that is not the map sector of the current packet nor the previous packet,
            it is all the map-sectors in between the current packet and the previous packet.

        Args:
            packet (Packet):         Packet that we want analyze
            previousPacket (Packet): Packet object that represents the previous packet for this station

        Returns:
            Returns any related map sectors (as an array)
        """
        if (not self._mayPacketHaveRelatedMapSectors(packet, previousPacket)):
            return []

        relatedMapSectors = []
        if (previousPacket.mapId == 7):
            # When previous packet is unconfirmed we need to add path between prev-prev-packet and prev-packet also
            minTimestamp = int(time.time()) - 86400  # 24 hours
            prevpreviousPacket = self.packetRepository.getLatestConfirmedMovingObjectByStationId(
                previousPacket.stationId, minTimestamp)
            if (prevpreviousPacket.isExistingObject() and prevpreviousPacket.markerCounter > 1):
                # We found a confirmed prev prev packet
                relatedMapSectors.extend(self._getRelatedMapSectors(
                    previousPacket, prevpreviousPacket))

        relatedMapSectors.extend(
            self._getRelatedMapSectors(packet, previousPacket))
        return relatedMapSectors

    def _mayPacketHaveRelatedMapSectors(self, packet,  previousPacket):
        """Returns true if packet may be related to other map sectors then the map sector it's in

        Args:
            packet (Packet):           Packet that we want analyze
            previousPacket (Packet):   Packet objekt that represents the previous packet for this station

        Returns:
            Returns true if packet may be related to other map sectors otherwise false
        """
        if (packet.isMoving == 1
                and previousPacket.isMoving == 1
                and packet.markerId != 1):
            # We only add related map-sectors to moving stations (that has a marker)
            if (packet.mapId == 1):
                # If new packet is not confirmed (mapId 7) we connect it with related map-sectors later
                if (previousPacket.markerCounter is not None and previousPacket.markerCounter > 1
                        or packet.markerId == previousPacket.markerId):
                    # We only add related map-sectors if previous packet has a marker with several connected packet
                    # A packet with a marker that is not shared with anyone will be converted to a ghost-marker in client
                    if (previousPacket.mapId == 1
                            or packet.markerId == previousPacket.markerId):
                        # If a previous packet has mapId = 7 (unconfirmed position),
                        # and new packet has another marker,
                        # then the previous marker is doomed to be a ghost-marker forever
                        return True
        return False

    def _getRelatedMapSectors(self, packet1, packet2):
        """Get any related map sectors between specified packets

        Note:
            A related map sector is a map-sector that is not the map sector of the current packet nor the previous packet,
            it is all the map-sectors in between the current packet and the previous packet.

        Args:
            packet1 (Packet):           Primary packet object
            packet2 (Packet):   Prvious packet object

        Returns:
            Returns any related map sectors (as an array)
        """
        relatedMapSectors = []
        distance = calculatedDistance = packet1.getDistance(
            packet2.latitude, packet2.longitude)
        if (distance > 500000):
            # if distance is longer than 500km, we consider this station to be world wide...
            # but currently we do not use this information since it would affect performance to much
            # but it is extremly few stations that actually is affected by this (about 0-2 stations)
            relatedMapSectors.append(99999999)
        else:
            minLat = packet2.latitude
            maxLat = packet1.latitude
            minLng = packet2.longitude
            maxLng = packet1.longitude

            if (maxLat < minLat):
                minLat = packet1.latitude
                maxLat = packet2.latitude
            if (maxLng < minLng):
                minLng = packet1.longitude
                maxLng = packet2.longitude

            mapSectorPolicy = MapSectorPolicy()
            minLng = mapSectorPolicy.getMapSectorLngRepresentation(minLng)
            minLat = mapSectorPolicy.getMapSectorLatRepresentation(minLat)
            maxLng = mapSectorPolicy.getMapSectorLngRepresentation(
                maxLng + 0.5)
            maxLat = mapSectorPolicy.getMapSectorLatRepresentation(
                maxLat + 0.2)
            prevPacketAreaCode = mapSectorPolicy.getMapSector(
                packet2.latitude, packet2.longitude)
            newPacketAreaCode = mapSectorPolicy.getMapSector(
                packet1.latitude, packet1.longitude)

            # lat interval: 0 - 18000000
            # lng interval: 0 - 00003600
            # Maybe we can do this smarter? Currently we are adding many map-sectors that is not relevant
            for lat in range(minLat, maxLat, 20000):
                for lng in range(minLng, maxLng, 5):
                    mapSectorAreaCode = lat+lng
                    if (mapSectorAreaCode != prevPacketAreaCode and mapSectorAreaCode != newPacketAreaCode):
                        relatedMapSectors.append(mapSectorAreaCode)
        return relatedMapSectors
