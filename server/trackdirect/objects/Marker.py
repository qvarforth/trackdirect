from trackdirect.common.Model import Model


class Marker(Model):
    """Marker represents the marker that each visible packet has, two packet with the same marker id will be connected on map
    """

    def __init__(self, db):
        """The __init__ method.

        Args:
            db (psycopg2.Connection): Database connection
        """
        Model.__init__(self, db)
        self.id = None

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
            cursor = self.db.cursor()
            cursor.execute("""select nextval('marker_seq')""")
            self.id = cursor.fetchone()[0]
            cursor.close()
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
