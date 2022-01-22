from math import floor, ceil


class MapSectorPolicy():
    """The MapSectorPolicy class hanles logic related to map sectors
    """

    def __init__(self):
        """The __init__ method.
        """

    def getMapSector(self, latitude, longitude):
        """Returns a map sector integer specified by latitude and longitude

        Args:
            latitude (float):  Numeric latitude
            longitude (float): Numeric longitude

        Returns:
            A map sector integer
        """
        if (type(latitude) is float and type(longitude) is float):
            lat = self.getMapSectorLatRepresentation(latitude)
            lng = self.getMapSectorLngRepresentation(longitude)

            # lat interval: 0 - 18000000
            # lng interval: 0 - 00003600
            return lat+lng
        else:
            return None

    def getMapSectorLatRepresentation(self, latitude):
        """Returns the latitude part of a map sector integer

        Args:
            latitude (float):  Numeric latitude

        Returns:
            The latitude part of a map sector integer
        """
        lat = int(floor(latitude)) + 90  # Positive representation of lat
        latDecimalPart = latitude - floor(latitude)

        if (latDecimalPart < 0.2):
            lat = lat * 10 + 0
        elif (latDecimalPart < 0.4):
            lat = lat * 10 + 2
        elif (latDecimalPart < 0.6):
            lat = lat * 10 + 4
        elif (latDecimalPart < 0.8):
            lat = lat * 10 + 6
        else:
            lat = lat * 10 + 8

        lat = lat * 10000

        # lat interval: 0 - 18000000
        return lat

    def getMapSectorLngRepresentation(self, longitude):
        """Returns the longitude part of a map sector integer

        Args:
            longitude (float):  Numeric latitude

        Returns:
            The longitude part of a map sector integer
        """
        lng = int(floor(longitude)) + 180  # Positive representation of lng
        lngDecimalPart = longitude - floor(longitude)

        if (lngDecimalPart < 0.5):
            lng = lng * 10 + 0
        else:
            lng = lng * 10 + 5

        # lng interval: 0 - 00003600
        return lng
