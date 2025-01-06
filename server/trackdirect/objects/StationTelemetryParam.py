from server.trackdirect.common.Model import Model


class StationTelemetryParam(Model):
    """StationTelemetryParam represents the telemetry parameters sent by the related station."""

    def __init__(self, db):
        """The __init__ method.

        Args:
            db (psycopg2.Connection): Database connection
        """
        super().__init__(db)
        self.station_id: int | None = None
        self.created_ts: str | None = None
        self.latest_ts: str | None = None
        self.valid_to_ts: str | None = None
        self.p1: str | None = None
        self.p2: str | None = None
        self.p3: str | None = None
        self.p4: str | None = None
        self.p5: str | None = None
        self.b1: str | None = None
        self.b2: str | None = None
        self.b3: str | None = None
        self.b4: str | None = None
        self.b5: str | None = None
        self.b6: str | None = None
        self.b7: str | None = None
        self.b8: str | None = None

    def validate(self) -> bool:
        """Returns true on success (when object content is valid), otherwise false.

        Returns:
            True on success otherwise False
        """
        return isinstance(self.station_id, int) and self.station_id > 0

    def insert(self) -> bool:
        """Method to call when we want to save a new object to database.

        Returns:
            True on success otherwise False
        """
        if not self.is_existing_object():
            cursor = self.db.cursor()
            cursor.execute(
                '''UPDATE station_telemetry_param
                   SET valid_to_ts = %s
                   WHERE station_id = %s
                     AND valid_to_ts IS NULL''',
                (self.created_ts, self.station_id)
            )

            cursor.execute(
                '''INSERT INTO station_telemetry_param(
                       station_id, created_ts, latest_ts, p1, p2, p3, p4, p5, b1, b2, b3, b4, b5, b6, b7, b8)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)''',
                (self.station_id, self.created_ts, self.created_ts, self.p1, self.p2, self.p3, self.p4, self.p5,
                 self.b1, self.b2, self.b3, self.b4, self.b5, self.b6, self.b7, self.b8)
            )
            return True
        return False

    def update(self) -> bool:
        """Method to call when we want to save changes to database.

        Returns:
            True on success otherwise False
        """
        return False