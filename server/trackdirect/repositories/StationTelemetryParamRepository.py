import datetime
import time
from trackdirect.common.Repository import Repository
from trackdirect.objects.StationTelemetryParam import StationTelemetryParam


class StationTelemetryParamRepository(Repository):
    """A Repository class for the StationTelemetryParam class
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
            StationTelemetryParam
        """
        selectCursor = self.db.cursor()
        selectCursor.execute(
            """select * from station_telemetry_param where id = %s""", (id,))
        record = selectCursor.fetchone()

        dbObject = self.create()
        if (record is not None):
            dbObject.id = record["id"]
            dbObject.stationId = record["station_id"]
            dbObject.createdTs = record["created_ts"]
            dbObject.latestTs = record["latest_ts"]
            dbObject.validToTs = record["valid_to_ts"]
            dbObject.p1 = record["p1"]
            dbObject.p2 = record["p2"]
            dbObject.p3 = record["p3"]
            dbObject.p4 = record["p4"]
            dbObject.p5 = record["p5"]
            dbObject.b1 = record["b1"]
            dbObject.b2 = record["b2"]
            dbObject.b3 = record["b3"]
            dbObject.b4 = record["b4"]
            dbObject.b5 = record["b5"]
            dbObject.b6 = record["b6"]
            dbObject.b7 = record["b7"]
            dbObject.b8 = record["b8"]
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
            StationTelemetryParam
        """
        newObject = self.create()
        if ("tPARM" in data):
            # Remove one second since that will give us a more accurate timestamp
            newObject.createdTs = int(time.time()) - 1
            newObject.p1 = data["tPARM"][0].replace('\x00', '')
            newObject.p2 = data["tPARM"][1].replace('\x00', '')
            newObject.p3 = data["tPARM"][2].replace('\x00', '')
            newObject.p4 = data["tPARM"][3].replace('\x00', '')
            newObject.p5 = data["tPARM"][4].replace('\x00', '')
            newObject.b1 = data["tPARM"][5].replace('\x00', '')
            newObject.b2 = data["tPARM"][6].replace('\x00', '')
            newObject.b3 = data["tPARM"][7].replace('\x00', '')
            newObject.b4 = data["tPARM"][8].replace('\x00', '')
            newObject.b5 = data["tPARM"][9].replace('\x00', '')
            newObject.b6 = data["tPARM"][10].replace('\x00', '')
            newObject.b7 = data["tPARM"][11].replace('\x00', '')
            newObject.b8 = data["tPARM"][12].replace('\x00', '')
        return newObject

    def create(self):
        """Creates an empty StationTelemetryParam object

        Returns:
            StationTelemetryParam
        """
        return StationTelemetryParam(self.db)
