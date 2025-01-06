from server.trackdirect.parser.policies.PacketSpeedComputablePolicy import PacketSpeedComputablePolicy


class PacketMaxSpeedPolicy:
    """PacketMaxSpeedPolicy handles logic related to max possible speed (used to filter out faulty packets)
    """

    def __init__(self):
        """The __init__ method.
        """

    def get_max_likely_speed(self, packet, prev_packet):
        """Returns the max likely speed

        Args:
            packet (Packet):  Packet that we want to analyze
            prev_packet (Packet):   Previous related packet for the same station

        Returns:
            Max likely speed as float
        """
        max_speed = self._get_default_station_max_speed(packet)

        if packet.speed is not None and packet.speed > max_speed:
            # We allow 100% faster speed than the reported speed
            max_speed = packet.speed * 2

        if prev_packet.is_existing_object() and prev_packet.speed is not None and prev_packet.speed > max_speed:
            # We allow 100% faster speed than the previous reported speed
            max_speed = prev_packet.speed * 2

        calculated_speed = 0
        if prev_packet.is_existing_object():
            calculated_speed = packet.get_calculated_speed(prev_packet)

        packet_speed_computable_policy = PacketSpeedComputablePolicy()
        if (packet_speed_computable_policy.is_speed_computable(packet, prev_packet)
                and prev_packet.map_id == 7
                and calculated_speed > max_speed):
            # If last position is unconfirmed but still is closer to the last confirmed and calculated speed is trusted we accept that speed
            # This part is IMPORTANT to avoid that all packets get map_id == 7
            max_speed = calculated_speed

        max_speed *= (1 + len(packet.station_id_path))
        return max_speed

    def _get_default_station_max_speed(self, packet):
        """Returns the station default max speed (not affected by or adaptive speed limit)

        Args:
            packet (Packet):  Packet that we want analyze

        Returns:
            Returns the station default max speed as int
        """
        # Bugatti Veyron Super Sport Record Edition 2010, the fastest production car can do 431 kmh (but a regular car usually drives a bit slower...)
        max_speed = 200
        if packet.altitude is not None:
            highest_land_altitude = 5767  # Uturuncu, Bolivia, highest road altitude
            air_plane_max_altitude = 15240  # Very rare that airplanes go higher than 50,000 feet
            satellite_min_altitude = 160000  # Objects below approximately 160 kilometers (99 mi) will experience very rapid orbital decay and altitude loss.

            if packet.altitude > satellite_min_altitude:
                # Seems like this is a satellite
                # Until we know more we don't change anything
                pass
            elif packet.altitude > air_plane_max_altitude:
                # Higher than a normal airplane but not a satellite, could be a high altitude balloon
                max_speed = 50
            elif packet.altitude > highest_land_altitude:
                # Seems like this is an airplane or a balloon
                # 394 kmh is the ground speed record for a hot air balloon
                # 950 kmh is a common upper cruise speed for regular airplanes
                max_speed = 950
        return max_speed