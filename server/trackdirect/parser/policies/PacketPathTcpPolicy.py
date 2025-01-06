import re

class PacketPathTcpPolicy:
    """PacketPathTcpPolicy is used to figure out if packet is sent using radio or TCP
    """

    def __init__(self, path: list):
        """The __init__ method.

        Args:
            path (list): Raw packet path list
        """
        self.path = path

    def is_sent_by_tcp(self) -> bool:
        """Returns True if packet is sent through TCPIP

        Returns:
            True if packet is sent through TCPIP otherwise False
        """
        if isinstance(self.path, list) and len(self.path) >= 2:
            if len(self.path) >= 2 and (re.match(r"^TCPIP\*.*$", self.path[0]) or re.match(r"^TCPXX\*.*$", self.path[0])):
                # first station is TCP (this usually means it is sent over TCP...)
                return True
            if any(keyword in self.path for keyword in ['qAC', 'qAX', 'qAU']):
                # Packet was received from the client directly via a verified, unverified, or UDP connection
                return True
        return False