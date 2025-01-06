import time
from server.trackdirect.common.Repository import Repository
from server.trackdirect.objects.PacketOgn import PacketOgn


class PacketOgnRepository(Repository):
    """A Repository class for the PacketOgn class."""

    def __init__(self, db):
        """Initialize the PacketOgnRepository with a database connection.

        Args:
            db (psycopg2.Connection): Database connection
        """
        super().__init__(db)

    def get_object_by_id(self, id: int) -> PacketOgn:
        """Return an object based on the specified id in the database.

        Args:
            id (int): Database row id

        Returns:
            PacketOgn: The PacketOgn object corresponding to the id
        """
        cursor = self.db.cursor()
        cursor.execute("SELECT * FROM packet_ogn WHERE id = %s", (id,))
        record = cursor.fetchone()
        cursor.close()
        return self.get_object_from_record(record)

    def get_object_by_packet_id_and_timestamp(self, id: int, timestamp: int) -> PacketOgn:
        """Return an object based on the specified packet id and timestamp in the database.

        Args:
            id (int): Database row id
            timestamp (int): Unix timestamp for the requested packet

        Returns:
            PacketOgn: The PacketOgn object corresponding to the packet id and timestamp
        """
        cursor = self.db.cursor()
        cursor.execute("SELECT * FROM packet_ogn WHERE packet_id = %s AND timestamp = %s", (id, timestamp))
        record = cursor.fetchone()
        cursor.close()
        return self.get_object_from_record(record)

    def get_object_from_record(self, record: dict) -> PacketOgn:
        """Convert a database record to a PacketOgn object.

        Args:
            record (dict): Database record dict to convert to a PacketOgn object

        Returns:
            PacketOgn: A PacketOgn object
        """
        db_object = PacketOgn(self.db)
        if record:
            db_object.id = record["id"]
            db_object.packet_id = int(record["packet_id"])
            db_object.station_id = int(record["station_id"])
            db_object.timestamp = int(record["timestamp"])
            db_object.ogn_sender_address = record['ogn_sender_address']
            db_object.ogn_address_type_id = record['ogn_address_type_id']
            db_object.ogn_aircraft_type_id = record['ogn_aircraft_type_id']
            db_object.ogn_climb_rate = record['ogn_climb_rate']
            db_object.ogn_turn_rate = record['ogn_turn_rate']
            db_object.ogn_signal_to_noise_ratio = record['ogn_signal_to_noise_ratio']
            db_object.ogn_bit_errors_corrected = record['ogn_bit_errors_corrected']
            db_object.ogn_frequency_offset = record['ogn_frequency_offset']
        return db_object

    def get_object_from_packet_data(self, data: dict) -> PacketOgn:
        """Create a PacketOgn object from raw packet data.

        Note:
            stationId will not be set.

        Args:
            data (dict): Raw packet data

        Returns:
            PacketOgn: A PacketOgn object created from the raw packet data
        """
        new_object = self.create()
        if "ogn" in data:
            # Remove one second since that will give us a more accurate timestamp
            new_object.timestamp = int(time.time()) - 1

            ogn_data = data["ogn"]
            new_object.ogn_sender_address = ogn_data.get("ogn_sender_address")
            new_object.ogn_address_type_id = ogn_data.get("ogn_address_type_id")
            new_object.ogn_aircraft_type_id = ogn_data.get("ogn_aircraft_type_id")
            new_object.ogn_climb_rate = ogn_data.get("ogn_climb_rate")
            new_object.ogn_turn_rate = ogn_data.get("ogn_turn_rate")
            new_object.ogn_signal_to_noise_ratio = ogn_data.get("ogn_signal_to_noise_ratio")
            new_object.ogn_bit_errors_corrected = ogn_data.get("ogn_bit_errors_corrected")
            new_object.ogn_frequency_offset = ogn_data.get("ogn_frequency_offset")

        return new_object

    def create(self) -> PacketOgn:
        """Create an empty PacketOgn object.

        Returns:
            PacketOgn: An empty PacketOgn object
        """
        return PacketOgn(self.db)