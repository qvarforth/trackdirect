from server.trackdirect.common.Model import Model


class StationTelemetryEqns(Model):
    """StationTelemetryEqns represents the telemetry equations sent by the related station
    """

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
        self.a1: float | None = None
        self.b1: float | None = None
        self.c1: float | None = None
        self.a2: float | None = None
        self.b2: float | None = None
        self.c2: float | None = None
        self.a3: float | None = None
        self.b3: float | None = None
        self.c3: float | None = None
        self.a4: float | None = None
        self.b4: float | None = None
        self.c4: float | None = None
        self.a5: float | None = None
        self.b5: float | None = None
        self.c5: float | None = None

    def validate(self) -> bool:
        """Returns true on success (when object content is valid), otherwise false

        Returns:
            True on success otherwise False
        """
        if not isinstance(self.station_id, int) or self.station_id <= 0:
            return False
        # Add more validation checks as needed
        return True

    def insert(self) -> bool:
        """Method to call when we want to save a new object to database

        Returns:
            True on success otherwise False
        """
        if not self.is_existing_object():
            with self.db.cursor() as cursor:
                cursor.execute(
                    """UPDATE station_telemetry_eqns
                       SET valid_to_ts = %s
                       WHERE station_id = %s AND valid_to_ts IS NULL""",
                    (self.created_ts, self.station_id)
                )

                cursor.execute(
                    """INSERT INTO station_telemetry_eqns(
                        station_id, created_ts, latest_ts, a1, b1, c1, a2, b2, c2, a3, b3, c3, a4, b4, c4, a5, b5, c5)
                       VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                    (self.station_id, self.created_ts, self.latest_ts,
                     self.a1, self.b1, self.c1,
                     self.a2, self.b2, self.c2,
                     self.a3, self.b3, self.c3,
                     self.a4, self.b4, self.c4,
                     self.a5, self.b5, self.c5)
                )
                self.db.commit()
                return True
        return False

    def update(self) -> bool:
        """Method to call when we want to save changes to database

        Returns:
            True on success otherwise False
        """
        # Implement the update logic as needed
        return False