from server.trackdirect.common.Model import Model
from server.trackdirect.database.PacketTelemetryTableCreator import PacketTelemetryTableCreator


class PacketTelemetry(Model):
    """PacketTelemetry represents the telemetry data in an APRS packet."""

    def __init__(self, db):
        """Initialize PacketTelemetry with a database connection.

        Args:
            db (psycopg2.Connection): Database connection
        """
        super().__init__(db)
        self.packet_id = None
        self.station_id = None
        self.timestamp = None
        self.val1 = None
        self.val2 = None
        self.val3 = None
        self.val4 = None
        self.val5 = None
        self.bits = None
        self.seq = None

    def validate(self) -> bool:
        """Validate the object content.

        Returns:
            bool: True if the object content is valid, otherwise False.
        """
        return self.station_id > 0 and self.packet_id > 0

    def insert(self) -> bool:
        """Insert a new object into the database.

        Since packets are inserted in batches, this method is not used.

        Returns:
            bool: Always returns False.
        """
        return False

    def update(self) -> bool:
        """Update the object in the database.

        Since packets are updated in batches, this method is not used.

        Returns:
            bool: Always returns False.
        """
        return False

    def is_duplicate(self) -> bool:
        """Check if a duplicate exists in the database.

        Returns:
            bool: True if a duplicate exists, otherwise False.
        """
        packet_telemetry_table_creator = PacketTelemetryTableCreator(self.db)
        packet_telemetry_table_creator.disable_create_if_missing()
        packet_telemetry_table = packet_telemetry_table_creator.get_table(self.timestamp)

        if packet_telemetry_table:
            with self.db.cursor() as select_cursor:
                select_cursor.execute(
                    f"SELECT * FROM {packet_telemetry_table} WHERE station_id = %s ORDER BY timestamp DESC LIMIT 1",
                    (self.station_id,)
                )
                record = select_cursor.fetchone()
                if record and record['seq'] == self.seq:
                    return True
        return False

    def get_dict(self) -> dict:
        """Get a dictionary representation of the packet telemetry.

        Returns:
            dict: A dictionary containing the packet telemetry data.
        """
        return {
            'id': self.id,
            'packet_id': self.packet_id,
            'station_id': self.station_id,
            'timestamp': self.timestamp,
            'val1': self.val1,
            'val2': self.val2,
            'val3': self.val3,
            'val4': self.val4,
            'val5': self.val5,
            'bits': self.bits,
            'seq': self.seq
        }