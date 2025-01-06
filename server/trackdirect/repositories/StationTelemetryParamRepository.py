import time
from server.trackdirect.common.Repository import Repository
from server.trackdirect.objects.StationTelemetryParam import StationTelemetryParam


class StationTelemetryParamRepository(Repository):
    """A Repository class for the StationTelemetryParam class."""

    def __init__(self, db):
        """Initialize the repository with a database connection.

        Args:
            db (psycopg2.Connection): Database connection
        """
        super().__init__(db)

    def get_object_by_id(self, id: int) -> StationTelemetryParam:
        """Retrieve a StationTelemetryParam object by its ID from the database.

        Args:
            id (int): Database row ID

        Returns:
            StationTelemetryParam: The retrieved object or an empty object if not found
        """
        with self.db.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM station_telemetry_param WHERE id = %s", (id,)
            )
            record = cursor.fetchone()

        db_object = self.create()
        if record:
            self._populate_db_object(db_object, record)

        return db_object

    def get_object_from_packet_data(self, data: dict) -> StationTelemetryParam:
        """Create a StationTelemetryParam object from raw packet data.

        Note:
            stationId will not be set.

        Args:
            data (dict): Raw packet data

        Returns:
            StationTelemetryParam: The created object
        """
        new_object = self.create()
        if "tPARM" in data:
            new_object.created_ts = str(int(time.time()) - 1)
            self._populate_from_packet_data(new_object, data["tPARM"])
        return new_object

    def create(self) -> StationTelemetryParam:
        """Create an empty StationTelemetryParam object.

        Returns:
            StationTelemetryParam: The created object
        """
        return StationTelemetryParam(self.db)

    def _populate_db_object(self, db_object: StationTelemetryParam, record: dict):
        """Populate a StationTelemetryParam object with data from a database record.

        Args:
            db_object (StationTelemetryParam): The object to populate
            record (dict): The database record
        """
        db_object.id = record["id"]
        db_object.station_id = record["station_id"]
        db_object.created_ts = record["created_ts"]
        db_object.latest_ts = record["latest_ts"]
        db_object.valid_to_ts = record["valid_to_ts"]
        db_object.p1 = record["p1"]
        db_object.p2 = record["p2"]
        db_object.p3 = record["p3"]
        db_object.p4 = record["p4"]
        db_object.p5 = record["p5"]
        db_object.b1 = record["b1"]
        db_object.b2 = record["b2"]
        db_object.b3 = record["b3"]
        db_object.b4 = record["b4"]
        db_object.b5 = record["b5"]
        db_object.b6 = record["b6"]
        db_object.b7 = record["b7"]
        db_object.b8 = record["b8"]

    def _populate_from_packet_data(self, new_object: StationTelemetryParam, tparm: list):
        """Populate a StationTelemetryParam object with data from packet data.

        Args:
            new_object (StationTelemetryParam): The object to populate
            tparm (list): The packet data
        """
        new_object.p1 = tparm[0].replace('\x00', '')
        new_object.p2 = tparm[1].replace('\x00', '')
        new_object.p3 = tparm[2].replace('\x00', '')
        new_object.p4 = tparm[3].replace('\x00', '')
        new_object.p5 = tparm[4].replace('\x00', '')
        new_object.b1 = tparm[5].replace('\x00', '')
        new_object.b2 = tparm[6].replace('\x00', '')
        new_object.b3 = tparm[7].replace('\x00', '')
        new_object.b4 = tparm[8].replace('\x00', '')
        new_object.b5 = tparm[9].replace('\x00', '')
        new_object.b6 = tparm[10].replace('\x00', '')
        new_object.b7 = tparm[11].replace('\x00', '')
        new_object.b8 = tparm[12].replace('\x00', '')
