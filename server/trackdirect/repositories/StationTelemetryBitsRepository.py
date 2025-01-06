import time
from server.trackdirect.common.Repository import Repository
from server.trackdirect.objects.StationTelemetryBits import StationTelemetryBits


class StationTelemetryBitsRepository(Repository):
    """A Repository class for the StationTelemetryBits class."""

    def __init__(self, db):
        """Initialize the repository with a database connection.

        Args:
            db (psycopg2.Connection): Database connection
        """
        super().__init__(db)

    def get_object_by_id(self, id: int) -> StationTelemetryBits:
        """Retrieve a StationTelemetryBits object by its ID from the database.

        Args:
            id (int): Database row ID

        Returns:
            StationTelemetryBits: The retrieved object or an empty object if not found
        """
        with self.db.cursor() as cursor:
            cursor.execute(
                """SELECT * FROM station_telemetry_bits WHERE id = %s""", (id,))
            record = cursor.fetchone()

        station_telemetry_bits = self.create()
        if record:
            station_telemetry_bits.id = record["id"]
            station_telemetry_bits.station_id = record["station_id"]
            station_telemetry_bits.created_ts = record["created_ts"]
            station_telemetry_bits.latest_ts = record["latest_ts"]
            station_telemetry_bits.valid_to_ts = record["valid_to_ts"]
            station_telemetry_bits.bits = record["bits"]
            station_telemetry_bits.title = record["title"]

        return station_telemetry_bits

    def get_object_from_packet_data(self, data: dict) -> StationTelemetryBits:
        """Create a StationTelemetryBits object from raw packet data.

        Note:
            stationId will not be set.

        Args:
            data (dict): Raw packet data

        Returns:
            StationTelemetryBits: The created object
        """
        station_telemetry_bits = self.create()
        if "tBITS" in data:
            # Remove one second for a more accurate timestamp
            station_telemetry_bits.created_ts = int(time.time()) - 1
            station_telemetry_bits.bits = data["tBITS"].replace('\x00', '')
            station_telemetry_bits.title = data["title"].replace('\x00', '')
        return station_telemetry_bits

    def create(self) -> StationTelemetryBits:
        """Create an empty StationTelemetryBits object.

        Returns:
            StationTelemetryBits: The created object
        """
        return StationTelemetryBits(self.db)
