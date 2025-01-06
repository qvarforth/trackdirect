from server.trackdirect.parser.policies.AprsPacketSymbolPolicy import AprsPacketSymbolPolicy
from server.trackdirect.database.PacketTableCreator import PacketTableCreator


class PacketAssumedMoveTypePolicy:
    """PacketAssumedMoveTypeIdPolicy calculates a packet's default move type."""

    def __init__(self, db):
        """Initialize the PacketAssumedMoveTypePolicy.

        Args:
            db (psycopg2.Connection): Database connection
        """
        self.db = db
        self.aprs_packet_symbol_policy = AprsPacketSymbolPolicy()
        self.packet_table_creator = PacketTableCreator(db)

    def get_assumed_move_type(self, packet, prev_packet):
        """Determine the current packet move type based on its movement status.

        Args:
            packet (Packet): Packet to determine move type for
            prev_packet (Packet): Previous related packet for the same station

        Returns:
            int: The current packet move type id
        """
        is_moving = self._get_default_assumed_move_type(packet)

        if prev_packet.is_existing_object() and is_moving == 0 and not self._is_balloon_predicted_touchdown(packet):
            # If assumed stationary, validate by comparing to previous packet
            if self._should_assume_moving(packet, prev_packet):
                is_moving = 1
            elif self._has_different_position(packet, prev_packet):
                number_of_packets = self._get_number_of_packet_with_same_symbol_and_other_pos(packet, packet.timestamp - 86400)
                if number_of_packets > 0:
                    is_moving = 1

        return is_moving

    def _is_balloon_predicted_touchdown(self, packet):
        """Check if the packet is likely a balloon touchdown.

        Args:
            packet (Packet): Packet to check

        Returns:
            bool: True if packet is likely a balloon touchdown, otherwise False
        """
        return packet.symbol_table != "/" and packet.symbol == "o" and packet.comment and "touchdown" in packet.comment

    def _get_default_assumed_move_type(self, packet):
        """Determine the default move type id for the packet.

        Args:
            packet (Packet): Packet to determine move type for

        Returns:
            int: The default packet move type id
        """
        if not packet or not packet.symbol or not packet.symbol_table:
            return 1  # Default to moving

        is_moving = 1
        if self.aprs_packet_symbol_policy.is_stationary_symbol(packet.symbol, packet.symbol_table) or \
           self.aprs_packet_symbol_policy.is_maybe_moving_symbol(packet.symbol, packet.symbol_table):
            is_moving = 0

        if is_moving == 0 and self._is_ssid_indicate_moving(packet.stationName) and \
           self.aprs_packet_symbol_policy.is_maybe_moving_symbol(packet.symbol, packet.symbol_table):
            is_moving = 1

        if is_moving == 0 and (packet.course or packet.speed) and packet.packet_type_id != 3:
            if self.aprs_packet_symbol_policy.is_maybe_moving_symbol(packet.symbol, packet.symbol_table) or \
               self._is_ssid_indicate_moving(packet.stationName) or \
               (packet.speed and packet.speed > 0) or \
               (packet.course and packet.course > 0):
                is_moving = 1

        return is_moving

    def _is_ssid_indicate_moving(self, station_name):
        """Check if the station SSID indicates movement.

        Args:
            station_name (str): Station name to check

        Returns:
            bool: True if SSID indicates movement, otherwise False
        """
        moving_ssids = ['-7', '-8', '-9', '-11', '-14']
        return any(station_name.endswith(ssid) for ssid in moving_ssids)

    def _get_number_of_packet_with_same_symbol_and_other_pos(self, packet, min_timestamp):
        """Count packets with the same symbol but different positions.

        Args:
            packet (Packet): Packet to base the search on
            min_timestamp (int): Minimum timestamp for the search

        Returns:
            int: Number of packets with the same symbol but different positions
        """
        cursor = self.db.cursor()
        packet_tables = self.packet_table_creator.get_tables(min_timestamp)
        result = 0

        for packet_table in packet_tables:
            sql = cursor.mogrify(
                f"""SELECT COUNT(*) AS number_of_packets 
                    FROM {packet_table} 
                    WHERE station_id = %s AND map_id = 1 AND symbol = %s AND symbol_table = %s 
                    AND latitude != %s AND longitude != %s""",
                (packet.station_id, packet.symbol, packet.symbol_table, packet.latitude, packet.longitude)
            )
            cursor.execute(sql)
            record = cursor.fetchone()
            if record:
                result += record["number_of_packets"]

        cursor.close()
        return result

    def _should_assume_moving(self, packet, prev_packet):
        """Determine if the packet should be assumed as moving based on previous packet.

        Args:
            packet (Packet): Current packet
            prev_packet (Packet): Previous packet

        Returns:
            bool: True if the packet should be assumed as moving, otherwise False
        """
        return (
                packet.is_symbol_equal(prev_packet) and
                (prev_packet.timestamp - prev_packet.position_timestamp) < 36000 and
                prev_packet.is_moving == 1
        ) or (
                self.aprs_packet_symbol_policy.is_maybe_moving_symbol(packet.symbol, packet.symbol_table) and
                prev_packet.is_moving == 1
        ) or (
            packet.is_symbol_equal(prev_packet) and
            not packet.is_position_equal(prev_packet)
        )

    def _has_different_position(self, packet, prev_packet):
        """Check if the packet has a different position compared to the previous packet.

        Args:
            packet (Packet): Current packet
            prev_packet (Packet): Previous packet

        Returns:
            bool: True if the packet has a different position, otherwise False
        """
        return not packet.is_position_equal(prev_packet)