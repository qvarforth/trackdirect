from trackdirect.common.Model import Model


class StationTelemetryUnit(Model):
    """StationTelemetryUnit represents the telemetry UNIT sent by the related station
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
                cursor.execute("""update station_telemetry_unit
                    set latest_ts = %s
                    where station_id = %s
                        and valid_to_ts is null
                        and u1 = %s
                        and u2 = %s
                        and u3 = %s
                        and u4 = %s
                        and u5 = %s
                        and l1 = %s
                        and l2 = %s
                        and l3 = %s
                        and l4 = %s
                        and l5 = %s
                        and l6 = %s
                        and l7 = %s
                        and l8 = %s""",
                               (self.createdTs,
                                self.stationId,
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
                                self.l8))

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
            insertCursor.execute("""update station_telemetry_unit
                set valid_to_ts = %s
                where station_id = %s
                and valid_to_ts is null""",
                                 (self.createdTs,
                                  self.stationId))

            insertCursor.execute("""insert into station_telemetry_unit(station_id, created_ts, latest_ts, u1, u2, u3, u4, u5, l1, l2, l3, l4, l5, l6, l7, l8)
                values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                                 (self.stationId,
                                  self.createdTs,
                                  self.createdTs,
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
                                  self.l8))

            return True
        else:
            return False

    def update(self):
        """Method to call when we want to save changes to database

        Returns:
            True on success otherwise False
        """
        return False
