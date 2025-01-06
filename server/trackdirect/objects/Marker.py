from server.trackdirect.common.Model import Model


class Marker(Model):
    """Marker represents the marker that each visible packet has.
    Two packets with the same marker id will be connected on the map.
    """

    def __init__(self, db):
        """Initialize the Marker instance.

        Args:
            db (psycopg2.Connection): Database connection
        """
        super().__init__(db)

    def validate(self) -> bool:
        """Validate the object content.

        Returns:
            bool: True if the object content is valid, otherwise False
        """
        return True

    def insert(self) -> bool:
        """Insert a new object into the database.

        Since packets will be inserted in batch, this method is not used.

        Returns:
            bool: True on success, otherwise False
        """
        if not self.is_existing_object():
            cursor = self.db.cursor()
            cursor.execute("""SELECT nextval('marker_seq')""")
            self.id = cursor.fetchone()[0]
            cursor.close()
            return True
        return False

    def update(self) -> bool:
        """Update the object in the database.

        Since packets will be updated in batch, this method is not used.

        Returns:
            bool: True on success, otherwise False
        """
        return False