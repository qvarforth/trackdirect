from server.trackdirect.common.Model import Model


class Sender(Model):
    """Sender represents the sender of a packet (often same name as station name)
    """

    def __init__(self, db):
        """Initialize the Sender object.

        Args:
            db (psycopg2.Connection): Database connection
        """
        super().__init__(db)
        self.name: str | None = None

    def validate(self) -> bool:
        """Validate the Sender object.

        Returns:
            bool: True if the object content is valid, otherwise False
        """
        return bool(self.name and self.name.strip())

    def insert(self) -> bool:
        """Insert a new Sender object into the database.

        Since packets will be inserted in batch, this method is not typically used.

        Returns:
            bool: True on success, otherwise False
        """
        if not self.is_existing_object():
            with self.db.cursor() as cursor:
                cursor.execute(
                    """INSERT INTO sender(name) VALUES(%s) RETURNING id""",
                    (self.name.strip(),)
                )
                self.id = cursor.fetchone()[0]
            return True
        return False

    def update(self) -> bool:
        """Update the Sender object in the database.

        Since packets will be updated in batch, this method is not typically used.

        Returns:
            bool: True on success, otherwise False
        """
        return False