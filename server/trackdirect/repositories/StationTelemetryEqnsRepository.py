import time
from server.trackdirect.common.Repository import Repository
from server.trackdirect.objects.StationTelemetryEqns import StationTelemetryEqns


class StationTelemetryEqnsRepository(Repository):
    """A Repository class for the StationTelemetryEqns class."""

    def __init__(self, db):
        """Initialize the repository with a database connection.

        Args:
            db (psycopg2.Connection): Database connection
        """
        super().__init__(db)

    def get_object_by_id(self, id: int) -> StationTelemetryEqns:
        """Retrieve a StationTelemetryEqns object by its ID from the database.

        Args:
            id (int): Database row ID

        Returns:
            StationTelemetryEqns: The retrieved object or an empty object if not found
        """
        with self.db.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM station_telemetry_eqns WHERE id = %s", (id,)
            )
            record = cursor.fetchone()

        db_object = self.create()
        if record:
            self._populate_object_from_record(db_object, record)

        return db_object

    def get_object_from_packet_data(self, data: dict) -> StationTelemetryEqns:
        """Create a StationTelemetryEqns object from raw packet data.

        Note:
            stationId will not be set.

        Args:
            data (dict): Raw packet data

        Returns:
            StationTelemetryEqns: The created object
        """
        new_object = self.create()
        if "tEQNS" in data:
            new_object.created_ts = str(int(time.time()) - 1)
            self._populate_object_from_data(new_object, data["tEQNS"])

        return new_object

    def create(self) -> StationTelemetryEqns:
        """Create an empty StationTelemetryEqns object.

        Returns:
            StationTelemetryEqns: The created object
        """
        return StationTelemetryEqns(self.db)

    def _populate_object_from_record(self, obj: StationTelemetryEqns, record: dict):
        """Populate a StationTelemetryEqns object from a database record.

        Args:
            obj (StationTelemetryEqns): The object to populate
            record (dict): The database record
        """
        obj.id = record["id"]
        obj.station_id = record["station_id"]
        obj.created_ts = record["created_ts"]
        obj.latest_ts = record["latest_ts"]
        obj.valid_to_ts = record["valid_to_ts"]
        obj.a1, obj.b1, obj.c1 = record["a1"], record["b1"], record["c1"]
        obj.a2, obj.b2, obj.c2 = record["a2"], record["b2"], record["c2"]
        obj.a3, obj.b3, obj.c3 = record["a3"], record["b3"], record["c3"]
        obj.a4, obj.b4, obj.c4 = record["a4"], record["b4"], record["c4"]
        obj.a5, obj.b5, obj.c5 = record["a5"], record["b5"], record["c5"]

    def _populate_object_from_data(self, obj: StationTelemetryEqns, data: list):
        """Populate a StationTelemetryEqns object from packet data.

        Args:
            obj (StationTelemetryEqns): The object to populate
            data (list): The packet data
        """
        for i in range(5):
            setattr(obj, f'a{i+1}', data[i][0])
            setattr(obj, f'b{i+1}', data[i][1])
            setattr(obj, f'c{i+1}', data[i][2])
