
from trackdirect.common.Repository import Repository
from trackdirect.objects.Marker import Marker


class MarkerRepository(Repository):
    """A Repository class for the Marker class
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
            Marker
        """
        selectCursor = self.db.cursor()
        selectCursor.execute(
            """select %s from marker_seq where last_value > %s""", (id, id, ))
        record = selectCursor.fetchone()

        dbObject = self.create()
        if (record is not None):
            dbObject.id = record["id"]

        selectCursor.close()
        return dbObject

    def create(self):
        """Creates an empty Marker object

        Returns:
            Marker
        """
        return Marker(self.db)
