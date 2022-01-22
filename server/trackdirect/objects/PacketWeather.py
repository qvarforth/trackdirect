from trackdirect.common.Model import Model


class PacketWeather(Model):
    """PacketWeather represents the weather data in a APRS packet
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
        self.humidity = None
        self.pressure = None
        self.rain1h = None
        self.rain24h = None
        self.rainSinceMidnight = None
        self.temperature = None
        self.windDirection = None
        self.windGust = None
        self.windSpeed = None
        self.luminosity = None
        self.snow = None
        self.wxRawTimestamp = None

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
        """Returns the packet weather as a dict

        Args:
            None

        Returns:
            A packet weather dict
        """
        data = {}
        data['id'] = self.id
        data['packet_id'] = self.packetId
        data['station_id'] = self.stationId
        data['timestamp'] = self.timestamp
        data['humidity'] = self.humidity
        data['pressure'] = self.pressure
        data['rain_1h'] = self.rain1h
        data['rain_24h'] = self.rain24h
        data['rain_since_midnight'] = self.rainSinceMidnight
        data['temperature'] = self.temperature
        data['wind_direction'] = self.windDirection
        data['wind_gust'] = self.windGust
        data['wind_speed'] = self.windSpeed
        data['luminosity'] = self.luminosity
        data['snow'] = self.snow
        data['wx_raw_timestamp'] = self.wxRawTimestamp
        return data
