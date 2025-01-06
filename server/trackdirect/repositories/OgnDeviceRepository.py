from server.trackdirect.common.Repository import Repository
from server.trackdirect.objects.OgnDevice import OgnDevice


class OgnDeviceRepository(Repository):
    """A Repository class for the OgnDevice class."""

    def __init__(self, db):
        """
        Initialize the OgnDeviceRepository instance.

        Args:
            db (DatabaseConnection): Database connection.
        """
        super().__init__(db)

    def get_object_by_id(self, id: int) -> OgnDevice:
        """
        Retrieve an OgnDevice object based on the specified id in the database.

        Args:
            id (int): Database row id.

        Returns:
            OgnDevice: An instance of OgnDevice.
        """
        cursor = self.db.cursor()
        cursor.execute("SELECT * FROM ogn_device WHERE id = %s", (id,))
        record = cursor.fetchone()

        if record is not None:
            db_object = self._get_object_from_record(record)
        else:
            db_object = self._create_empty_object()

        cursor.close()
        return db_object

    def get_object_by_device_id(self, device_id: str) -> OgnDevice:
        """
        Retrieve an OgnDevice object based on the specified device_id in the database.

        Args:
            device_id (str): Device Id (corresponds to ogn_sender_address).

        Returns:
            OgnDevice: An instance of OgnDevice.
        """
        cursor = self.db.cursor()
        cursor.execute("SELECT * FROM ogn_device WHERE device_id LIKE %s", (device_id,))
        record = cursor.fetchone()

        if record is not None:
            db_object = self._get_object_from_record(record)
        else:
            db_object = self._create_empty_object()

        cursor.close()
        return db_object

    def _get_object_from_record(self, record: dict) -> OgnDevice:
        """
        Create an OgnDevice object based on the specified database record.

        Args:
            record (dict): A database record from the ogn_device table.

        Returns:
            OgnDevice: An instance of OgnDevice.
        """
        db_object = self._create_empty_object()
        if record is not None:
            db_object.device_type = record["device_type"]
            db_object.device_id = record["device_id"]
            db_object.aircraft_model = record["aircraft_model"]
            db_object.registration = record["registration"]
            db_object.cn = record["cn"]
            db_object.tracked = record["tracked"] != 'N'
            db_object.identified = record["identified"] != 'N'
            try:
                db_object.ddb_aircraft_type = int(record["ddb_aircraft_type"])
            except ValueError:
                db_object.ddb_aircraft_type = None

        return db_object

    def _create_empty_object(self) -> OgnDevice:
        """
        Create an empty OgnDevice object.

        Returns:
            OgnDevice: An instance of OgnDevice.
        """
        return OgnDevice(self.db)