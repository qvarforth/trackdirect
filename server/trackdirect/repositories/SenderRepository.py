import logging
import collections
from trackdirect.common.Repository import Repository
from trackdirect.objects.Sender import Sender
from trackdirect.objects.Station import Station
from trackdirect.exceptions.TrackDirectMissingSenderError import TrackDirectMissingSenderError


class SenderRepository(Repository):
    """A Repository class for the Sender class
    """

    # static class variables
    senderIdCache = {}
    senderNameCache = {}

    def __init__(self, db):
        """The __init__ method.

        Args:
            db (psycopg2.Connection): Database connection
        """
        self.db = db
        self.logger = logging.getLogger('trackdirect')

    def getObjectById(self, id):
        """The getObjectById method is supposed to return an object based on the specified id in database

        Args:
            id (int):  Database row id

        Returns:
            Sender instance
        """
        selectCursor = self.db.cursor()
        selectCursor.execute("""select * from sender where id = %s""", (id,))
        record = selectCursor.fetchone()

        dbObject = Sender(self.db)
        if (record is not None):
            dbObject.id = record["id"]
            dbObject.name = record["name"]
        else:
            # sender do not exists, return empty object
            pass

        selectCursor.close()
        return dbObject

    def getObjectByName(self, name, createNewIfMissing=True, sourceId=None):
        """Returns an object based on the specified name

        Args:
            name (str):                     Name of the requested sender
            createNewIfMissing (boolean):   Set to true if sender should be created if it can not be found

        Returns:
            Sender instance
        """
        selectCursor = self.db.cursor()
        selectCursor.execute(
            """select * from sender where name = %s""", (name.strip(),))
        record = selectCursor.fetchone()

        dbObject = self.create()
        if (record is not None):
            dbObject.id = record["id"]
            dbObject.name = record["name"]
        elif (createNewIfMissing):
            # sender do not exists, create it
            dbObject.name = name
            dbObject.save()

            # Also create a related station
            stationObject = Station(self.db)
            stationObject.name = name
            stationObject.sourceId = sourceId
            stationObject.save()

        selectCursor.close()
        return dbObject

    def getObjectByStationId(self, stationId):
        """Returns an object based on the specified station id

        Args:
            stationId (int):     Id of the station

        Returns:
            Sender instance
        """
        selectCursor = self.db.cursor()
        selectCursor.execute(
            """select * from sender where id in (select latest_sender_id from station where id = %s)""", (stationId,))
        record = selectCursor.fetchone()

        dbObject = self.create()
        if (record is not None):
            dbObject.id = record["id"]
            dbObject.name = record["name"]

        selectCursor.close()
        return dbObject

    def getCachedObjectById(self, senderId):
        """Get Sender based on sender id

        Args:
            senderId (int):     Id of the sender

        Returns:
            Sender
        """
        if (senderId not in SenderRepository.senderIdCache):
            sender = self.getObjectById(senderId)
            if (sender.isExistingObject()):
                maxNumberOfSenders = 100
                if (len(SenderRepository.senderIdCache) > maxNumberOfSenders):
                    # reset cache
                    SenderRepository.senderIdCache = {}
                SenderRepository.senderIdCache[senderId] = sender
                return sender
        else:
            try:
                return SenderRepository.senderIdCache[senderId]
            except KeyError as e:
                sender = self.getObjectById(senderId)
                if (sender.isExistingObject()):
                    return sender
        raise TrackDirectMissingSenderError(
            'No sender with specified id found')

    def getCachedObjectByName(self, senderName):
        """Get Sender based on sender name

        Args:
            senderName (string):  Sender name

        Returns:
            Sender
        """
        if (senderName not in SenderRepository.senderNameCache):
            sender = self.getObjectByName(senderName, False)
            if (sender.isExistingObject()):
                maxNumberOfSenders = 100
                if (len(SenderRepository.senderNameCache) > maxNumberOfSenders):
                    # reset cache
                    SenderRepository.senderNameCache = {}
                SenderRepository.senderNameCache[senderName] = sender
                return sender
        else:
            try:
                return SenderRepository.senderNameCache[senderName]
            except KeyError as e:
                sender = self.getObjectByName(senderName, False)
                if (sender.isExistingObject()):
                    return sender
        raise TrackDirectMissingSenderError(
            'No sender with specified sender name found')

    def create(self):
        """Creates an empty Sender object

        Returns:
            Sender instance
        """
        return Sender(self.db)
