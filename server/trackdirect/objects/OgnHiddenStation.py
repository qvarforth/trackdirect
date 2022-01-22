
from trackdirect.common.Model import Model


class OgnHiddenStation(Model):
    """OgnDevice represents a pre registered device in the ogn ddb
    """

    def __init__(self, db):
        """The __init__ method.

        Args:
            db (psycopg2.Connection): Database connection
        """
        Model.__init__(self, db)

        self.id = None
        self.hashedName = None

    def getStationName(self):
        """Returns the unidentifiable station name used for the current hashed name

        Returns:
            string
        """
        if (self.isExistingObject()):
            return 'UNKNOWN' + str(self.id)
        else:
            return None

    def validate(self):
        """Returns true on success (when object content is valid), otherwise false

        Returns:
            True on success otherwise False
        """
        return True

    def insert(self):
        """Method to call when we want to save a new object to database

        Since packet will be inserted in batch we never use this method.

        Returns:
            True on success otherwise False
        """
        if (not self.isExistingObject()):
            insertCursor = self.db.cursor()
            insertCursor.execute(
                """insert into ogn_hidden_station(hashed_name) values(%s) RETURNING id""", (str(
                    self.hashedName).strip(),)
            )
            self.id = insertCursor.fetchone()[0]
            insertCursor.close()
            return True
        else:
            return False

    def update(self):
        """Method to call when we want to save changes to database

        Returns:
            True on success otherwise False
        """
        return False
