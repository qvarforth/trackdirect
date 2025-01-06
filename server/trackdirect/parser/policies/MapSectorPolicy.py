from math import floor, ceil


class MapSectorPolicy:
    """The MapSectorPolicy class handles logic related to map sectors."""

    def __init__(self):
        """Initialize the MapSectorPolicy class."""
        pass

    def get_map_sector(self, latitude, longitude):
        """
        Returns a map sector integer specified by latitude and longitude.

        Args:
            latitude (float): Numeric latitude.
            longitude (float): Numeric longitude.

        Returns:
            int: A map sector integer.
        """
        if isinstance(latitude, float) and isinstance(longitude, float):
            lat = self.get_map_sector_lat_representation(latitude)
            lng = self.get_map_sector_lng_representation(longitude)

            # lat interval: 0 - 18000000
            # lng interval: 0 - 00003600
            return lat + lng
        else:
            return None

    def get_map_sector_lat_representation(self, latitude):
        """
        Returns the latitude part of a map sector integer.

        Args:
            latitude (float): Numeric latitude.

        Returns:
            int: The latitude part of a map sector integer.
        """
        lat = int(floor(latitude)) + 90  # Positive representation of lat
        lat_decimal_part = latitude - floor(latitude)

        if lat_decimal_part < 0.2:
            lat = lat * 10
        elif lat_decimal_part < 0.4:
            lat = lat * 10 + 2
        elif lat_decimal_part < 0.6:
            lat = lat * 10 + 4
        elif lat_decimal_part < 0.8:
            lat = lat * 10 + 6
        else:
            lat = lat * 10 + 8

        lat = lat * 10000

        # lat interval: 0 - 18000000
        return lat

    def get_map_sector_lng_representation(self, longitude):
        """
        Returns the longitude part of a map sector integer.

        Args:
            longitude (float): Numeric longitude.

        Returns:
            int: The longitude part of a map sector integer.
        """
        lng = int(floor(longitude)) + 180  # Positive representation of lng
        lng_decimal_part = longitude - floor(longitude)

        if lng_decimal_part < 0.5:
            lng = lng * 10
        else:
            lng = lng * 10 + 5

        # lng interval: 0 - 00003600
        return lng