import abc


class Model():
    """The Model class is the parent of all my models
    """

    def __init__(self, db):
        """The __init__ method.

        Args:
            id (int):  Database row id
        """
        self.id = None
        self.db = db

    def isExistingObject(self):
        """Returns true if the object exists in database

        Returns:
            true if the object exists in database otherwise false
        """
        if ((type(self.id) == int) and self.id is not None and self.id > 0):
            return True
        else:
            return False

    @abc.abstractmethod
    def insert(self):
        """Insert this object into database

        Returns:
            true on success otherwise false
        """
        return False

    @abc.abstractmethod
    def update(self):
        """Update columns in database based on this object

        Returns:
            true on success otherwise false
        """
        return False

    @abc.abstractmethod
    def validate(self):
        """Return true if object attribute values are valid

        Returns:
            true if object attribute values are valid otherwise false
        """
        return

    def save(self):
        """Save object data to database if attribute data is valid

        Returns:
            true on success otherwise false
        """
        if (self.validate()):
            if (self.isExistingObject()):
                return self.update()
            else:
                return self.insert()
        return False
