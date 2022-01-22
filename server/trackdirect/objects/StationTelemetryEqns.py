from trackdirect.common.Model import Model


class StationTelemetryEqns(Model):
    """StationTelemetryEqns represents the telemetry equations sent by the related station
    """

    def __init__(self, db):
        """The __init__ method.

        Args:
            db (psycopg2.Connection): Database connection
        """
        Model.__init__(self, db)
        self.id = None
        self.stationId = None
        self.createdTs = None
        self.latestTs = None
        self.validToTs = None
        self.a1 = None
        self.b1 = None
        self.c1 = None
        self.a2 = None
        self.b2 = None
        self.c2 = None
        self.a3 = None
        self.b3 = None
        self.c3 = None
        self.a4 = None
        self.b4 = None
        self.c4 = None
        self.a5 = None
        self.b5 = None
        self.c5 = None

    def validate(self):
        """Returns true on success (when object content is valid), otherwise false

        Returns:
            True on success otherwise False
        """
        if (type(self.stationId) != int or self.stationId <= 0):
            return False

        return True

    def save(self):
        """Save object data to database if attribute data is valid

        Returns:
            Returns true on success otherwise false
        """
        if (self.validate()):
            if (self.isExistingObject()):
                return self.update()
            else:
                cursor = self.db.cursor()
                cursor.execute("""update station_telemetry_eqns
                    set latest_ts = %s
                    where station_id = %s
                        and valid_to_ts is null
                        and a1::numeric = %s
                        and b1::numeric = %s
                        and c1::numeric = %s

                        and a2::numeric = %s
                        and b2::numeric = %s
                        and c2::numeric = %s

                        and a3::numeric = %s
                        and b3::numeric = %s
                        and c3::numeric = %s

                        and a4::numeric = %s
                        and b4::numeric = %s
                        and c4::numeric = %s

                        and a5::numeric = %s
                        and b5::numeric = %s
                        and c5::numeric = %s""",

                               (self.createdTs,
                                self.stationId,
                                self.a1,
                                self.b1,
                                self.c1,

                                self.a2,
                                self.b2,
                                self.c2,

                                self.a3,
                                self.b3,
                                self.c3,

                                self.a4,
                                self.b4,
                                self.c4,

                                self.a5,
                                self.b5,
                                self.c5))

                if (cursor.rowcount == 0):
                    return self.insert()
                else:
                    # We do not insert it since it was equal to the existsing row
                    return True
        return False

    def insert(self):
        """Method to call when we want to save a new object to database

        Returns:
            True on success otherwise False
        """
        if (not self.isExistingObject()):
            insertCursor = self.db.cursor()
            insertCursor.execute("""update station_telemetry_eqns
                set valid_to_ts = %s
                where station_id = %s
                    and valid_to_ts is null""", (
                self.createdTs,
                self.stationId))

            insertCursor.execute("""insert into station_telemetry_eqns(station_id, created_ts, latest_ts, a1, b1, c1, a2, b2, c2, a3, b3, c3, a4, b4, c4, a5, b5, c5)
                values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                                 (self.stationId,
                                  self.createdTs,
                                  self.timestamp,

                                  self.a1,
                                  self.b1,
                                  self.c1,

                                  self.a2,
                                  self.b2,
                                  self.c2,

                                  self.a3,
                                  self.b3,
                                  self.c3,

                                  self.a4,
                                  self.b4,
                                  self.c4,

                                  self.a5,
                                  self.b5,
                                  self.c5))
            return True
        else:
            return False

    def update(self):
        """Method to call when we want to save changes to database

        Returns:
            True on success otherwise False
        """
        return False
