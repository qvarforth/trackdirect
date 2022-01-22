from trackdirect.common.Model import Model


class Sender(Model):
    """Sender represents the sender of a packet (often same name as station name)
    """

    def __init__(self, db):
        """The __init__ method.

        Args:
            db (psycopg2.Connection): Database connection
        """
        Model.__init__(self, db)

        self.id = None
        self.name = None

    def validate(self):
        """Returns true on success (when object content is valid), otherwise false

        Returns:
            True on success otherwise False
        """
        if (self.name == ''):
            return False

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
                """insert into sender(name) values(%s) RETURNING id""", (self.name.strip(
                ),)
            )
            self.id = insertCursor.fetchone()[0]
            insertCursor.close()
            return True
        else:
            return False

    def update(self):
        """Method to call when we want to save changes to database

        Since packet will be updated in batch we never use this method.

        Returns:
            True on success otherwise False
        """
        return False
