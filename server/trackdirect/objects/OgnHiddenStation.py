from server.trackdirect.common.Model import Model
import psycopg2

class OgnHiddenStation(Model):
    """OgnHiddenStation represents a pre-registered device in the ogn ddb."""

    def __init__(self, db):
        """
        Initialize the OgnHiddenStation object.

        Args:
            db (psycopg2.Connection): Database connection.
        """
        super().__init__(db)
        self.hashedName: str | None = None

    def get_station_name(self) -> str | None:
        """
        Returns the unidentifiable station name used for the current hashed name.

        Returns:
            str: The station name if the object exists, otherwise None.
        """
        if self.is_existing_object():
            return 'UNKNOWN' + str(self.id)
        return None

    def validate(self) -> bool:
        """
        Validate the object content.

        Returns:
            bool: True if the object content is valid, otherwise False.
        """
        return True

    def insert(self) -> bool:
        """
        Insert a new object into the database.

        Since packets will be inserted in batch, this method is not used.

        Returns:
            bool: True on success, otherwise False.
        """
        if not self.is_existing_object():
            try:
                cursor = self.db.cursor()
                cursor.execute(
                    """INSERT INTO ogn_hidden_station(hashed_name) VALUES(%s) RETURNING id""",
                    (str(self.hashedName).strip(),)
                )
                self.id = cursor.fetchone()[0]
                self.db.commit()
                cursor.close()
                return True
            except psycopg2.Error as e:
                self.db.rollback()
                print(f"Database error: {e}")
                return False
        return False

    def update(self) -> bool:
        """
        Update the object in the database.

        Returns:
            bool: True on success, otherwise False.
        """
        return False