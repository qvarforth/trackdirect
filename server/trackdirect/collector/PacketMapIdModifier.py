import logging
from twisted.python import log
import psycopg2
import psycopg2.extras

from trackdirect.database.PacketTableCreator import PacketTableCreator
from trackdirect.exceptions.TrackDirectMissingTableError import TrackDirectMissingTableError


class PacketMapIdModifier():
    """PacketMapIdModifier is used to modify mapId on existing packets in database based on new packets
    """

    def __init__(self, cur, packetTableCreator):
        """The __init__ method.

        Args:
            cur (psycopg2.Cursor):                      Database cursor
            packetTableCreator (PacketTableCreator):    PacketTableCreator instance
        """
        self.cur = cur
        self.packetTableCreator = packetTableCreator

    def execute(self, packets):
        """Perform mapId mofifications based on information in specified packets

        Args:
            packets (array):  Packets that may affect exisintg packets mapId
            cur (cursor):     Database curser to use
        """
        self._markPreviousPacketsAsReplaced(packets)
        self._markPreviousPacketsAsAbnormal(packets)
        self._markPreviousPacketsAsConfirmed(packets)

    def _markPreviousPacketsAsReplaced(self, packets):
        """Find packets that has been replaced by packets in this batch and mark them as replaced (mapId 2, 12 or 13)

        Args:
            packets (array):  Packets that may affect exisintg packets mapId
        """
        packetsToUpdateToMapId2 = {}
        packetsToUpdateToMapId12 = {}
        packetsToUpdateToMapId13 = {}
        for packet in packets:
            if (packet.replacePacketId is not None):
                try:
                    self.packetTableCreator.enableCreateIfMissing()
                    newPacketTable = self.packetTableCreator.getPacketTable(
                        packet.timestamp)
                    self.packetTableCreator.disableCreateIfMissing()
                    oldPacketTable = self.packetTableCreator.getPacketTable(
                        packet.replacePacketTimestamp)

                    if (packet.mapId == 5):
                        if (oldPacketTable not in packetsToUpdateToMapId13):
                            packetsToUpdateToMapId13[oldPacketTable] = []

                        packetsToUpdateToMapId13[oldPacketTable].append(
                            packet.replacePacketId)

                    elif (newPacketTable == oldPacketTable):
                        if (oldPacketTable not in packetsToUpdateToMapId2):
                            packetsToUpdateToMapId2[oldPacketTable] = []

                        packetsToUpdateToMapId2[oldPacketTable].append(
                            packet.replacePacketId)

                    else:
                        if (oldPacketTable not in packetsToUpdateToMapId12):
                            packetsToUpdateToMapId12[oldPacketTable] = []

                        packetsToUpdateToMapId12[oldPacketTable].append(
                            packet.replacePacketId)
                except TrackDirectMissingTableError as e:
                    pass

        if (packetsToUpdateToMapId2):
            for packetTable in packetsToUpdateToMapId2:
                # Set map_id = 2
                self._updatePacketMapId(
                    packetTable, packetsToUpdateToMapId2[packetTable], 2)

        if (packetsToUpdateToMapId12):
            for packetTable in packetsToUpdateToMapId12:
                # Set map_id = 12
                self._updatePacketMapId(
                    packetTable, packetsToUpdateToMapId12[packetTable], 12)

        if (packetsToUpdateToMapId13):
            for packetTable in packetsToUpdateToMapId13:
                # Set map_id = 13
                self._updatePacketMapId(
                    packetTable, packetsToUpdateToMapId13[packetTable], 13)

    def _markPreviousPacketsAsAbnormal(self, packets):
        """Find packets that has been confirmed to by abnormal becuse of packets in this batch and mark them as abnormal (mapId 9)

        Args:
            packets (array):  Packets that may affect exisintg packets mapId
        """
        packetsToUpdate = {}
        for packet in packets:
            if (packet.abnormalPacketId is not None):
                try:
                    self.packetTableCreator.disableCreateIfMissing()
                    packetTable = self.packetTableCreator.getPacketTable(
                        packet.abnormalPacketTimestamp)

                    if (packetTable not in packetsToUpdate):
                        packetsToUpdate[packetTable] = []

                    packetsToUpdate[packetTable].append(
                        packet.abnormalPacketId)
                except TrackDirectMissingTableError as e:
                    pass

        if (packetsToUpdate):
            for packetTable in packetsToUpdate:
                # Set map_id = 9
                self._updatePacketMapId(
                    packetTable, packetsToUpdate[packetTable], 9)

    def _markPreviousPacketsAsConfirmed(self, packets):
        """Find packets that has been found to be correct becuase of packets in this batch and mark them as confirmed (mapId 1)

        Args:
            packets (array):  Packets that may affect exisintg packets mapId
            cur (cursor):     Database curser to use
        """
        packetsToUpdate = {}
        for packet in packets:
            if (packet.confirmPacketId is not None):
                try:
                    self.packetTableCreator.disableCreateIfMissing()
                    packetTable = self.packetTableCreator.getPacketTable(
                        packet.confirmPacketTimestamp)

                    if (packetTable not in packetsToUpdate):
                        packetsToUpdate[packetTable] = []

                    packetsToUpdate[packetTable].append(packet.confirmPacketId)
                except TrackDirectMissingTableError as e:
                    pass

        if (packetsToUpdate):
            for packetTable in packetsToUpdate:
                # Set map_id = 1
                self._updatePacketMapId(
                    packetTable, packetsToUpdate[packetTable], 1)

    def _updatePacketMapId(self, packetTable, packetIdList, mapId):
        """Update map id on all specified packets

        Args:
            cur (cursor):          Database cursor to use
            packetTable (str):     Packet database table to perform update on
            packetIdList (array):  Array of all packet id's to update
            mapId (int):           The requested new map id
        """
        if (packetIdList):
            sql = self.cur.mogrify("""update """ + packetTable + """
                set map_id = %s
                where id in %s""", (mapId, tuple(packetIdList),))
            self.cur.execute(sql)
