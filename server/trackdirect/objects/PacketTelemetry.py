from trackdirect.common.Model import Model
from trackdirect.database.PacketTelemetryTableCreator import PacketTelemetryTableCreator


class PacketTelemetry(Model):
    """PacketTelemetry represents the telemetry data in a APRS packet
    """

    def __init__(self, db):
        """The __init__ method.

        Args:
            db (psycopg2.Connection): Database connection
        """
        Model.__init__(self, db)
        self.id = None
        self.packetId = None
        self.stationId = None
        self.timestamp = None
        self.val1 = None
        self.val2 = None
        self.val3 = None
        self.val4 = None
        self.val5 = None
        self.bits = None
        self.seq = None

    def validate(self):
        """Returns true on success (when object content is valid), otherwise false

        Returns:
            True on success otherwise False
        """
        if (self.stationId <= 0):
            return False

        if (self.packetId <= 0):
            return False

        return True

    def insert(self):
        """Method to call when we want to save a new object to database

        Since packet will be inserted in batch we never use this method.

        Returns:
            True on success otherwise False
        """
        return False

    def update(self):
        """Method to call when we want to save changes to database

        Since packet will be updated in batch we never use this method.

        Returns:
            True on success otherwise False
        """
        return False

    def isDuplicate(self):
        """Method returnes true if a duplicate exists in database

        Returns:
            True if a duplicate exists in database otherwise False
        """
        packetTelemetryTableCreator = PacketTelemetryTableCreator(self.db)
        packetTelemetryTableCreator.disableCreateIfMissing()
        packetTelemetryTable = packetTelemetryTableCreator.getPacketTelemetryTable(
            self.timestamp)
        if (packetTelemetryTable is not None):

            selectCursor = self.db.cursor()
            selectCursor.execute("""select * from """ + packetTelemetryTable +
                                 """ where station_id = %s order by timestamp desc limit 1""", (self.stationId,))

            record = selectCursor.fetchone()
            selectCursor.close()
            if record is not None and record['seq'] == self.seq:
                return True
        return False

    def getDict(self):
        """Returns a packet telemetry dict

        Args:
            None

        Returns:
            A packet telemetry dict
        """
        data = {}
        data['id'] = self.id
        data['packet_id'] = self.packetId
        data['station_id'] = self.stationId
        data['timestamp'] = self.timestamp
        data['val1'] = self.val1
        data['val2'] = self.val2
        data['val3'] = self.val3
        data['val4'] = self.val4
        data['val5'] = self.val5
        data['bits'] = self.bits
        data['seq'] = self.seq
        return data
