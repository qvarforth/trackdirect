class PacketSpeedComputablePolicy:
    """PacketSpeedComputablePolicy handles logic related to parameters that may cause errors in speed calculations
    """

    def __init__(self):
        """The __init__ method.
        """

    def is_speed_computable(self, packet, prev_packet):
        """Returns true if speed is possible to calculate in a way that we can trust it

        Args:
            packet (Packet):        Packet that we want to know move typ for
            prev_packet (Packet):    Previous related packet for the same station

        Returns:
            Returns true if speed is possible to calculate
        """
        if (packet is None or prev_packet is None or
                prev_packet.is_moving != 1 or prev_packet.map_id not in [1, 7] or
                packet.marker_id == 1 or packet.is_moving != 1):
            return False

        if (packet.reported_timestamp is not None and prev_packet.reported_timestamp is not None and
                packet.reported_timestamp != 0 and prev_packet.reported_timestamp != 0 and
                (packet.reported_timestamp % 60 != 0 or prev_packet.reported_timestamp % 60 != 0) and
                prev_packet.reported_timestamp != packet.reported_timestamp):
            return True

        calculated_distance = packet.get_distance(prev_packet.latitude, prev_packet.longitude)
        if len(packet.station_id_path) < 1:
            # Packet was sent through internet, delay should be small
            return True
        elif len(packet.station_id_path) <= 1 and calculated_distance > 5000:
            # Packet has not been digipeated (delay should not be extreme)
            # and distance is longer than 5km
            return True
        else:
            # Packet was digipeated (delay can be very long)
            # or distance was short, calculated speed can not be trusted
            return False