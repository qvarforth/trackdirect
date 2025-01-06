import logging
from server.trackdirect.objects.Sender import Sender
from server.trackdirect.objects.Station import Station
from server.trackdirect.exceptions.TrackDirectMissingSenderError import TrackDirectMissingSenderError
from server.trackdirect.common.Repository import Repository


class SenderRepository(Repository):
    """A Repository class for the Sender class."""

    # Static class variables for caching
    senderIdCache = {}
    senderNameCache = {}
    maxNumberOfSenders = 100

    def __init__(self, db):
        """Initialize the SenderRepository with a database connection.

        Args:
            db (psycopg2.Connection): Database connection
        """
        super().__init__(db)
        self.logger = logging.getLogger('trackdirect')

    def get_object_by_id(self, id):
        """Retrieve a Sender object by its ID.

        Args:
            id (int): Database row ID

        Returns:
            Sender: An instance of Sender
        """
        with self.db.cursor() as cursor:
            cursor.execute("SELECT * FROM sender WHERE id = %s", (id,))
            record = cursor.fetchone()

        dbObject = Sender(self.db)
        if record:
            dbObject.id = record["id"]
            dbObject.name = record["name"]

        return dbObject

    def get_object_by_name(self, name, createNewIfMissing=True, sourceId=None):
        """Retrieve a Sender object by its name, optionally creating it if missing.

        Args:
            name (str): Name of the requested sender
            createNewIfMissing (bool): Create sender if not found
            sourceId (int, optional): Source ID for the station

        Returns:
            Sender: An instance of Sender
        """
        with self.db.cursor() as cursor:
            cursor.execute("SELECT * FROM sender WHERE name = %s", (name.strip(),))
            record = cursor.fetchone()

        dbObject = self.create()
        if record:
            dbObject.id = record["id"]
            dbObject.name = record["name"]
        elif createNewIfMissing:
            dbObject.name = name
            dbObject.save()

            stationObject = Station(self.db)
            stationObject.name = name
            stationObject.source_id = sourceId
            stationObject.save()

        return dbObject

    def get_object_by_station_id(self, stationId):
        """Retrieve a Sender object by its associated station ID.

        Args:
            stationId (int): ID of the station

        Returns:
            Sender: An instance of Sender
        """
        with self.db.cursor() as cursor:
            cursor.execute(
                """SELECT * FROM sender WHERE id IN 
                   (SELECT latest_sender_id FROM station WHERE id = %s)""",
                (stationId,)
            )
            record = cursor.fetchone()

        dbObject = self.create()
        if record:
            dbObject.id = record["id"]
            dbObject.name = record["name"]

        return dbObject

    def get_cached_object_by_id(self, senderId):
        """Retrieve a cached Sender object by its ID.

        Args:
            senderId (int): ID of the sender

        Returns:
            Sender: An instance of Sender
        """
        if senderId not in SenderRepository.senderIdCache:
            sender = self.get_object_by_id(senderId)
            if sender.is_existing_object():
                self._cache_sender_by_id(senderId, sender)
                return sender
        else:
            return SenderRepository.senderIdCache[senderId]

        raise TrackDirectMissingSenderError('No sender with specified id found')

    def get_cached_object_by_name(self, senderName):
        """Retrieve a cached Sender object by its name.

        Args:
            senderName (str): Sender name

        Returns:
            Sender: An instance of Sender
        """
        if senderName not in SenderRepository.senderNameCache:
            sender = self.get_object_by_name(senderName, False)
            if sender.is_existing_object():
                self._cache_sender_by_name(senderName, sender)
                return sender
        else:
            return SenderRepository.senderNameCache[senderName]

        raise TrackDirectMissingSenderError('No sender with specified sender name found')

    def create(self):
        """Create an empty Sender object.

        Returns:
            Sender: An instance of Sender
        """
        return Sender(self.db)

    def _cache_sender_by_id(self, senderId, sender):
        """Cache a Sender object by its ID."""
        if len(SenderRepository.senderIdCache) > SenderRepository.maxNumberOfSenders:
            SenderRepository.senderIdCache.clear()
        SenderRepository.senderIdCache[senderId] = sender

    def _cache_sender_by_name(self, senderName, sender):
        """Cache a Sender object by its name."""
        if len(SenderRepository.senderNameCache) > SenderRepository.maxNumberOfSenders:
            SenderRepository.senderNameCache.clear()
        SenderRepository.senderNameCache[senderName] = sender
