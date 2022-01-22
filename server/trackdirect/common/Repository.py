
import abc


class Repository():
    """The Repository class is the parent of all my repository classes
    """

    def __init__(self, db):
        """The __init__ method.

        Args:
            db (object):  Database connection (with autocommit)
        """
        self.db = db

    @abc.abstractmethod
    def getObjectById(self, id):
        """The getObjectById method is supposed to return an object based on the specified id in database

        Args:
            id (int):  Database row id

        Returns:
            object
        """
        return
