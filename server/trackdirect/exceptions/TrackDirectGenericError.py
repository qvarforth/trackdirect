class TrackDirectGenericError(Exception):
    """ Base exception class for the library. Logs information via logging module
    """

    def __init__(self, message):
        """The __init__ method.

        Args:
            message (str): Exception message
        """
        super(TrackDirectGenericError, self).__init__(message)
        self.message = message
