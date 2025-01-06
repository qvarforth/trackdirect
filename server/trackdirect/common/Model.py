import abc


class Model(abc.ABC):
    """The Model class is the parent of all my models
    """

    def __init__(self, db):
        """The __init__ method."""
        self.id: int | None = None
        self.db = db

    def is_existing_object(self) -> bool:
        """Returns true if the object exists in database

        Returns:
            true if the object exists in database otherwise false
        """
        return isinstance(self.id, int) and self.id is not None and self.id > 0

    @abc.abstractmethod
    def insert(self) -> bool:
        """Insert this object into database

        Returns:
            true on success otherwise false
        """
        pass

    @abc.abstractmethod
    def update(self) -> bool:
        """Update columns in database based on this object

        Returns:
            true on success otherwise false
        """
        pass

    @abc.abstractmethod
    def validate(self) -> bool:
        """Return true if object attribute values are valid

        Returns:
            true if object attribute values are valid otherwise false
        """
        pass

    def save(self) -> bool:
        """Save object data to database if attribute data is valid

        Returns:
            true on success otherwise false
        """
        if self.validate():
            if self.is_existing_object():
                return self.update()
            else:
                return self.insert()
        return False