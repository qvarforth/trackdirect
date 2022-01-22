import datetime
import time

from trackdirect.common.Repository import Repository
from trackdirect.objects.PacketOgn import PacketOgn


class PacketOgnRepository(Repository):
    """A Repository class for the PacketOgn class
    """

    def __init__(self, db):
        """The __init__ method.

        Args:
            db (psycopg2.Connection):   Database connection
        """
        self.db = db

    def getObjectById(self, id):
        """The getObjectById method is supposed to return an object based on the specified id in database

        Args:
            id (int):  Database row id

        Returns:
            PacketOgn
        """
        selectCursor = self.db.cursor()
        selectCursor.execute("""select * from packet_ogn where id = %s""", (id,))
        record = selectCursor.fetchone()
        selectCursor.close()
        return self.getObjectFromRecord(record)

    def getObjectByPacketIdAndTimestamp(self, id, timestamp):
        """Returns an object based on the specified packet id in database

        Args:
            id (int):         Database row id
            timestamp (int):  Unix timestamp for requested packet (must be samt date as packet was received)

        Returns:
            PacketOgn
        """
        selectCursor = self.db.cursor()
        selectCursor.execute("""select * from packet_ogn where packet_id = %s and timestamp = %s""", (id, timestamp,))
        record = selectCursor.fetchone()
        selectCursor.close()
        return self.getObjectFromRecord(record)

    def getObjectFromRecord(self, record):
        """Returns a packet OGN object from a record

        Args:
            record (dict):  Database record dict to convert to a packet OGN object

        Returns:
            A packet OGN object
        """
        dbObject = PacketOgn(self.db)
        if (record is not None):
            dbObject.id = record["id"]
            dbObject.packetId = int(record["packet_id"])
            dbObject.stationId = int(record["station_id"])
            dbObject.timestamp = int(record["timestamp"])

            dbObject.ognSenderAddress = record['ogn_sender_address']
            dbObject.ognAddressTypeId = record['ogn_address_type_id']
            dbObject.ognAircraftTypeId = record['ogn_aircraft_type_id']
            dbObject.ognClimbRate = record['ogn_climb_rate']
            dbObject.ognTurnRate = record['ogn_turn_rate']
            dbObject.ognSignalToNoiseRatio = record['ogn_signal_to_noise_ratio']
            dbObject.ognBitErrorsCorrected = record['ogn_bit_errors_corrected']
            dbObject.ognFrequencyOffset = record['ogn_frequency_offset']
        return dbObject

    def getObjectFromPacketData(self, data):
        """Create object from raw packet data

        Note:
            stationId will not be set

        Args:
            data (dict):  Raw packet data

        Returns:
            PacketOgn
        """
        newObject = self.create()
        if ("ogn" in data):
            # Remove one second since that will give us a more accurate timestamp
            newObject.timestamp = int(time.time()) - 1

            if ("ogn_sender_address" in data["ogn"]):
                newObject.ognSenderAddress = data["ogn"]["ogn_sender_address"]

            if ("ogn_address_type_id" in data["ogn"]):
                newObject.ognAddressTypeId = data["ogn"]["ogn_address_type_id"]

            if ("ogn_aircraft_type_id" in data["ogn"]):
                newObject.ognAircraftTypeId = data["ogn"]["ogn_aircraft_type_id"]

            if ("ogn_climb_rate" in data["ogn"]):
                newObject.ognClimbRate = data["ogn"]["ogn_climb_rate"]

            if ("ogn_turn_rate" in data["ogn"]):
                newObject.ognTurnRate = data["ogn"]["ogn_turn_rate"]

            if ("ogn_signal_to_noise_ratio" in data["ogn"]):
                newObject.ognSignalToNoiseRatio = data["ogn"]["ogn_signal_to_noise_ratio"]

            if ("ogn_bit_errors_corrected" in data["ogn"]):
                newObject.ognBitErrorsCorrected = data["ogn"]["ogn_bit_errors_corrected"]

            if ("ogn_frequency_offset" in data["ogn"]):
                newObject.ognFrequencyOffset = data["ogn"]["ogn_frequency_offset"]

        return newObject

    def create(self):
        """Creates an empty PacketOgn object

        Returns:
            PacketOgn
        """
        return PacketOgn(self.db)
