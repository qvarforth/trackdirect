from trackdirect.exceptions.TrackDirectParseError import TrackDirectParseError


class AprsPacketTypePolicy():
    """The AprsPacketTypePolicy class can answer questions related to what packet type
    """

    def __init__(self):
        """The __init__ method.
        """
        self.onlyPositionCharList = []
        self.generalPositionCharList = []
        self.objectCharList = []
        self.itemCharList = []
        self.weatherCharList = []
        self.telemetryCharList = []
        self.messageCharList = []
        self.queryCharList = []
        self.statusCharList = []
        self.otherCharList = []
        self._initPacketTypeArrays()

    def getPacketType(self, packet):
        """Returns the packet type id

        Args:
            packet (Packet):  Packet that we want analyze

        Returns:
            Packet type id as integer
        """
        if (packet is None):
            return 11
        elif (packet.sourceId == 4):
            return 12
        else:
            packetTypeChar = self._getPacketTypeChar(packet)

            if (self._isPositionPacketType(packetTypeChar)):
                return 1
            elif (self._isGeneralPositionPacketType(packetTypeChar)):
                if (packet.symbol == "\\" and packet.symbolTable == "/"):
                    return 2
                elif (packet.symbol == "_"):
                    return 3
                else:
                    return 1
            elif (self._isObjectPacketType(packetTypeChar)):
                return 4
            elif (self._isItemPacketType(packetTypeChar)):
                return 5
            elif (self._isWeatherPacketType(packetTypeChar)):
                return 3
            elif (self._isTelemetryPacketType(packetTypeChar)):
                return 6
            elif (self._isMessagePacketType(packetTypeChar)):
                return 7
            elif (self._isQueryPacketType(packetTypeChar)):
                return 8
            elif (self._isStatusPacketType(packetTypeChar)):
                return 10
            elif (self._isOtherPacketType(packetTypeChar)):
                return 11
            else:
                return 11

    def _isPositionPacketType(self, packetTypeChar):
        """Returns true if the specified packet type character is of type position

        Args:
            None

        Returns:
            True if the specified packet type character is of type position
        """
        if (packetTypeChar in self.onlyPositionCharList):
            return True
        else:
            return False

    def _isGeneralPositionPacketType(self, packetTypeChar):
        """Returns true if the specified packet type character is of type general position

        Args:
            None

        Returns:
            True if the specified packet type character is of type general position
        """
        if (packetTypeChar in self.generalPositionCharList):
            return True
        else:
            return False

    def _isObjectPacketType(self, packetTypeChar):
        """Returns true if the specified packet type character is of type object

        Args:
            None

        Returns:
            True if the specified packet type character is of type object
        """
        if (packetTypeChar in self.objectCharList):
            return True
        else:
            return False

    def _isItemPacketType(self, packetTypeChar):
        """Returns true if the specified packet type character is of type item

        Args:
            None

        Returns:
            True if the specified packet type character is of type item
        """
        if (packetTypeChar in self.itemCharList):
            return True
        else:
            return False

    def _isWeatherPacketType(self, packetTypeChar):
        """Returns true if the specified packet type character is of type weather

        Args:
            None

        Returns:
            True if the specified packet type character is of type weather
        """
        if (packetTypeChar in self.weatherCharList):
            return True
        else:
            return False

    def _isTelemetryPacketType(self, packetTypeChar):
        """Returns true if the specified packet type character is of type telemetry

        Args:
            None

        Returns:
            True if the specified packet type character is of type telemetry
        """
        if (packetTypeChar in self.telemetryCharList):
            return True
        else:
            return False

    def _isMessagePacketType(self, packetTypeChar):
        """Returns true if the specified packet type character is of type message

        Args:
            None

        Returns:
            True if the specified packet type character is of type message
        """
        if (packetTypeChar in self.messageCharList):
            return True
        else:
            return False

    def _isQueryPacketType(self, packetTypeChar):
        """Returns true if the specified packet type character is of type query

        Args:
            None

        Returns:
            True if the specified packet type character is of type query
        """
        if (packetTypeChar in self.queryCharList):
            return True
        else:
            return False

    def _isStatusPacketType(self, packetTypeChar):
        """Returns true if the specified packet type character is of type status

        Args:
            None

        Returns:
            True if the specified packet type character is of type status
        """
        if (packetTypeChar in self.statusCharList):
            return True
        else:
            return False

    def _isOtherPacketType(self, packetTypeChar):
        """Returns true if the specified packet type character is of type other

        Args:
            None

        Returns:
            True if the specified packet type character is of type other
        """
        if (packetTypeChar in self.otherCharList):
            return True
        else:
            return False

    def _initPacketTypeArrays(self):
        """Init the packet type arrays

        Args:
            None
        """
        self.onlyPositionCharList.append("`")  # New Mic-E data
        self.onlyPositionCharList.append("'")  # Old Mic-E data
        self.onlyPositionCharList.append("[")  # maidenhead locator beacon
        self.onlyPositionCharList.append("$")  # raw gps

        # Position without timestamp (no APRS messaging), or Ultimeter 2000 WX Station
        self.generalPositionCharList.append("!")
        # Position without timestamp (with APRS messaging)
        self.generalPositionCharList.append("=")
        # Position with timestamp (no APRS messaging)
        self.generalPositionCharList.append("/")
        # Position with timestamp (with APRS messaging)
        self.generalPositionCharList.append("@")

        self.objectCharList.append(";")  # Object

        self.itemCharList.append(")")  # item report

        self.weatherCharList.append("#")  # raw weather report
        self.weatherCharList.append("*")  # complete weather report
        self.weatherCharList.append("_")  # positionless weather report

        self.telemetryCharList.append("T")  # telemetry report"

        self.messageCharList.append(":")  # Message

        self.queryCharList.append("?")  # general query format

        self.statusCharList.append(">")  # Status

        self.otherCharList.append("%")  # agrelo
        self.otherCharList.append("&")  # reserved
        self.otherCharList.append("(")  # unused
        self.otherCharList.append("+")  # reserved
        self.otherCharList.append(",")  # invalid/test format
        self.otherCharList.append("-")  # unused
        self.otherCharList.append(".")  # reserved
        self.otherCharList.append("<")  # station capabilities
        self.otherCharList.append("\\")  # unused
        self.otherCharList.append("]")  # unused
        self.otherCharList.append("^")  # unused
        self.otherCharList.append("{")  # user defined
        self.otherCharList.append("}")  # 3rd party traffic

    def _getPacketTypeChar(self, packet):
        """Returns the packet type char

        Args:
            packet (Packet): Packet object to find type char for

        Returns:
            Packet type char
        """
        try:
            (rawHeader, rawBody) = packet.raw.split(':', 1)
        except:
            raise TrackDirectParseError(
                'Could not split packet into header and body', packet)

        if len(rawBody) == 0:
            raise TrackDirectParseError('Packet body is empty', packet)

        return rawBody[0]
