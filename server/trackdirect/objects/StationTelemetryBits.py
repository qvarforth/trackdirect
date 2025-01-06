from server.trackdirect.common.Model import Model


class StationTelemetryBits(Model):
    """StationTelemetryBits represents the telemetry bits sent by the related station
    """

    def __init__(self, db):
        """The __init__ method.

        Args:
            db (psycopg2.Connection): Database connection
        """
        super().__init__(db)
        self.station_id = None
        self.created_ts = None
        self.latest_ts = None
        self.valid_to_ts = None
        self.bits = None
        self.title = None

    def validate(self) -> bool:
        """Returns true on success (when object content is valid), otherwise false

        Returns:
            True on success otherwise False
        """
        return isinstance(self.station_id, int) and self.station_id > 0

    def insert(self) -> bool:
        """Method to call when we want to save a new object to database

        Returns:
            True on success otherwise False
        """
        if not self.is_existing_object():
            try:
                with self.db.cursor() as cursor:
                    cursor.execute("""UPDATE station_telemetry_bits
                                      SET valid_to_ts = %s
                                      WHERE station_id = %s
                                      AND valid_to_ts IS NULL""",
                                   (self.created_ts, self.station_id))

                    cursor.execute("""INSERT INTO station_telemetry_bits(
                                          station_id,
                                          created_ts,
                                          latest_ts,
                                          bits,
                                          title)
                                      VALUES (%s, %s, %s, %s, %s)""",
                                   (self.station_id,
                                    self.created_ts,
                                    self.created_ts,
                                    self.bits,
                                    self.title))
                self.db.commit()
                return True
            except Exception as e:
                self.db.rollback()
                print(f"Error inserting StationTelemetryBits: {e}")
                return False
        return False

    def update(self) -> bool:
        """Method to call when we want to save changes to database

        Returns:
            True on success otherwise False
        """
        # Implement the update logic if needed
        return False