class StationNameFormatPolicy:
    """The StationNameFormatPolicy class handles logic related to station name format
    """

    STATUS_CHARACTERS = ['*', '!', '_', '\'', '"', '`']

    @staticmethod
    def get_correct_format(name):
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
        for char in StationNameFormatPolicy.STATUS_CHARACTERS:
            name = name.replace(char, '')
        return name.strip()