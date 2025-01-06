from server.trackdirect.database.PacketTableCreator import PacketTableCreator
from server.trackdirect.exceptions.TrackDirectMissingTableError import TrackDirectMissingTableError


class PacketMapIdModifier:
    """PacketMapIdModifier is used to modify mapId on existing packets in database based on new packets."""

    def __init__(self, cur, packet_table_creator: PacketTableCreator):
        """The __init__ method.

        Args:
            cur (psycopg2.Cursor): Database cursor
            packet_table_creator (PacketTableCreator): PacketTableCreator instance
        """
        self.cur = cur
        self.packet_table_creator = packet_table_creator

    def execute(self, packets: list):
        """Perform mapId modifications based on information in specified packets.

        Args:
            packets (list): Packets that may affect existing packets mapId
        """
        self._mark_previous_packets(packets, 'replacePacketId', 'replacePacketTimestamp', {5: 13}, 2, 12)
        self._mark_previous_packets(packets, 'abnormalPacketId', 'abnormalPacketTimestamp', {}, 9)
        self._mark_previous_packets(packets, 'confirmPacketId', 'confirmPacketTimestamp', {}, 1)

    def _mark_previous_packets(self, packets: list, packet_id_attr: str, timestamp_attr: str, special_cases: dict, default_map_id: int, secondary_map_id: int = None):
        """Mark previous packets based on the given attributes and map IDs.

        Args:
            packets (list): Packets that may affect existing packets mapId
            packet_id_attr (str): Attribute name for packet ID
            timestamp_attr (str): Attribute name for timestamp
            special_cases (dict): Special cases for mapId based on packet mapId
            default_map_id (int): Default mapId to set
            secondary_map_id (int, optional): Secondary mapId to set if conditions are met
        """
        packets_to_update = {default_map_id: {}, secondary_map_id: {}, **{v: {} for v in special_cases.values()}}

        for packet in packets:
            packet_id = getattr(packet, packet_id_attr, None)
            if packet_id is not None:
                try:
                    self.packet_table_creator.enable_create_if_missing()
                    new_packet_table = self.packet_table_creator.get_table(packet.timestamp)
                    self.packet_table_creator.disable_create_if_missing()
                    old_packet_table = self.packet_table_creator.get_table(getattr(packet, timestamp_attr))

                    map_id = special_cases.get(packet.map_id, default_map_id)
                    if secondary_map_id and new_packet_table != old_packet_table:
                        map_id = secondary_map_id

                    if old_packet_table not in packets_to_update[map_id]:
                        packets_to_update[map_id][old_packet_table] = []

                    packets_to_update[map_id][old_packet_table].append(packet_id)
                except TrackDirectMissingTableError:
                    pass

        for map_id, tables in packets_to_update.items():
            if map_id is not None:
                for packet_table, packet_ids in tables.items():
                    self._update_packet_map_id(packet_table, packet_ids, map_id)

    def _update_packet_map_id(self, packet_table: str, packet_id_list: list, map_id: int):
        """Update map id on all specified packets.

        Args:
            packet_table (str): Packet database table to perform update on
            packet_id_list (list): Array of all packet id's to update
            map_id (int): The requested new map id
        """
        if packet_id_list:
            sql = self.cur.mogrify(
                f"UPDATE {packet_table} SET map_id = %s WHERE id IN %s",
                (map_id, tuple(packet_id_list))
            )
            self.cur.execute(sql)