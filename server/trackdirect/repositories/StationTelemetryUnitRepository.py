import time
from server.trackdirect.common.Repository import Repository
from server.trackdirect.objects.StationTelemetryUnit import StationTelemetryUnit


class StationTelemetryUnitRepository(Repository):
    """A Repository class for the StationTelemetryUnit class."""

    def __init__(self, db):
        """Initialize the repository with a database connection.

        Args:
            db (psycopg2.Connection): Database connection
        """
        super().__init__(db)

    def get_object_by_id(self, id: int) -> StationTelemetryUnit:
        """Retrieve a StationTelemetryUnit object by its database ID.

        Args:
            id (int): Database row ID

        Returns:
            StationTelemetryUnit: The retrieved object or an empty object if not found
        """
        with self.db.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM station_telemetry_unit WHERE id = %s", (id,)
            )
            record = cursor.fetchone()

        db_object = self.create()
        if record:
            attributes = [
                "id", "stationId", "createdTs", "latestTs", "validToTs",
                "u1", "u2", "u3", "u4", "u5", "l1", "l2", "l3", "l4", "l5", "l6", "l7", "l8"
            ]
            for attr in attributes:
                setattr(db_object, attr, record[attr])

        return db_object

    def get_object_from_packet_data(self, data: dict) -> StationTelemetryUnit:
        """Create a StationTelemetryUnit object from raw packet data.

        Note:
            stationId will not be set.

        Args:
            data (dict): Raw packet data

        Returns:
            StationTelemetryUnit: The created object
        """
        new_object = self.create()
        if "tUNIT" in data:
            new_object.created_ts = int(time.time()) - 1
            attributes = ["u1", "u2", "u3", "u4", "u5", "l1", "l2", "l3", "l4", "l5", "l6", "l7", "l8"]
            for i, attr in enumerate(attributes):
                setattr(new_object, attr, data["tUNIT"][i].replace('\x00', ''))

        return new_object

    def create(self) -> StationTelemetryUnit:
        """Create an empty StationTelemetryUnit object.

        Returns:
            StationTelemetryUnit: The created object
        """
        return StationTelemetryUnit(self.db)
