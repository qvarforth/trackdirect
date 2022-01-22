from trackdirect.common.Model import Model


class PacketOgn(Model):
    """PacketOgn represents the OGN data in a APRS packet
    """

    def __init__(self, db):
        """The __init__ method.

        Args:
            db (psycopg2.Connection): Database connection
        """
        Model.__init__(self, db)
        self.id = None
        self.packetId = None
        self.stationId = None
        self.timestamp = None
        self.ognSenderAddress = None
        self.ognAddressTypeId = None
        self.ognAircraftTypeId = None
        self.ognClimbRate = None
        self.ognTurnRate = None
        self.ognSignalToNoiseRatio = None
        self.ognBitErrorsCorrected = None
        self.ognFrequencyOffset = None

    def validate(self):
        """Returns true on success (when object content is valid), otherwise false

        Returns:
            True on success otherwise False
        """
        if (self.stationId <= 0):
            return False

        if (self.packetId <= 0):
            return False

        return True

    def insert(self):
        """Method to call when we want to save a new object to database

        Since packet will be inserted in batch we never use this method.

        Returns:
            True on success otherwise False
        """
        return False

    def update(self):
        """Method to call when we want to save changes to database

        Since packet will be updated in batch we never use this method.

        Returns:
            True on success otherwise False
        """
        return False

    def getDict(self):
        """Returns the packet OGN as a dict

        Args:
            None

        Returns:
            A packet OGN dict
        """
        data = {}
        data['id'] = self.id
        data['packet_id'] = self.packetId
        data['station_id'] = self.stationId
        data['timestamp'] = self.timestamp
        data['ogn_sender_address'] = self.ognSenderAddress
        data['ogn_address_type_id'] = self.ognAddressTypeId
        data['ogn_aircraft_type_id'] = self.ognAircraftTypeId
        data['ogn_climb_rate'] = self.ognClimbRate
        data['ogn_turn_rate'] = self.ognTurnRate
        data['ogn_signal_to_noise_ratio'] = self.ognSignalToNoiseRatio
        data['ogn_bit_errors_corrected'] = self.ognBitErrorsCorrected
        data['ogn_frequency_offset'] = self.ognFrequencyOffset
        return data
