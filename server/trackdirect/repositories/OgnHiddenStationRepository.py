from trackdirect.common.Repository import Repository
from trackdirect.objects.OgnHiddenStation import OgnHiddenStation


class OgnHiddenStationRepository(Repository):
    """A Repository class for the OgnHiddenStation class
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
            OgnHiddenStation
        """
        selectCursor = self.db.cursor()
        selectCursor.execute(
            """select * from ogn_hidden_station where id = %s""", (id,))
        record = selectCursor.fetchone()

        dbObject = self.create()
        if (record is not None):
            dbObject = self.getObjectFromRecord(record)
        else:
            # station do not exists, return empty object
            pass

        selectCursor.close()
        return dbObject

    def getObjectByHashedName(self, hashedName, createNewIfMissing):
        """The getObjectById method is supposed to return an object based on the specified id in database

        Args:
            hashedName (string):           Uniqe hash for station
            createNewIfMissing (boolean):  Set to true if a new should be created if no one is found

        Returns:
            OgnHiddenStation instance
        """
        selectCursor = self.db.cursor()
        selectCursor.execute(
            """select * from ogn_hidden_station where hashed_name = %s""", (str(hashedName),))
        record = selectCursor.fetchone()

        if (record is not None):
            dbObject = self.getObjectFromRecord(record)
        elif (createNewIfMissing):
            # not exist, create it
            dbObject = self.create()
            dbObject.hashedName = hashedName
            dbObject.save()
        else:
            # ogn_device do not exists, return empty object
            dbObject = self.create()

        selectCursor.close()
        return dbObject

    def getObjectFromRecord(self, record):
        """Returns a OgnHiddenStation object based on the specified database record dict

        Args:
            record (dict):  A database record dict from the ogn_device database table

        Returns:
            A OgnHiddenStation object
        """
        dbObject = self.create()
        if (record is not None):
            dbObject.id = int(record["id"])
            dbObject.name = record["hashed_name"]

        return dbObject

    def create(self):
        """Creates an empty OgnHiddenStation object

        Returns:
            OgnHiddenStation instance
        """
        return OgnHiddenStation(self.db)
