import datetime
import time
from trackdirect.common.Repository import Repository
from trackdirect.objects.StationTelemetryUnit import StationTelemetryUnit


class StationTelemetryUnitRepository(Repository):
    """A Repository class for the StationTelemetryUnit class
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
            StationTelemetryUnit
        """
        selectCursor = self.db.cursor()
        selectCursor.execute(
            """select * from station_telemetry_unit where id = %s""", (id,))
        record = selectCursor.fetchone()

        dbObject = self.create()
        if (record is not None):
            dbObject.id = record["id"]
            dbObject.stationId = record["station_id"]
            dbObject.createdTs = record["created_ts"]
            dbObject.latestTs = record["latest_ts"]
            dbObject.validToTs = record["valid_to_ts"]
            dbObject.u1 = record["u1"]
            dbObject.u2 = record["u2"]
            dbObject.u3 = record["u3"]
            dbObject.u4 = record["u4"]
            dbObject.u5 = record["u5"]
            dbObject.l1 = record["l1"]
            dbObject.l2 = record["l2"]
            dbObject.l3 = record["l3"]
            dbObject.l4 = record["l4"]
            dbObject.l5 = record["l5"]
            dbObject.l6 = record["l6"]
            dbObject.l7 = record["l7"]
            dbObject.l8 = record["l8"]
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
            StationTelemetryUnit
        """
        newObject = self.create()
        if ("tUNIT" in data):
            # Remove one second since that will give us a more accurate timestamp
            newObject.createdTs = int(time.time()) - 1

            newObject.u1 = data["tUNIT"][0].replace('\x00', '')
            newObject.u2 = data["tUNIT"][1].replace('\x00', '')
            newObject.u3 = data["tUNIT"][2].replace('\x00', '')
            newObject.u4 = data["tUNIT"][3].replace('\x00', '')
            newObject.u5 = data["tUNIT"][4].replace('\x00', '')
            newObject.l1 = data["tUNIT"][5].replace('\x00', '')
            newObject.l2 = data["tUNIT"][6].replace('\x00', '')
            newObject.l3 = data["tUNIT"][7].replace('\x00', '')
            newObject.l4 = data["tUNIT"][8].replace('\x00', '')
            newObject.l5 = data["tUNIT"][9].replace('\x00', '')
            newObject.l6 = data["tUNIT"][10].replace('\x00', '')
            newObject.l7 = data["tUNIT"][11].replace('\x00', '')
            newObject.l8 = data["tUNIT"][12].replace('\x00', '')

        return newObject

    def create(self):
        """Creates an empty StationTelemetryUnit object

        Returns:
            StationTelemetryUnit
        """
        return StationTelemetryUnit(self.db)
