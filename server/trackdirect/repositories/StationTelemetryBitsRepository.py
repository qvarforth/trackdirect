import datetime
import time
from trackdirect.common.Repository import Repository
from trackdirect.objects.StationTelemetryBits import StationTelemetryBits


class StationTelemetryBitsRepository(Repository):
    """A Repository class for the StationTelemetryBits class
    """

    def __init__(self, db):
        """The __init__ method.

        Args:
            db (psycopg2.Connection): Database connection
        """
        self.db = db

    def getObjectById(self, id):
        """The getObjectById method is supposed to return an object based on the specified id in database

        Args:
            id (int):  Database row id

        Returns:
            StationTelemetryBits
        """
        selectCursor = self.db.cursor()
        selectCursor.execute(
            """select * from station_telemetry_bits where id = %s""", (id,))
        record = selectCursor.fetchone()

        dbObject = self.create()
        if (record is not None):
            dbObject.id = record["id"]
            dbObject.stationId = record["station_id"]
            dbObject.createdTs = record["created_ts"]
            dbObject.latestTs = record["latest_ts"]
            dbObject.validToTs = record["valid_to_ts"]
            dbObject.bits = record["bits"]
            dbObject.title = record["title"]
        else:
            # do not exists, return empty object
            pass

        selectCursor.close()
        return dbObject

    def getObjectFromPacketData(self, data):
        """Create object from raw packet data

        Note:
            stationId will not be set

        Args:
            data (dict):  Raw packet data

        Returns:
            StationTelemetryBits
        """
        newObject = self.create()
        if ("tBITS" in data):
            # Remove one second since that will give us a more accurate timestamp
            newObject.createdTs = int(time.time()) - 1
            newObject.bits = data["tBITS"].replace('\x00', '')
            newObject.title = data["title"].replace('\x00', '')
        return newObject

    def create(self):
        """Creates an empty StationTelemetryBits object

        Returns:
            StationTelemetryBits
        """
        return StationTelemetryBits(self.db)
