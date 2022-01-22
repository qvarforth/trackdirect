from trackdirect.common.Model import Model


class StationTelemetryBits(Model):
    """StationTelemetryBits represents the telemetry bits sent by the related station
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
        self.bits = None
        self.title = None

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
                cursor.execute("""update station_telemetry_bits
                    set latest_ts = %s
                    where station_id = %s
                        and valid_to_ts is null
                        and bits = %s
                        and title = %s""",
                               (self.createdTs,
                                self.stationId,
                                self.bits,
                                self.title))

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
            insertCursor.execute("""update station_telemetry_bits
                set valid_to_ts = %s
                where station_id = %s
                    and valid_to_ts is null""",
                                 (self.createdTs,
                                  self.stationId))

            insertCursor.execute("""insert into station_telemetry_bits(
                    station_id,
                    created_ts,
                    latest_ts,
                    bits,
                    title)
                values (%s, %s, %s, %s, %s)""",
                                 (self.stationId,
                                  self.createdTs,
                                  self.createdTs,
                                  self.bits,
                                  self.title))
            return True
        else:
            return False

    def update(self):
        """Method to call when we want to save changes to database

        Returns:
            True on success otherwise False
        """
        return False
