from server.trackdirect.common.Model import Model


class StationTelemetryUnit(Model):
    """StationTelemetryUnit represents the telemetry UNIT sent by the related station
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
        self.u1 = None
        self.u2 = None
        self.u3 = None
        self.u4 = None
        self.u5 = None
        self.l1 = None
        self.l2 = None
        self.l3 = None
        self.l4 = None
        self.l5 = None
        self.l6 = None
        self.l7 = None
        self.l8 = None

    def validate(self) -> bool:
        """Returns true on success (when object content is valid), otherwise false

        Returns:
            True on success otherwise False
        """
        return isinstance(self.station_id, int) and self.station_id > 0

    def save(self) -> bool:
        """Save object data to database if attribute data is valid

        Returns:
            Returns true on success otherwise false
        """
        if self.validate():
            if self.is_existing_object():
                return self.update()
            else:
                cursor = self.db.cursor()
                cursor.execute(
                    """UPDATE station_telemetry_unit
                    SET latest_ts = %s
                    WHERE station_id = %s
                        AND valid_to_ts IS NULL
                        AND u1 = %s
                        AND u2 = %s
                        AND u3 = %s
                        AND u4 = %s
                        AND u5 = %s
                        AND l1 = %s
                        AND l2 = %s
                        AND l3 = %s
                        AND l4 = %s
                        AND l5 = %s
                        AND l6 = %s
                        AND l7 = %s
                        AND l8 = %s""",
                    (
                        self.created_ts,
                        self.station_id,
                        self.u1,
                        self.u2,
                        self.u3,
                        self.u4,
                        self.u5,
                        self.l1,
                        self.l2,
                        self.l3,
                        self.l4,
                        self.l5,
                        self.l6,
                        self.l7,
                        self.l8,
                    ),
                )

                if cursor.rowcount == 0:
                    cursor.close()
                    return self.insert()
                else:
                    cursor.close()
                    # We do not insert it since it was equal to the existing row
                    return True
        return False

    def insert(self) -> bool:
        """Method to call when we want to save a new object to database

        Returns:
            True on success otherwise False
        """
        if not self.is_existing_object():
            cursor = self.db.cursor()
            cursor.execute(
                """UPDATE station_telemetry_unit
                SET valid_to_ts = %s
                WHERE station_id = %s
                AND valid_to_ts IS NULL""",
                (self.created_ts, self.station_id),
            )

            cursor.execute(
                """INSERT INTO station_telemetry_unit(
                    station_id, created_ts, latest_ts, u1, u2, u3, u4, u5, l1, l2, l3, l4, l5, l6, l7, l8)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                (
                    self.station_id,
                    self.created_ts,
                    self.created_ts,
                    self.u1,
                    self.u2,
                    self.u3,
                    self.u4,
                    self.u5,
                    self.l1,
                    self.l2,
                    self.l3,
                    self.l4,
                    self.l5,
                    self.l6,
                    self.l7,
                    self.l8,
                ),
            )
            cursor.close()
            return True
        else:
            return False

    def update(self) -> bool:
        """Method to call when we want to save changes to database

        Returns:
            True on success otherwise False
        """
        # Implement the update logic here
        return False