import logging
from server.trackdirect.common.Model import Model


class Station(Model):
    """Station represents the object/station that the packet is about
    """

    def __init__(self, db):
        """The __init__ method.

        Args:
            db (psycopg2.Connection): Database connection
        """
        super().__init__(db)
        self.logger = logging.getLogger('trackdirect')

        self.id = None
        self.name = None
        self.latest_sender_id = None
        self.station_type_id = 1  # default to 1
        self.source_id = None

        self.latest_packet_id = None
        self.latest_packet_timestamp = None

        self.latest_location_packet_id = None
        self.latest_location_packet_timestamp = None

        self.latest_weather_packet_id = None
        self.latest_weather_packet_timestamp = None

        self.latest_telemetry_packet_id = None
        self.latest_telemetry_packet_timestamp = None

        # Latest packet with a location that is confirmed to be correct
        self.latest_confirmed_packet_id = None
        self.latest_confirmed_packet_timestamp = None
        self.latest_confirmed_symbol = None
        self.latest_confirmed_symbol_table = None
        self.latest_confirmed_latitude = None
        self.latest_confirmed_longitude = None
        self.latest_confirmed_marker_id = None

        self.latest_ogn_packet_id = None
        self.latest_ogn_packet_timestamp = None
        self.latest_ogn_sender_address = None
        self.latest_ogn_aircraft_type_id = None
        self.latest_ogn_address_type_id = None

    def validate(self) -> bool:
        """Returns true on success (when object content is valid), otherwise false

        Returns:
            True on success otherwise False
        """
        return bool(self.name)

    def insert(self) -> bool:
        """Method to call when we want to save a new object to database

        Since packet will be inserted in batch we never use this method.

        Returns:
            True on success otherwise False
        """
        if not self.is_existing_object():
            with self.db.cursor() as cursor:
                cursor.execute(
                    """INSERT INTO station(name, station_type_id, source_id) 
                    VALUES(%s, %s, %s) RETURNING id""",
                    (self.name.strip(), self.station_type_id, self.source_id)
                )
                self.id = cursor.fetchone()[0]
            return True
        return False

    def update(self) -> bool:
        """Method to call when we want to save changes to database

        Returns:
            True on success otherwise False
        """
        if self.is_existing_object():
            with self.db.cursor() as cursor:
                cursor.execute(
                    """UPDATE station 
                    SET source_id = %s, name = %s, station_type_id = %s 
                    WHERE id = %s AND source_id IS NULL""",
                    (self.source_id, self.name, self.station_type_id, self.id)
                )
            return True
        return False

    def get_short_dict(self) -> dict:
        """Returns a dict representation of the object

        Returns:
            Dict representation of the object
        """
        data = {
            'id': self.id,
            'name': self.name,
            'latest_sender_id': self.latest_sender_id,
            'station_type_id': self.station_type_id,
            'source_id': self.source_id,
            'latest_confirmed_packet_id': int(self.latest_confirmed_packet_id) if self.latest_confirmed_packet_id is not None else None,
            'latest_confirmed_packet_timestamp': self.latest_confirmed_packet_timestamp,
            'latest_confirmed_symbol': self.latest_confirmed_symbol,
            'latest_confirmed_symbol_table': self.latest_confirmed_symbol_table,
            'latest_confirmed_latitude': float(self.latest_confirmed_latitude) if self.latest_confirmed_latitude is not None else None,
            'latest_confirmed_longitude': float(self.latest_confirmed_longitude) if self.latest_confirmed_longitude is not None else None,
            'latest_location_packet_id': self.latest_location_packet_id,
            'latest_location_packet_timestamp': self.latest_location_packet_timestamp,
            'latest_packet_id': int(self.latest_packet_id) if self.latest_packet_id is not None else None,
            'latest_packet_timestamp': self.latest_packet_timestamp,
        }

        return data