from server.trackdirect.common.Model import Model

class OgnDevice(Model):
    """OgnDevice represents a pre-registered device in the OGN database."""

    def __init__(self, db):
        """
        Initialize an OgnDevice instance.

        Args:
            db (psycopg2.Connection): Database connection.
        """
        super().__init__(db)
        self.device_type = None
        self.device_id = None
        self.aircraft_model = None
        self.registration = None
        self.cn = None
        self.tracked = None
        self.identified = None
        self.ddb_aircraft_type = None  # Do not confuse with the aircraft type in APRS message

    def validate(self) -> bool:
        """
        Validate the object's attributes.

        Returns:
            bool: True if the object's attributes are valid, otherwise False.
        """
        # Add actual validation logic here
        return True

    def insert(self) -> bool:
        """
        Insert the object into the database.

        Returns:
            bool: True on success, otherwise False.
        """
        # Add actual insertion logic here
        return False

    def update(self) -> bool:
        """
        Update the object in the database.

        Returns:
            bool: True on success, otherwise False.
        """
        # Add actual update logic here
        return False

    def to_dict(self) -> dict:
        """
        Get a dictionary representation of the object.

        Returns:
            dict: Dictionary representation of the object.
        """
        return {
            'device_type': self.device_type,
            'device_id': self.device_id,
            'aircraft_model': self.aircraft_model,
            'registration': self.registration,
            'cn': self.cn,
            'tracked': self.tracked,
            'identified': self.identified,
            'ddb_aircraft_type': self.ddb_aircraft_type
        }