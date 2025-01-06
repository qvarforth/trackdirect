from server.trackdirect.common.Model import Model


class PacketOgn(Model):
    """PacketOgn represents the OGN data in an APRS packet."""

    def __init__(self, db):
        """Initialize PacketOgn with database connection and attributes.

        Args:
            db (psycopg2.Connection): Database connection
        """
        super().__init__(db)
        self.id = None
        self.packet_id = None
        self.station_id = None
        self.timestamp = None
        self.ogn_sender_address = None
        self.ogn_address_type_id = None
        self.ogn_aircraft_type_id = None
        self.ogn_climb_rate = None
        self.ogn_turn_rate = None
        self.ogn_signal_to_noise_ratio = None
        self.ogn_bit_errors_corrected = None
        self.ogn_frequency_offset = None

    def validate(self) -> bool:
        """Validate the object content.

        Returns:
            bool: True if object content is valid, otherwise False
        """
        if self.station_id is None or self.station_id <= 0:
            return False

        if self.packet_id is None or self.packet_id <= 0:
            return False

        return True

    def insert(self) -> bool:
        """Insert the object into the database.

        Since packets are inserted in batch, this method is not used.

        Returns:
            bool: Always returns False
        """
        return False

    def update(self) -> bool:
        """Update the object in the database.

        Since packets are updated in batch, this method is not used.

        Returns:
            bool: Always returns False
        """
        return False

    def get_dict(self) -> dict:
        """Convert the object to a dictionary.

        Returns:
            dict: A dictionary representation of the object
        """
        return {
            'id': self.id,
            'packet_id': self.packet_id,
            'station_id': self.station_id,
            'timestamp': self.timestamp,
            'ogn_sender_address': self.ogn_sender_address,
            'ogn_address_type_id': self.ogn_address_type_id,
            'ogn_aircraft_type_id': self.ogn_aircraft_type_id,
            'ogn_climb_rate': self.ogn_climb_rate,
            'ogn_turn_rate': self.ogn_turn_rate,
            'ogn_signal_to_noise_ratio': self.ogn_signal_to_noise_ratio,
            'ogn_bit_errors_corrected': self.ogn_bit_errors_corrected,
            'ogn_frequency_offset': self.ogn_frequency_offset
        }