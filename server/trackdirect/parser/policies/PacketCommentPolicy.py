import re


class PacketCommentPolicy():
    """The PacketCommentPolicy class handles logic to format comments
    """

    def __init__(self):
        """The __init__ method.
        """

    def getComment(self, data, packetTypeId):
        """Returns the packet comment

        Args:
            data (dict):         Raw packet data
            packetTypeId (int):  Packet type id

        Returns:
            String
        """
        comment = None
        if (packetTypeId == 7 and "message_text" in data):
            # We save messages as a comment (a message packet does not have a comment so this column is free)
            comment = data["message_text"]
        elif (packetTypeId == 10 and "status" in data):
            # We save status as comment (a status message does not have a comment so this column is free)
            comment = data["status"]
        elif ("comment" in data):
            comment = data["comment"]

        if isinstance(comment, bytes):
            comment = comment.encode('ascii', 'ignore')
            comment = comment.replace('\x00', '')

        return self._formatComment(comment)

    def _formatComment(self, comment):
        """Remove junk from comment

        Args:
            comment (string):   Comment from packet

        Returns:
            String
        """
        comment = self._lchop(comment, "!=")
        comment = self._rchop(comment, "!=")
        comment = self._lchop(comment, "]=")
        comment = self._rchop(comment, "]=")
        comment = self._lchop(comment, ">=")
        comment = self._rchop(comment, ">=")
        comment = self._lchop(comment, "_%")
        comment = self._rchop(comment, "_%")
        comment = self._lchop(comment, "_#")
        comment = self._rchop(comment, "_#")
        comment = self._lchop(comment, "_\"")
        comment = self._rchop(comment, "_\"")
        comment = self._lchop(comment, "_$")
        comment = self._rchop(comment, "_$")
        comment = self._lchop(comment, "_)")
        comment = self._rchop(comment, "_)")
        comment = self._lchop(comment, "_(")
        comment = self._rchop(comment, "_(")
        comment = self._lchop(comment, "()")
        comment = self._rchop(comment, "()")
        comment = self._lchop(comment, "^")
        comment = self._rchop(comment, "^")
        comment = self._lchop(comment, "\\x")
        comment = self._rchop(comment, "\\x")
        comment = self._lchop(comment, "/")
        comment = self._rchop(comment, "/")
        comment = self._lchop(comment, "\\!")
        comment = self._rchop(comment, "\\!")
        comment = self._lchop(comment, "1}")
        comment = self._rchop(comment, "1}")
        comment = self._lchop(comment, "_1")
        comment = self._rchop(comment, "_1")
        comment = self._lchop(comment, "\"(}")
        comment = self._rchop(comment, "\"(}")
        comment = self._rchop(comment, "=")
        comment = self._lchop(comment, "]")
        comment = self._lchopRegex(comment, "\.\.\.\/\d\d\d")
        comment = self._lchopRegex(comment, "\d\d\d\/\d\d\d")
        comment = self._lchop(comment, ".../...")

        if (comment is not None and len(comment) <= 1):
            # Comments with one letter is probably wrong
            comment = None
        return comment

    def _rchop(self, string, substr):
        """Chops substr from right of string

        Args:
            string (str): String to do modification on
            substr (str): Substr to look for in string

        Returns:
            Updated version of string
        """
        if (string is not None and string.endswith(substr)):
            return string[:-len(substr)]
        return string

    def _lchop(self, string, substr):
        """Chops substr from left of string

        Args:
            string (str): String to do modification on
            substr (str): Substr to look for in string

        Returns:
            Updated version of string
        """
        if (string is not None and string.startswith(substr)):
            return string[len(substr):]
        return string

    def _lchopRegex(self, string, substrRegex):
        """Chops substr from left of string

        Args:
            string (str): String to do modification on
            substrRegex (str): Substr to look for in string

        Returns:
            Updated version of string
        """
        regex = re.compile(substrRegex)
        if (string is not None):
            m = re.match(regex, string)
            if (m):
                return string[len(m.group(0)):]
        return string
