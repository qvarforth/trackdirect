from server.trackdirect.common.Model import Model


class PacketWeather(Model):
    """PacketWeather represents the weather data in an APRS packet
    """

    def __init__(self, db):
        """The __init__ method.

        Args:
            db (psycopg2.Connection): Database connection
        """
        super().__init__(db)
        self.packet_id = None
        self.station_id = None
        self.timestamp = None
        self.humidity = None
        self.pressure = None
        self.rain1h = None
        self.rain24h = None
        self.rain_since_midnight = None
        self.temperature = None
        self.wind_direction = None
        self.wind_gust = None
        self.wind_speed = None
        self.luminosity = None
        self.snow = None
        self.wx_raw_timestamp = None

    def validate(self) -> bool:
        """Returns true on success (when object content is valid), otherwise false

        Returns:
            True on success otherwise False
        """
        if self.station_id is None or self.station_id <= 0:
            return False

        if self.packet_id is None or self.packet_id <= 0:
            return False

        return True

    def insert(self) -> bool:
        """Method to call when we want to save a new object to database

        Since packet will be inserted in batch we never use this method.

        Returns:
            True on success otherwise False
        """
        return False

    def update(self) -> bool:
        """Method to call when we want to save changes to database

        Since packet will be updated in batch we never use this method.

        Returns:
            True on success otherwise False
        """
        return False

    def get_dict(self) -> dict:
        """Returns the packet weather as a dict

        Returns:
            A packet weather dict
        """
        return {
            'id': self.id,
            'packet_id': self.packet_id,
            'station_id': self.station_id,
            'timestamp': self.timestamp,
            'humidity': self.humidity,
            'pressure': self.pressure,
            'rain_1h': self.rain1h,
            'rain_24h': self.rain24h,
            'rain_since_midnight': self.rain_since_midnight,
            'temperature': self.temperature,
            'wind_direction': self.wind_direction,
            'wind_gust': self.wind_gust,
            'wind_speed': self.wind_speed,
            'luminosity': self.luminosity,
            'snow': self.snow,
            'wx_raw_timestamp': self.wx_raw_timestamp
        }