from server.trackdirect.parser.policies.PacketOrderPolicy import PacketOrderPolicy
from server.trackdirect.parser.policies.PacketMaxSpeedPolicy import PacketMaxSpeedPolicy


class PacketMapIdPolicy:
    """PacketMapIdPolicy tries to find the best mapId for the current packet."""

    def __init__(self, packet, prev_packet):
        """The __init__ method.

        Args:
            packet (Packet):  Packet that we want to analyze
            prev_packet (Packet): Previous related packet for the same station
        """
        self.packet = packet
        self.prev_packet = prev_packet
        self.has_kill_character = False
        self.marker_counter_confirm_limit = 3

        # Results
        self.mapId = None
        self.marker_id = None
        self.is_replacing_prev_packet = False
        self.is_confirming_prev_packet = False
        self.is_killing_prev_packet = False

    def enable_having_kill_character(self):
        """Treat this packet as having a kill character."""
        self.has_kill_character = True

    def get_map_id(self):
        """Returns the map id that corresponds to the found marker id.

        Returns:
            int
        """
        self._find_map_id()
        return self.mapId

    def get_marker_id(self):
        """Returns the found marker id.

        Returns:
            int
        """
        self._find_map_id()
        return self.marker_id

    def is_replacing_previous_packet(self):
        """Returns true if packet replaces previous packet.

        Returns:
            boolean
        """
        self._find_map_id()
        return self.is_replacing_prev_packet

    def is_confirming_previous_packet(self):
        """Returns true if packet confirms previous packet.

        Returns:
            boolean
        """
        self._find_map_id()
        return self.is_confirming_prev_packet

    def is_killing_previous_packet(self):
        """Returns true if packet kills previous packet.

        Returns:
            boolean
        """
        self._find_map_id()
        return self.is_killing_prev_packet

    def _find_map_id(self):
        """Find a suitable marker id for the current packet and set corresponding attribute (and related attributes)."""
        if self.mapId is not None:
            return

        packetOrderPolicy = PacketOrderPolicy()

        if self.packet.source_id == 2 and self.packet.station_id_path:
            self.mapId = 16
            self.marker_id = 1
        elif not self._is_packet_on_map():
            self.mapId = 10
            self.marker_id = 1
        elif packetOrderPolicy.is_packet_in_wrong_order(self.packet, self.prev_packet):
            self.mapId = 6
            self.marker_id = 1
        elif self._is_faulty_gps_position():
            self._find_map_id_for_faulty_gps_position()
        elif self.packet.is_moving == 1:
            self._find_map_id_for_moving_station()
        else:
            self._find_map_id_for_stationary_station()

    def _is_packet_on_map(self):
        """Returns true if current packet will be on map.

        Returns:
            boolean
        """
        return (
                self.packet.latitude is not None
                and self.packet.longitude is not None
                and isinstance(self.packet.latitude, float)
                and isinstance(self.packet.longitude, float)
                and self.packet.source_id != 3
                and self.packet.map_id in [1, 5, 7, 9]
        )

    def _find_map_id_for_stationary_station(self):
        """Find a suitable marker id for the current packet (assumes it is a stationary station) and set corresponding attribute (and related attributes)."""
        if (
            self.prev_packet.is_existing_object()
            and self.packet.is_position_equal(self.prev_packet)
            and self.packet.is_symbol_equal(self.prev_packet)
            and self.packet.is_moving == self.prev_packet.is_moving
            and self.prev_packet.map_id in [1, 7]
        ):
            self.mapId = 1
            self.marker_id = self.prev_packet.marker_id
            if (self.has_kill_character):
                self.mapId = 14
            self.is_replacing_prev_packet = True
        elif self.has_kill_character:
            self.marker_id = 1
            self.mapId = 4
        else:
            self.mapId = 1
            self.marker_id = None

    def _find_map_id_for_moving_station(self):
        """Find a suitable marker id for the current packet (assumes it is a moving station) and set corresponding attribute (and related attributes)."""
        if self.has_kill_character:
            self.mapId = 4
            self.marker_id = 1
        elif (
                self.prev_packet.is_existing_object()
                and self.prev_packet.is_moving == 1
                and self.prev_packet.map_id in [1, 7]
        ):
            calculated_distance = self.packet.get_distance(self.prev_packet.latitude, self.prev_packet.longitude)
            calculated_speed = self.packet.get_calculated_speed(self.prev_packet)
            packet_max_speed_policy = PacketMaxSpeedPolicy()
            max_speed = packet_max_speed_policy.get_max_likely_speed(self.packet, self.prev_packet)
            absolute_max_distance = 50000
            absolute_max_speed = 2000

            if self.packet.is_position_equal(self.prev_packet):
                self._find_map_id_for_moving_station_with_same_position()
            elif calculated_distance < 5000 and calculated_speed <= absolute_max_speed:
                self._find_map_id_for_moving_station_with_likely_speed()
            elif calculated_speed <= max_speed and calculated_speed <= absolute_max_speed and calculated_distance <= absolute_max_distance:
                self._find_map_id_for_moving_station_with_likely_speed()
            elif calculated_speed <= max_speed and calculated_distance > absolute_max_distance:
                self._find_map_id_for_moving_station_with_to_long_distance()
            else:
                self.mapId = 7
                self.marker_id = None
        else:
            if (
                self.prev_packet.is_existing_object()
                and self.prev_packet.is_moving == 0
                and self.packet.is_symbol_equal(self.prev_packet)
            ):
                self.is_killing_prev_packet = True
            self.mapId = 1
            self.marker_id = None

    def _find_map_id_for_moving_station_with_to_long_distance(self):
        """Sets a suitable marker id for the current packet based on prevPacket and assumes that distance is too long between them."""
        if self.prev_packet.marker_counter == 1:
            self.is_killing_prev_packet = True
        self.mapId = 1
        self.marker_id = None

    def _find_map_id_for_moving_station_with_likely_speed(self):
        """Sets a suitable marker id for the current packet based on prevPacket and assumes that speed is likely."""
        self.marker_id = self.prev_packet.marker_id
        if self.prev_packet.map_id == 1 or (self.prev_packet.marker_counter + 1) >= self.marker_counter_confirm_limit:
            self.mapId = 1
        else:
            self.mapId = self.prev_packet.map_id

        if self.mapId == 1 and self.prev_packet.map_id == 7:
            self.is_confirming_prev_packet = True

    def _find_map_id_for_moving_station_with_same_position(self):
        """Sets a suitable marker id for the current packet based on prevPacket and assumes that position is equal."""
        self.marker_id = self.prev_packet.marker_id
        self.is_replacing_prev_packet = True
        if self.prev_packet.map_id == 1 or (self.prev_packet.marker_counter + 1) >= self.marker_counter_confirm_limit:
            self.mapId = 1
        else:
            self.mapId = self.prev_packet.map_id

    def _find_map_id_for_faulty_gps_position(self):
        """Sets a suitable marker id for the current packet based on prevPacket and assumes that gps position is faulty (mapId 5)."""
        if self.has_kill_character:
            self.mapId = 4
            self.marker_id = 1
        elif (
                self.prev_packet.map_id == self.mapId
                and self.packet.is_position_equal(self.prev_packet)
                and self.packet.is_symbol_equal(self.prev_packet)
        ):
            self.is_replacing_prev_packet = True
            self.mapId = 5
            self.marker_id = self.prev_packet.marker_id
        else:
            self.mapId = 5
            self.marker_id = None

    def _is_faulty_gps_position(self):
        """Parse the packet and modify the mapId attribute if position is faulty."""
        packetlat_cmp = int(round(self.packet.latitude * 100000))
        packetlng_cmp = int(round(self.packet.longitude * 100000))

        faulty_positions = [
            (0, 0),
            (1 * 100000, 1 * 100000),
            (36 * 100000, 136 * 100000),
            (-48 * 100000, 0)
        ]

        return (packetlat_cmp, packetlng_cmp) in faulty_positions