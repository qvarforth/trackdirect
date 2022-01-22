from trackdirect.common.Model import Model


class StationTelemetryParam(Model):
    """StationTelemetryParam represents the telemetry parameters sent by the related station
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
        self.p1 = None
        self.p2 = None
        self.p3 = None
        self.p4 = None
        self.p5 = None
        self.b1 = None
        self.b2 = None
        self.b3 = None
        self.b4 = None
        self.b5 = None
        self.b6 = None
        self.b7 = None
        self.b8 = None

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
                cursor.execute("""update station_telemetry_param
                    set latest_ts = %s
                    where station_id = %s
                        and valid_to_ts is null
                        and p1 = %s
                        and p2 = %s
                        and p3 = %s
                        and p4 = %s
                        and p5 = %s
                        and b1 = %s
                        and b2 = %s
                        and b3 = %s
                        and b4 = %s
                        and b5 = %s
                        and b6 = %s
                        and b7 = %s
                        and b8 = %s""",
                               (self.createdTs,
                                self.stationId,
                                self.p1,
                                self.p2,
                                self.p3,
                                self.p4,
                                self.p5,
                                self.b1,
                                self.b2,
                                self.b3,
                                self.b4,
                                self.b5,
                                self.b6,
                                self.b7,
                                self.b8))

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
            insertCursor.execute("""update station_telemetry_param
                set valid_to_ts = %s
                where station_id = %s
                    and valid_to_ts is null""",
                                 (self.createdTs,
                                  self.stationId))

            insertCursor.execute("""insert into station_telemetry_param(station_id, created_ts, latest_ts, p1, p2, p3, p4, p5, b1, b2, b3, b4, b5, b6, b7, b8)
                values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                                 (self.stationId,
                                  self.createdTs,
                                  self.createdTs,
                                  self.p1,
                                  self.p2,
                                  self.p3,
                                  self.p4,
                                  self.p5,
                                  self.b1,
                                  self.b2,
                                  self.b3,
                                  self.b4,
                                  self.b5,
                                  self.b6,
                                  self.b7,
                                  self.b8))
            return True
        else:
            return False

    def update(self):
        """Method to call when we want to save changes to database

        Returns:
            True on success otherwise False
        """
        return False
