import time
from server.trackdirect.common.Repository import Repository
from server.trackdirect.objects.PacketWeather import PacketWeather
from server.trackdirect.database.PacketWeatherTableCreator import PacketWeatherTableCreator
from server.trackdirect.exceptions.TrackDirectMissingTableError import TrackDirectMissingTableError


class PacketWeatherRepository(Repository):
    """A Repository class for the PacketWeather class."""

    def __init__(self, db):
        """Initialize the PacketWeatherRepository with a database connection.

        Args:
            db (psycopg2.Connection): Database connection
        """
        super().__init__(db)
        self.packet_weather_table_creator = PacketWeatherTableCreator(self.db)
        self.packet_weather_table_creator.disable_create_if_missing()

    def get_object_by_id(self, object_id):
        """Retrieve a PacketWeather object by its ID from the database.

        Args:
            object_id (int): Database row ID

        Returns:
            PacketWeather
        """
        with self.db.cursor() as cursor:
            cursor.execute("SELECT * FROM packet_weather WHERE id = %s", (object_id,))
            record = cursor.fetchone()
        return self._get_object_from_record(record)

    def get_object_by_packet_id_and_timestamp(self, packet_id, timestamp):
        """Retrieve a PacketWeather object by packet ID and timestamp.

        Args:
            packet_id (int): Packet ID
            timestamp (int): Unix timestamp for the requested packet

        Returns:
            PacketWeather
        """
        try:
            table = self.packet_weather_table_creator.get_packet_weather_table(timestamp)
            with self.db.cursor() as cursor:
                cursor.execute(f"SELECT * FROM {table} WHERE packet_id = %s", (packet_id,))
                record = cursor.fetchone()
            return self._get_object_from_record(record)
        except TrackDirectMissingTableError:
            return self.create()

    def _get_object_from_record(self, record):
        """Convert a database record to a PacketWeather object.

        Args:
            record (dict): Database record

        Returns:
            PacketWeather
        """
        packet_weather = PacketWeather(self.db)
        if record:
            packet_weather.id = record["id"]
            packet_weather.packet_id = int(record["packet_id"])
            packet_weather.station_id = int(record["station_id"])
            packet_weather.timestamp = int(record["timestamp"])
            packet_weather.humidity = record["humidity"]
            packet_weather.pressure = record["pressure"]
            packet_weather.rain1h = record["rain_1h"]
            packet_weather.rain24h = record["rain_24h"]
            packet_weather.rain_since_midnight = record["rain_since_midnight"]
            packet_weather.temperature = record["temperature"]
            packet_weather.wind_direction = record["wind_direction"]
            packet_weather.wind_gust = record["wind_gust"]
            packet_weather.wind_speed = record["wind_speed"]
            packet_weather.luminosity = record["luminosity"]
            packet_weather.snow = record["snow"]
            packet_weather.wx_raw_timestamp = record["wx_raw_timestamp"]
        return packet_weather

    def get_object_from_packet_data(self, data):
        """Create a PacketWeather object from raw packet data.

        Note:
            stationId will not be set.

        Args:
            data (dict): Raw packet data

        Returns:
            PacketWeather
        """
        packet_weather = self.create()
        if "weather" in data:
            packet_weather.timestamp = int(time.time()) - 1  # Adjust timestamp for accuracy

            weather_data = data["weather"]
            packet_weather.humidity = weather_data.get("humidity")
            packet_weather.pressure = weather_data.get("pressure")
            packet_weather.rain1h = weather_data.get("rain_1h")
            packet_weather.rain24h = weather_data.get("rain_24h")
            packet_weather.rain_since_midnight = weather_data.get("rain_since_midnight")
            packet_weather.temperature = weather_data.get("temperature")
            packet_weather.wind_direction = weather_data.get("wind_direction")
            packet_weather.wind_gust = weather_data.get("wind_gust")
            packet_weather.wind_speed = weather_data.get("wind_speed")
            packet_weather.luminosity = weather_data.get("luminosity")
            packet_weather.snow = weather_data.get("snow")
            packet_weather.wx_raw_timestamp = weather_data.get("wx_raw_timestamp")
        return packet_weather

    def create(self):
        """Create an empty PacketWeather object.

        Returns:
            PacketWeather
        """
        return PacketWeather(self.db)
