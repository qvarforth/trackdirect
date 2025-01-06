import time
from server.trackdirect.common.Repository import Repository
from server.trackdirect.objects.PacketTelemetry import PacketTelemetry
from server.trackdirect.database.PacketTelemetryTableCreator import PacketTelemetryTableCreator
from server.trackdirect.exceptions.TrackDirectMissingTableError import TrackDirectMissingTableError


class PacketTelemetryRepository(Repository):
    """A Repository class for the PacketTelemetry class."""

    def __init__(self, db):
        """Initialize the repository with a database connection.

        Args:
            db (psycopg2.Connection): Database connection
        """
        super().__init__(db)
        self.packet_telemetry_table_creator = PacketTelemetryTableCreator(self.db)
        self.packet_telemetry_table_creator.disable_create_if_missing()

    def get_object_by_id(self, id):
        """Return an object based on the specified id in the database.

        Args:
            id (int): Database row id

        Returns:
            PacketTelemetry
        """
        with self.db.cursor() as cursor:
            cursor.execute("SELECT * FROM packet_telemetry WHERE id = %s", (id,))
            record = cursor.fetchone()
        return self.get_object_from_record(record)

    def get_object_by_packet_id_and_timestamp(self, id, timestamp):
        """Return an object based on the specified packet id and timestamp in the database.

        Args:
            id (int): Database row id
            timestamp (int): Unix timestamp for requested packet

        Returns:
            PacketTelemetry
        """
        try:
            table = self.packet_telemetry_table_creator.get_table(timestamp)
            with self.db.cursor() as cursor:
                cursor.execute(f"SELECT * FROM {table} WHERE packet_id = %s", (id,))
                record = cursor.fetchone()
            return self.get_object_from_record(record)
        except TrackDirectMissingTableError:
            return self.create()

    def get_object_from_record(self, record):
        """Return a packet telemetry object from a database record.

        Args:
            record (dict): Database record dict to convert to a packet telemetry object

        Returns:
            PacketTelemetry
        """
        db_object = self.create()
        if record is not None:
            db_object.id = record["id"]
            db_object.packet_id = int(record["packet_id"])
            db_object.station_id = int(record["station_id"])
            db_object.timestamp = int(record["timestamp"])
            db_object.val1 = int(record["val1"])
            db_object.val2 = int(record["val2"])
            db_object.val3 = int(record["val3"])
            db_object.val4 = int(record["val4"])
            db_object.val5 = int(record["val5"])
            db_object.bits = int(record["bits"])
            db_object.seq = int(record["seq"])
        return db_object

    def get_object_from_packet_data(self, data):
        """Create an object from raw packet data.

        Note:
            stationId will not be set.

        Args:
            data (dict): Raw packet data

        Returns:
            PacketTelemetry
        """
        new_object = self.create()
        if "telemetry" in data:
            # Remove one second for a more accurate timestamp
            new_object.timestamp = int(time.time()) - 1

            telemetry = data["telemetry"]
            if "vals" in telemetry:
                new_object.val1, new_object.val2, new_object.val3, new_object.val4, new_object.val5 = telemetry["vals"]

            if "bits" in telemetry:
                new_object.bits = telemetry["bits"]

            if "seq" in telemetry:
                seq = telemetry["seq"]
                if isinstance(seq, str):
                    try:
                        new_object.seq = int(seq, 10)
                    except ValueError:
                        new_object.seq = None
                elif isinstance(seq, int):
                    new_object.seq = seq
        return new_object

    def create(self):
        """Create an empty PacketTelemetry object.

        Returns:
            PacketTelemetry
        """
        return PacketTelemetry(self.db)