import datetime
import time

from trackdirect.common.Repository import Repository
from trackdirect.objects.PacketWeather import PacketWeather
from trackdirect.database.PacketWeatherTableCreator import PacketWeatherTableCreator
from trackdirect.exceptions.TrackDirectMissingTableError import TrackDirectMissingTableError


class PacketWeatherRepository(Repository):
    """A Repository class for the PacketWeather class
    """

    def __init__(self, db):
        """The __init__ method.

        Args:
            db (psycopg2.Connection):   Database connection
        """
        self.db = db
        self.packetWeatherTableCreator = PacketWeatherTableCreator(self.db)
        self.packetWeatherTableCreator.disableCreateIfMissing()

    def getObjectById(self, id):
        """The getObjectById method is supposed to return an object based on the specified id in database

        Args:
            id (int):  Database row id

        Returns:
            PacketWeather
        """
        selectCursor = self.db.cursor()
        selectCursor.execute("""select * from packet_weather where id = %s""", (id,))
        record = selectCursor.fetchone()
        selectCursor.close()
        return self.getObjectFromRecord(record)

    def getObjectByPacketIdAndTimestamp(self, id, timestamp):
        """Returns an object based on the specified packet id in database

        Args:
            id (int):         Database row id
            timestamp (int):  Unix timestamp for requested packet (must be samt date as packet was received)

        Returns:
            PacketWeather
        """
        try:
            table = self.packetWeatherTableCreator.getPacketWeatherTable(
                timestamp)
            selectCursor = self.db.cursor()
            selectCursor.execute("""select * from """ +
                                 table + """ where packet_id = %s""", (id,))
            record = selectCursor.fetchone()
            selectCursor.close()
            return self.getObjectFromRecord(record)
        except TrackDirectMissingTableError as e:
            return self.create()

    def getObjectFromRecord(self, record):
        """Returns a packet weather object from a record

        Args:
            record (dict):  Database record dict to convert to a packet weather object

        Returns:
            A packet weather object
        """
        dbObject = PacketWeather(self.db)
        if (record is not None):
            dbObject.id = record["id"]
            dbObject.packetId = int(record["packet_id"])
            dbObject.stationId = int(record["station_id"])
            dbObject.timestamp = int(record["timestamp"])
            dbObject.humidity = record["humidity"]
            dbObject.pressure = record["pressure"]
            dbObject.rain1h = record["rain_1h"]
            dbObject.rain24h = record["rain_24h"]
            dbObject.rainSinceMidnight = record["rain_since_midnight"]
            dbObject.temperature = record["temperature"]
            dbObject.windDirection = record["wind_direction"]
            dbObject.windGust = record["wind_gust"]
            dbObject.windSpeed = record["wind_speed"]
            dbObject.luminosity = record["luminosity"]
            dbObject.snow = record["snow"]
            dbObject.wxRawTimestamp = record["wx_raw_timestamp"]
        return dbObject

    def getObjectFromPacketData(self, data):
        """Create object from raw packet data

        Note:
            stationId will not be set

        Args:
            data (dict):  Raw packet data

        Returns:
            PacketWeather
        """
        newObject = self.create()
        if ("weather" in data):
            # Remove one second since that will give us a more accurate timestamp
            newObject.timestamp = int(time.time()) - 1

            if ("humidity" in data["weather"]):
                newObject.humidity = data["weather"]["humidity"]
            if ("pressure" in data["weather"]):
                newObject.pressure = data["weather"]["pressure"]
            if ("rain_1h" in data["weather"]):
                newObject.rain1h = data["weather"]["rain_1h"]
            if ("rain_24h" in data["weather"]):
                newObject.rain24h = data["weather"]["rain_24h"]
            if ("rain_since_midnight" in data["weather"]):
                newObject.rainSinceMidnight = data["weather"]["rain_since_midnight"]
            if ("temperature" in data["weather"]):
                newObject.temperature = data["weather"]["temperature"]
            if ("wind_direction" in data["weather"]):
                newObject.windDirection = data["weather"]["wind_direction"]
            if ("wind_gust" in data["weather"]):
                newObject.windGust = data["weather"]["wind_gust"]
            if ("wind_speed" in data["weather"]):
                newObject.windSpeed = data["weather"]["wind_speed"]
            if ("luminosity" in data["weather"]):
                newObject.luminosity = data["weather"]["luminosity"]
            if ("snow" in data["weather"]):
                newObject.snow = data["weather"]["snow"]
            if ("wx_raw_timestamp" in data["weather"]):
                newObject.wxRawTimestamp = data["weather"]["wx_raw_timestamp"]
        return newObject

    def create(self):
        """Creates an empty PacketWeather object

        Returns:
            PacketWeather
        """
        return PacketWeather(self.db)
