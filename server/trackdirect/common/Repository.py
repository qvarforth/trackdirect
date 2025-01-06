import abc

class Repository(abc.ABC):
    """The Repository class is the parent of all repository classes."""

    def __init__(self, db):
        """The __init__ method.

        Args:
            db (psycopg2.Connection): Database connection (with autocommit)
        """
        self.db = db

    @abc.abstractmethod
    def get_object_by_id(self, id: int):
        """The get_object_by_id method is supposed to return an object based on the specified id in the database.

        Args:
            id (int): Database row id

        Returns:
            object
        """
        pass