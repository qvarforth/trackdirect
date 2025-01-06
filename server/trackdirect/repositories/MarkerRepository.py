from server.trackdirect.common.Repository import Repository
from server.trackdirect.objects.Marker import Marker

class MarkerRepository(Repository):
    """A Repository class for the Marker class."""

    def __init__(self, db):
        """Initialize the MarkerRepository instance.

        Args:
            db (DatabaseConnection): Database connection (with autocommit)
        """
        super().__init__(db)

    def get_object_by_id(self, id: int) -> Marker:
        """Return a Marker object based on the specified id in the database.

        Args:
            id (int): Database row id

        Returns:
            Marker: The Marker object with the specified id, or None if not found
        """
        cursor = self.db.cursor()
        cursor.execute("SELECT * FROM marker WHERE id = %s", (id,))
        record = cursor.fetchone()

        marker = None
        if record is not None:
            marker = self.create()
            marker.id = record["id"]
            # Populate other fields of the marker object as needed
            # e.g., marker.name = record["name"]

        cursor.close()
        return marker

    def create(self) -> Marker:
        """Create an empty Marker object.

        Returns:
            Marker: A new Marker object
        """
        return Marker(self.db)