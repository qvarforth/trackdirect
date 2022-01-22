class StationNameFormatPolicy():
    """The StationNameFormatPolicy class handles logic related to station name format
    """

    def __init__(self):
        """The __init__ method.
        """

    def getCorrectFormat(self, name):
        """ Returns the specified name in correct format
        (without any status characters)

        Notes:
            _ == kill character
            ! == live character for item
            * == live character for object
            single quote and double quote is just to annoying
            (of course we can handle it in database but why use it in a name...)

        Args:
            name (string):  name of station

        Returns:
            string
        """
        return name.replace('*', '').replace('!', '').replace('_', '').replace('\'', '').replace('"', '').replace('`', '').strip()
