import re


class PacketCommentPolicy:
    """The PacketCommentPolicy class handles logic to format comments."""

    def __init__(self):
        """Initialize the PacketCommentPolicy class."""
        pass

    def get_comment(self, data, packet_type_id):
        """Returns the packet comment.

        Args:
            data (dict): Raw packet data.
            packet_type_id (int): Packet type id.

        Returns:
            str: Formatted comment.
        """
        comment = None
        if packet_type_id == 7 and "message_text" in data:
            # We save messages as a comment (a message packet does not have a comment so this column is free)
            comment = data["message_text"]
        elif packet_type_id == 10 and "status" in data:
            # We save status as comment (a status message does not have a comment so this column is free)
            comment = data["status"]
        elif "comment" in data:
            comment = data["comment"]

        if isinstance(comment, bytes):
            comment = comment.decode('ascii', 'ignore')
            comment = comment.replace('\x00', '')

        return self._format_comment(comment)

    def _format_comment(self, comment):
        """Remove junk from comment.

        Args:
            comment (str): Comment from packet.

        Returns:
            str: Cleaned comment.
        """
        if comment is None:
            return None

        junk_list = [
            "!=","!=", "]=", "]=", ">=", ">=", "_%", "_%", "_#", "_#", "_\"", "_\"", "_$", "_$", "_)", "_)", "_(", "_(",
            "()", "()", "^", "^", "\\x", "\\x", "/", "/", "\\!", "\\!", "1}", "1}", "_1", "_1", "\"(}", "\"(}", "=", "]",
            ".../..."
        ]

        for junk in junk_list:
            comment = self._lchop(comment, junk)
            comment = self._rchop(comment, junk)

        comment = self._lchop_regex(comment, r"\.\.\.\/\d\d\d")
        comment = self._lchop_regex(comment, r"\d\d\d\/\d\d\d")

        if len(comment) <= 1:
            # Comments with one letter are probably wrong
            comment = None

        return comment

    def _rchop(self, string, substr):
        """Chops substr from right of string.

        Args:
            string (str): String to do modification on.
            substr (str): Substr to look for in string.

        Returns:
            str: Updated version of string.
        """
        if string and string.endswith(substr):
            return string[:-len(substr)]
        return string

    def _lchop(self, string, substr):
        """Chops substr from left of string.

        Args:
            string (str): String to do modification on.
            substr (str): Substr to look for in string.

        Returns:
            str: Updated version of string.
        """
        if string and string.startswith(substr):
            return string[len(substr):]
        return string

    def _lchop_regex(self, string, substr_regex):
        """Chops substr from left of string using regex.

        Args:
            string (str): String to do modification on.
            substr_regex (str): Substr regex to look for in string.

        Returns:
            str: Updated version of string.
        """
        regex = re.compile(substr_regex)
        if string:
            match = re.match(regex, string)
            if match:
                return string[len(match.group(0)):]
        return string