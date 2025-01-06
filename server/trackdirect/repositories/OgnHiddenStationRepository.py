from ..common.Repository import Repository
from ..objects.OgnHiddenStation import OgnHiddenStation
import psycopg2
from typing import Optional


class OgnHiddenStationRepository(Repository):
    """A Repository class for the OgnHiddenStation class."""

    def __init__(self, db):
        """
        Initialize the OgnHiddenStationRepository object.

        Args:
            db (psycopg2.Connection): Database connection.
        """
        super().__init__(db)

    def get_object_by_id(self, id: int) -> Optional[OgnHiddenStation]:
        """
        Return an OgnHiddenStation object based on the specified id in the database.

        Args:
            id (int): Database row id.

        Returns:
            Optional[OgnHiddenStation]: The OgnHiddenStation object if found, otherwise None.
        """
        cursor = self.db.cursor()
        cursor.execute("SELECT * FROM ogn_hidden_station WHERE id = %s", (id,))
        record = cursor.fetchone()
        cursor.close()

        if record is not None:
            return self.get_object_from_record(record)
        return None

    def get_object_by_hashed_name(self, hashed_name: str, create_new_if_missing: bool) -> OgnHiddenStation:
        """
        Return an OgnHiddenStation object based on the specified hashed name in the database.

        Args:
            hashed_name (str): Unique hash for the station.
            create_new_if_missing (bool): Set to True if a new object should be created if none is found.

        Returns:
            OgnHiddenStation: The OgnHiddenStation object.
        """
        cursor = self.db.cursor()
        cursor.execute("SELECT * FROM ogn_hidden_station WHERE hashed_name = %s", (hashed_name,))
        record = cursor.fetchone()
        cursor.close()

        if record is not None:
            return self.get_object_from_record(record)
        elif create_new_if_missing:
            db_object = self.create()
            db_object.hashedName = hashed_name
            db_object.save()
            return db_object
        return self.create()

    def get_object_from_record(self, record: dict) -> OgnHiddenStation:
        """
        Return an OgnHiddenStation object based on the specified database record.

        Args:
            record (dict): A database record from the ogn_hidden_station table.

        Returns:
            OgnHiddenStation: The OgnHiddenStation object.
        """
        db_object = self.create()
        if record is not None:
            db_object.id = int(record["id"])
            db_object.hashedName = record["hashed_name"]
        return db_object

    def create(self) -> OgnHiddenStation:
        """
        Create an empty OgnHiddenStation object.

        Returns:
            OgnHiddenStation: The new OgnHiddenStation object.
        """
        return OgnHiddenStation(self.db)