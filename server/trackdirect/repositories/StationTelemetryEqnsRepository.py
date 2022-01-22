import datetime
import time
from trackdirect.common.Repository import Repository
from trackdirect.objects.StationTelemetryEqns import StationTelemetryEqns


class StationTelemetryEqnsRepository(Repository):
    """A Repository class for the StationTelemetryEqns class
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
            StationTelemetryEqns
        """
        selectCursor = self.db.cursor()
        selectCursor.execute(
            """select * from station_telemetry_eqns where id = %s""", (id,))
        record = selectCursor.fetchone()

        dbObject = self.create()
        if (record is not None):
            dbObject.id = record["id"]
            dbObject.stationId = record["station_id"]
            dbObject.createdTs = record["created_ts"]
            dbObject.latestTs = record["latest_ts"]
            dbObject.validToTs = record["valid_to_ts"]
            dbObject.a1 = record["a1"]
            dbObject.b1 = record["b1"]
            dbObject.c1 = record["c1"]
            dbObject.a2 = record["a2"]
            dbObject.b2 = record["b2"]
            dbObject.c2 = record["c2"]
            dbObject.a3 = record["a3"]
            dbObject.b3 = record["b3"]
            dbObject.c3 = record["c3"]
            dbObject.a4 = record["a4"]
            dbObject.b4 = record["b4"]
            dbObject.c4 = record["c4"]
            dbObject.a5 = record["a5"]
            dbObject.b5 = record["b5"]
            dbObject.c5 = record["c5"]
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
            StationTelemetryEqns
        """
        newObject = self.create()
        if ("tEQNS" in data):
            # Remove one second since that will give us a more accurate timestamp
            newObject.createdTs = int(time.time()) - 1

            newObject.a1 = data["tEQNS"][0][0]
            newObject.b1 = data["tEQNS"][0][1]
            newObject.c1 = data["tEQNS"][0][2]

            newObject.a2 = data["tEQNS"][1][0]
            newObject.b2 = data["tEQNS"][1][1]
            newObject.c2 = data["tEQNS"][1][2]

            newObject.a3 = data["tEQNS"][2][0]
            newObject.b3 = data["tEQNS"][2][1]
            newObject.c3 = data["tEQNS"][2][2]

            newObject.a4 = data["tEQNS"][3][0]
            newObject.b4 = data["tEQNS"][3][1]
            newObject.c4 = data["tEQNS"][3][2]

            newObject.a5 = data["tEQNS"][4][0]
            newObject.b5 = data["tEQNS"][4][1]
            newObject.c5 = data["tEQNS"][4][2]
        return newObject

    def create(self):
        """Creates an empty StationTelemetryEqns object

        Returns:
            StationTelemetryEqns
        """
        return StationTelemetryEqns(self.db)
