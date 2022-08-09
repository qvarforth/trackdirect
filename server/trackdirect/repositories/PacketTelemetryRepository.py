import time

from trackdirect.common.Repository import Repository
from trackdirect.objects.PacketTelemetry import PacketTelemetry
from trackdirect.database.PacketTelemetryTableCreator import PacketTelemetryTableCreator
from trackdirect.exceptions.TrackDirectMissingTableError import TrackDirectMissingTableError


class PacketTelemetryRepository(Repository):
    """A Repository class for the PacketTelemetry class
    """

    def __init__(self, db):
        """The __init__ method.

        Args:
            db (psycopg2.Connection):    Database connection
        """
        self.db = db
        self.packetTelemetryTableCreator = PacketTelemetryTableCreator(self.db)
        self.packetTelemetryTableCreator.disableCreateIfMissing()

    def getObjectById(self, id):
        """The getObjectById method is supposed to return an object based on the specified id in database

        Args:
            id (int):  Database row id

        Returns:
            PacketTelemetry
        """
        selectCursor = self.db.cursor()
        selectCursor.execute("""select * from packet_telemetry where id = %s""", (id,))
        record = selectCursor.fetchone()
        selectCursor.close()
        return self.getObjectFromRecord(record)

    def getObjectByPacketIdAndTimestamp(self, id, timestamp):
        """Returns an object based on the specified packet id in database

        Args:
            id (int):         Database row id
            timestamp (int):  Unix timestamp for requested packet

        Returns:
            PacketTelemetry
        """
        try:
            table = self.packetTelemetryTableCreator.getPacketTelemetryTable(
                timestamp)
            selectCursor = self.db.cursor()
            selectCursor.execute("""select * from """ +
                                 table + """ where packet_id = %s""", (id,))
            record = selectCursor.fetchone()
            selectCursor.close()
            return self.getObjectFromRecord(record)
        except TrackDirectMissingTableError as e:
            return self.create()

    def getObjectFromRecord(self, record):
        """Returns a packet telemetry object from a record

        Args:
            record (dict):  Database record dict to convert to a packet telemetry object

        Returns:
            A packet telemetry object
        """
        dbObject = self.create()
        if (record is not None):
            dbObject.id = record["id"]
            dbObject.packetId = int(record["packet_id"])
            dbObject.stationId = int(record["station_id"])
            dbObject.timestamp = int(record["timestamp"])
            dbObject.val1 = int(record["val1"])
            dbObject.val2 = int(record["val2"])
            dbObject.val3 = int(record["val3"])
            dbObject.val4 = int(record["val4"])
            dbObject.val5 = int(record["val5"])
            dbObject.bits = int(record["bits"])
            dbObject.seq = int(record["seq"])
        return dbObject

    def getObjectFromPacketData(self, data):
        """Create object from raw packet data

        Note:
            stationId will not be set

        Args:
            data (dict):  Raw packet data

        Returns:
            PacketTelemetry
        """
        newObject = self.create()
        if ("telemetry" in data):
            # Remove one second since that will give us a more accurate timestamp
            newObject.timestamp = int(time.time()) - 1

            if ("vals" in data["telemetry"]):
                newObject.val1 = data["telemetry"]["vals"][0]
                newObject.val2 = data["telemetry"]["vals"][1]
                newObject.val3 = data["telemetry"]["vals"][2]
                newObject.val4 = data["telemetry"]["vals"][3]
                newObject.val5 = data["telemetry"]["vals"][4]

            if ("bits" in data["telemetry"]):
                newObject.bits = data["telemetry"]["bits"]

            if ("seq" in data["telemetry"]):
                if isinstance(data["telemetry"]["seq"], str):
                    try:
                        newObject.seq = int(data["telemetry"]["seq"], 10)
                    except ValueError:
                        newObject.seq = None
                elif isinstance(data["telemetry"]["seq"], int):
                    newObject.seq = data["telemetry"]["seq"]
        return newObject

    def create(self):
        """Creates an empty PacketTelemetry object

        Returns:
            PacketTelemetry
        """
        return PacketTelemetry(self.db)
