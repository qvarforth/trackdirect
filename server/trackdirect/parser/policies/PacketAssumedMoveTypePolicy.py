from trackdirect.parser.policies.AprsPacketSymbolPolicy import AprsPacketSymbolPolicy
from trackdirect.database.PacketTableCreator import PacketTableCreator


class PacketAssumedMoveTypePolicy():
    """PacketAssumedMoveTypeIdPolicy calculates a packets default move type
    """

    def __init__(self, db):
        """The __init__ method.

        Args:
            db (psycopg2.Connection): Database connection
        """
        self.db = db

    def getAssumedMoveType(self, packet, prevPacket):
        """Returns the current packet move type based on if it seems to be moving or not

        Args:
            packet (Packet):       Packet that we want to know move typ for
            prevPacket (Packet):   Previous related packet for the same station

        Returns:
            Returns the current packet move type id as integer
        """
        isMoving = self._getDefaultAssumedMoveType(packet)
        if (prevPacket.isExistingObject()
                and isMoving == 0
                and not self._isBalloonPredictedTouchdown(packet)):
            aprsPacketSymbolPolicy = AprsPacketSymbolPolicy()

            # If assumed stationary we validate this by comparing to previous packet
            if (packet.isSymbolEqual(prevPacket)
                    and (prevPacket.timestamp - prevPacket.positionTimestamp) < 36000
                    and prevPacket.isMoving == 1):
                # Previous packet has same symbol and is moving
                # (If previous was moving so should this)
                isMoving = 1

            elif (aprsPacketSymbolPolicy.isMaybeMovingSymbol(packet.symbol, packet.symbolTable)
                    and prevPacket.isMoving == 1):
                # symbol that maybe is moving is considered moving if prev packet is moving
                isMoving = 1

            elif (packet.isSymbolEqual(prevPacket)
                    and not packet.isPostitionEqual(prevPacket)):
                # Previous packet has same symbol and another position
                isMoving = 1

            elif (not packet.isPostitionEqual(prevPacket)):
                # Previous packet has another symbol and another position
                # In this case we do a deper investigation... (this is to heavy to do for all packets)
                numberOfPackets = self._getNumberOfPacketWithSameSymbolAndOtherPos(
                    packet, packet.timestamp - 86400
                )

                if (numberOfPackets > 0):
                    # We have more then 1 positions for this symbol from this station, assume it is moving
                    isMoving = 1
        return isMoving

    def _isBalloonPredictedTouchdown(self, packet):
        """Returns true if packet probably is a balloon touchdown

        Args:
            packet (Packet):  Packet that we want to know move typ for

        Returns:
            true if packet probably is a balloon touchdown otherwise false
        """
        if (packet.symbolTable != "/" and packet.symbol == "o"):
            # Symbol is a small circle often used as predicted touchdown
            if (packet.comment is not None and "touchdown" in packet.comment):
                return True
        return False

    def _getDefaultAssumedMoveType(self, packet):
        """Returns the default packet move type id

        Args:
            packet (Packet):  Packet that we want to know move typ for

        Returns:
            Returns the default packet move type id as integer
        """
        # Default is moving and if we are not sure we should choose moving
        isMoving = 1
        if (packet is not None
                and packet.symbol is not None
                and packet.symbolTable is not None):
            # First we set a initial value based on symbol
            aprsPacketSymbolPolicy = AprsPacketSymbolPolicy()
            if (aprsPacketSymbolPolicy.isStationarySymbol(packet.symbol, packet.symbolTable)
                    or aprsPacketSymbolPolicy.isMaybeMovingSymbol(packet.symbol, packet.symbolTable)):
                isMoving = 0
            if (isMoving == 0 and self._isSsidIndicateMoving(packet.stationName)
                    and aprsPacketSymbolPolicy.isMaybeMovingSymbol(packet.symbol, packet.symbolTable)):
                isMoving = 1
            if (isMoving == 0
                    and (packet.course is not None or packet.speed is not None)
                    and packet.packetTypeId != 3):
                # Packet has a speed and a course and is not a weather packet!
                # If it looks like a weather station we validate that speed is higher than 0
                if (aprsPacketSymbolPolicy.isMaybeMovingSymbol(packet.symbol, packet.symbolTable)):
                    isMoving = 1
                elif (self._isSsidIndicateMoving(packet.stationName)):
                    isMoving = 1
                elif (packet.speed is not None and packet.speed > 0):
                    # A moving stationary station?!
                    isMoving = 1
                elif (packet.course is not None and packet.course > 0):
                    # A moving stationary station?!
                    isMoving = 1
        return isMoving

    def _isSsidIndicateMoving(self, stationName):
        """Returns true if station SSID indicates moving

        Args:
            stationName (string):   Packet station name

        Returns:
            Returns true if station SSID indicates moving otherwise false
        """
        if (stationName.endswith('-7')):
            # walkie talkies, HT's or other human portable
            return True
        elif (stationName.endswith('-8')):
            # boats, sailboats, RV's or second main mobile
            return True
        elif (stationName.endswith('-9')):
            # Primary Mobile (usually message capable)
            return True
        elif (stationName.endswith('-11')):
            # balloons, aircraft, spacecraft, etc
            return True
        elif (stationName.endswith('-14')):
            # Truckers or generally full time drivers
            return True
        else:
            return False

    def _getNumberOfPacketWithSameSymbolAndOtherPos(self, packet, minTimestamp):
        """Returns the number of packets that has the same symbol but another position (for the same station)

        Args:
            stationId (int):     Id of the station
            packet (Packet):     Packet instance that we base the search on

        Returns:
            The number of packets that has the same symbol but another position
        """
        selectCursor = self.db.cursor()
        packetTableCreator = PacketTableCreator(self.db)
        packetTables = packetTableCreator.getPacketTables(minTimestamp)
        result = 0
        for packetTable in packetTables:
            sql = selectCursor.mogrify("""select count(*) number_of_packets from """ + packetTable + """ where station_id = %s and map_id = 1 and symbol = %s and symbol_table = %s and latitude != %s and longitude != %s""", (
                packet.stationId,
                packet.symbol,
                packet.symbolTable,
                packet.latitude,
                packet.longitude,))

            selectCursor = self.db.cursor()
            selectCursor.execute(sql)
            record = selectCursor.fetchone()

            if (record is not None):
                result = result + record["number_of_packets"]

        selectCursor.close()
        return result
