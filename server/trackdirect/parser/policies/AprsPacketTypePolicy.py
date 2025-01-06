from server.trackdirect.exceptions.TrackDirectParseError import TrackDirectParseError


class AprsPacketTypePolicy:
    """The AprsPacketTypePolicy class can answer questions related to what packet type
    """

    PACKET_TYPE_IDS = {
        'POSITION': 1,
        'GENERAL_POSITION': 2,
        'WEATHER': 3,
        'OBJECT': 4,
        'ITEM': 5,
        'TELEMETRY': 6,
        'MESSAGE': 7,
        'QUERY': 8,
        'STATUS': 10,
        'OTHER': 11,
        'HUBHAB': 12
    }

    def __init__(self):
        """The __init__ method.
        """
        self.packet_type_char_lists = {
            'onlyPositionCharList': ["`", "'", "[", "$"],
            'generalPositionCharList': ["!", "=", "/", "@"],
            'objectCharList': [";"],
            'itemCharList': [")"],
            'weatherCharList': ["#", "*", "_"],
            'telemetryCharList': ["T"],
            'messageCharList': [":"],
            'queryCharList': ["?"],
            'statusCharList': [">"],
            'otherCharList': ["%", "&", "(", "+", ",", "-", ".", "<", "\\", "]", "^", "{", "}"]
        }

    def get_packet_type(self, packet):
        """Returns the packet type id

        Args:
            packet (Packet):  Packet that we want analyze

        Returns:
            Packet type id as integer
        """
        if packet is None:
            return self.PACKET_TYPE_IDS['OTHER']
        elif packet.source_id == 4:
            return self.PACKET_TYPE_IDS['HUBHAB']
        else:
            packet_type_char = self._get_packet_type_char(packet)

            if self._is_packet_type(packet_type_char, 'onlyPositionCharList'):
                return self.PACKET_TYPE_IDS['POSITION']
            elif self._is_packet_type(packet_type_char, 'generalPositionCharList'):
                if packet.symbol == "\\" and packet.symbol_table == "/":
                    return self.PACKET_TYPE_IDS['GENERAL_POSITION']
                elif packet.symbol == "_":
                    return self.PACKET_TYPE_IDS['WEATHER']
                else:
                    return self.PACKET_TYPE_IDS['POSITION']
            elif self._is_packet_type(packet_type_char, 'objectCharList'):
                return self.PACKET_TYPE_IDS['OBJECT']
            elif self._is_packet_type(packet_type_char, 'itemCharList'):
                return self.PACKET_TYPE_IDS['ITEM']
            elif self._is_packet_type(packet_type_char, 'weatherCharList'):
                return self.PACKET_TYPE_IDS['WEATHER']
            elif self._is_packet_type(packet_type_char, 'telemetryCharList'):
                return self.PACKET_TYPE_IDS['TELEMETRY']
            elif self._is_packet_type(packet_type_char, 'messageCharList'):
                return self.PACKET_TYPE_IDS['MESSAGE']
            elif self._is_packet_type(packet_type_char, 'queryCharList'):
                return self.PACKET_TYPE_IDS['QUERY']
            elif self._is_packet_type(packet_type_char, 'statusCharList'):
                return self.PACKET_TYPE_IDS['STATUS']
            elif self._is_packet_type(packet_type_char, 'otherCharList'):
                return self.PACKET_TYPE_IDS['OTHER']
            else:
                return self.PACKET_TYPE_IDS['OTHER']

    def _is_packet_type(self, packet_type_char, char_list_name):
        """Returns true if the specified packet type character is in the given list

        Args:
            packet_type_char (str): The packet type character
            char_list_name (str): The name of the character list

        Returns:
            bool: True if the specified packet type character is in the given list
        """
        return packet_type_char in self.packet_type_char_lists[char_list_name]

    def _get_packet_type_char(self, packet):
        """Returns the packet type char

        Args:
            packet (Packet): Packet object to find type char for

        Returns:
            Packet type char
        """
        try:
            rawHeader, rawBody = packet.raw.split(':', 1)
        except ValueError:
            raise TrackDirectParseError('Could not split packet into header and body', packet)

        if len(rawBody) == 0:
            raise TrackDirectParseError('Packet body is empty', packet)

        return rawBody[0]