import logging
from trackdirect.common.Model import Model


class Station(Model):
    """Station represents the object/station that the packet is about
    """

    def __init__(self, db):
        """The __init__ method.

        Args:
            db (psycopg2.Connection): Database connection
        """
        Model.__init__(self, db)
        self.logger = logging.getLogger('trackdirect')

        self.id = None
        self.name = None
        self.latestSenderId = None
        self.stationTypeId = 1  # default to 1
        self.sourceId = None

        self.latestPacketId = None
        self.latestPacketTimestamp = None

        self.latestLocationPacketId = None
        self.latestLocationPacketTimestamp = None

        self.latestWeatherPacketId = None
        self.latestWeatherPacketTimestamp = None

        self.latestTelemetryPacketId = None
        self.latestTelemetryPacketTimestamp = None

        # Latest packet with a location that is confirmed to be correct
        self.latestConfirmedPacketId = None
        self.latestConfirmedPacketTimestamp = None
        self.latestConfirmedSymbol = None
        self.latestConfirmedSymbolTable = None
        self.latestConfirmedLatitude = None
        self.latestConfirmedLongitude = None
        self.latestConfirmedMarkerId = None

        self.latestOgnPacketId = None
        self.latestOgnPacketTimestamp = None
        self.latestOgnSenderAddress = None
        self.latestOgnAircraftTypeId = None
        self.latestOgnAddressTypeId = None

    def validate(self):
        """Returns true on success (when object content is valid), otherwise false

        Returns:
            True on success otherwise False
        """
        if (self.name == ''):
            return False

        return True

    def insert(self):
        """Method to call when we want to save a new object to database

        Since packet will be inserted in batch we never use this method.

        Returns:
            True on success otherwise False
        """
        if (not self.isExistingObject()):
            insertCursor = self.db.cursor()
            insertCursor.execute(
                """insert into station(name, station_type_id, source_id) values(%s, %s, %s) RETURNING id""", (
                    self.name.strip(), self.stationTypeId, self.sourceId)
            )
            self.id = insertCursor.fetchone()[0]
            insertCursor.close()
            return True
        else:
            return False

    def update(self):
        """Method to call when we want to save changes to database

        Returns:
            True on success otherwise False
        """
        if (self.isExistingObject()):
            cursor = self.db.cursor()
            cursor.execute(
                """update station set source_id = %s, name = %s, station_type_id = %s where id = %s and source_id is null""", (
                    self.sourceId, self.name, self.stationTypeId, self.id)
            )
            cursor.close()
            return True
        else:
            return False

    def getShortDict(self):
        """Returns a dict representation of the object

        Returns:
            Dict representation of the object
        """
        data = {}
        data['id'] = self.id

        data['name'] = self.name
        data['latest_sender_id'] = self.latestSenderId
        data['station_type_id'] = self.stationTypeId
        data['source_id'] = self.sourceId

        if (self.latestConfirmedPacketId is not None):
            data['latest_confirmed_packet_id'] = int(
                self.latestConfirmedPacketId)
        else:
            data['latest_confirmed_packet_id'] = None

        data['latest_confirmed_packet_timestamp'] = self.latestConfirmedPacketTimestamp
        data['latest_confirmed_symbol'] = self.latestConfirmedSymbol
        data['latest_confirmed_symbol_table'] = self.latestConfirmedSymbolTable

        if (self.latestConfirmedLatitude is not None):
            data['latest_confirmed_latitude'] = float(
                self.latestConfirmedLatitude)
        else:
            data['latest_confirmed_latitude'] = None

        if (self.latestConfirmedLongitude is not None):
            data['latest_confirmed_longitude'] = float(
                self.latestConfirmedLongitude)
        else:
            data['latest_confirmed_longitude'] = None

        if (self.latestLocationPacketId is not None):
            data['latest_location_packet_id'] = self.latestLocationPacketId
        else:
            data['latest_location_packet_id'] = None

        data['latest_location_packet_timestamp'] = self.latestLocationPacketTimestamp

        if (self.latestPacketId is not None):
            data['latest_packet_id'] = int(self.latestPacketId)
        else:
            data['latest_packet_id'] = None

        data['latest_packet_timestamp'] = self.latestPacketTimestamp

        return data
