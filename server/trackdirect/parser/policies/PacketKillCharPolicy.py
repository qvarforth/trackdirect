class PacketKillCharPolicy:
    """The PacketKillCharPolicy class handles logic related to packet kill character."""

    def __init__(self):
        """The __init__ method."""
        pass

    def has_kill_character(self, data):
        """A packet may contain a kill char, if exists the object/item should be hidden on map.

        Args:
            data (dict): Raw packet data

        Returns:
            bool: True if the object name ends with '_', False otherwise
        """
        object_name = data.get("object_name")
        return bool(object_name and object_name.endswith('_'))