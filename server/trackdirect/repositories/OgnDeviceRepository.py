from random import randint

from trackdirect.common.Repository import Repository
from trackdirect.objects.OgnDevice import OgnDevice


class OgnDeviceRepository(Repository):
    """A Repository class for the OgnDevice class
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
            OgnDevice
        """
        selectCursor = self.db.cursor()
        selectCursor.execute(
            """select * from ogn_device where id = %s""", (id,))
        record = selectCursor.fetchone()

        dbObject = self.create()
        if (record is not None):
            dbObject = self.getObjectFromRecord(record)
        else:
            # ogn_device do not exists, return empty object
            pass

        selectCursor.close()
        return dbObject

    def getObjectByDeviceId(self, deviceId):
        """The getObjectById method is supposed to return an object based on the specified id in database

        Args:
            deviceId (string):  Device Id (corresponds to ogn_sender_address)

        Returns:
            OgnDevice instance
        """
        selectCursor = self.db.cursor()
        selectCursor.execute(
            """select * from ogn_device where device_id like %s""", (deviceId,))
        record = selectCursor.fetchone()

        if (record is not None):
            dbObject = self.getObjectFromRecord(record)
        else:
            # ogn_device do not exists, return empty object
            dbObject = OgnDevice(self.db)

        selectCursor.close()
        return dbObject

    def getObjectFromRecord(self, record):
        """Returns a OgnDevice object based on the specified database record dict

        Args:
            record (dict):  A database record dict from the ogn_device database table

        Returns:
            A OgnDevice object
        """
        dbObject = self.create()
        if (record is not None):
            dbObject.id = randint(1, 9999999)
            dbObject.deviceType = record["device_type"]
            dbObject.deviceId = record["device_id"]
            dbObject.aircraftModel = record["aircraft_model"]
            dbObject.registration = record["registration"]
            dbObject.cn = record["cn"]

            if (record["tracked"] == 'N'):
                dbObject.tracked = False
            else:
                dbObject.tracked = True

            if (record["identified"] == 'N'):
                dbObject.identified = False
            else:
                dbObject.identified = True

            try:
                dbObject.ddbAircraftType = int(record["ddb_aircraft_type"])
            except ValueError:
                pass

        return dbObject

    def create(self):
        """Creates an empty OgnDevice object

        Returns:
            OgnDevice instance
        """
        return OgnDevice(self.db)
