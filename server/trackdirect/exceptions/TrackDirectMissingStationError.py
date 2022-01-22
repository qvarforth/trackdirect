from trackdirect.exceptions.TrackDirectGenericError import TrackDirectGenericError


class TrackDirectMissingStationError(TrackDirectGenericError):
    """Raised when unexpected format of a supported packet format is encountered
    """

    def __init__(self, message, data={}):
        """The __init__ method.

        Args:
            message (str): Exception message
            data (dict):   Packet data that caused parse error
        """
        super(TrackDirectMissingStationError, self).__init__(message)
        self.packet = data
