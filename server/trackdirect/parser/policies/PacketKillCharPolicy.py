class PacketKillCharPolicy():
    """The PacketKillCharPolicy class handles logic related to packet kill character
    """

    def __init__(self):
        """The __init__ method.
        """

    def hasKillCharacter(self, data):
        """A packet may contain a kill char, if exists the object/item should be hidden on map

        Args:
            data (dict):   Raw packet data

        Returns:
            Boolean
        """
        if ("object_name" in data
                and data["object_name"] is not None
                and data["object_name"] != ''
                and data["object_name"].endswith('_')):
            return True
        return False
