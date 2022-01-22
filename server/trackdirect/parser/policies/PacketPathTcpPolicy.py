import re


class PacketPathTcpPolicy():
    """PacketPathTcpPolicy is used to figure out if packet is sent using radio or TCP
    """

    def __init__(self, path):
        """The __init__ method.

        Args:
            path (list):      Raw packet path list
        """
        self.path = path

    def isSentByTCP(self):
        """Returns True if packet is sent through TCPIP

        Returns:
            True if packet is sent through TCPIP otherwise False
        """
        if (isinstance(self.path, list)):
            if len(self.path) >= 2 and (re.match(r"^TCPIP\*.*$", self.path[0]) or re.match(r"^TCPXX\*.*$", self.path[0])):
                # first station is TCP (this usually means it is sent over TCP...)
                return True
            if ('qAC' in self.path):
                # Packet was received from the client directly via a verified connection
                return True
            if ('qAX' in self.path):
                # Packet was received from the client directly via a unverified connection
                return True
            if ('qAU' in self.path):
                # Packet was received from the client directly via a UDP connection.
                return True
        return False
