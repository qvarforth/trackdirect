from trackdirect.common.Model import Model


class OgnDevice(Model):
    """OgnDevice represents a pre registered device in the ogn ddb
    """

    def __init__(self, db):
        """The __init__ method.

        Args:
            db (psycopg2.Connection): Database connection
        """
        Model.__init__(self, db)

        self.deviceType = None
        self.deviceId = None
        self.aircraftModel = None
        self.registration = None
        self.cn = None
        self.tracked = None
        self.identified = None
        self.ddbAircraftType = None  # Do not confuse with the aircraft type in aprs message

    def validate(self):
        """Returns true on success (when object content is valid), otherwise false

        Returns:
            True on success otherwise False
        """
        return True

    def insert(self):
        """Method to call when we want to save a new object to database

        Returns:
            True on success otherwise False
        """
        return False

    def update(self):
        """Method to call when we want to save changes to database

        Returns:
            True on success otherwise False
        """
        return False

    def getDict(self):
        """Returns a dict representation of the object

        Returns:
            Dict representation of the object
        """
        data = {}

        data['device_type'] = self.deviceType
        data['device_id'] = self.deviceId
        data['aircraft_model'] = self.aircraftModel
        data['registration'] = self.registration
        data['cn'] = self.cn
        data['tracked'] = self.tracked
        data['identified'] = self.identified
        data['ddb_aircraft_type'] = self.ddbAircraftType

        return data
