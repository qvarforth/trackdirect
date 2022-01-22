import collections
import re

from trackdirect.exceptions.TrackDirectMissingStationError import TrackDirectMissingStationError
from trackdirect.parser.policies.PacketPathTcpPolicy import PacketPathTcpPolicy


class PacketPathPolicy():
    """PacketPathPolicy handles logic to generate the path for a specified packet
    """

    def __init__(self, path, sourceId, stationRepository, senderRepository):
        """The __init__ method.

        Args:
            path (list):      Raw packet path list
            sourceId (int):   Packet source id
            stationRepository (StationRepository):   StationRepository instance
            senderRepository (SenderRepository):    SenderRepository instance
        """
        self.path = path
        self.sourceId = sourceId
        self.stationRepository = stationRepository
        self.senderRepository = senderRepository

        self.stationIdPath = []
        self.stationNamePath = []
        self.stationLocationPath = []
        self._parsePath()

    def getStationIdPath(self):
        """Returns station id path

        Returns:
            list
        """
        return self.stationIdPath

    def getStationNamePath(self):
        """Returns station name path

        Returns:
            list
        """
        return self.stationNamePath

    def getStationLocationPath(self):
        """Returns station location path, a list of longitude and latitude values

        Returns:
            list
        """
        return self.stationLocationPath

    def _parsePath(self):
        """Parse Station path

        Note:
            Include station in path if
            - Station name is after q-code (this is the I-gate)
            - Station name is before unused path command and a used command exists after (this is a digipeater that has inserted itself into the path)
            - As a precaution we also include stations where name has a * after it (no matter the position in path)
        """
        isQCodeFound = False
        isNonUsedPathCommandFound = False
        packetPathTcpPolicy = PacketPathTcpPolicy(self.path)
        if (packetPathTcpPolicy.isSentByTCP()):
            return

        i = 0
        while i < len(self.path):
            index = i
            i += 1
            name = self.path[index]

            if (isinstance(name, int)):
                name = str(name)

            if (self._isQCode(name)):
                isQCodeFound = True
                continue

            if (self._isPathCommand(name)):
                if (not self._isUsedPathCommand(name)):
                    isNonUsedPathCommandFound = True
                continue

            pathStationName = name.replace('*', '')
            if (not self._isStationNameValid(pathStationName)):
                continue

            if (isQCodeFound
                    or name.find('*') >= 0
                    or not isNonUsedPathCommandFound):
                self._addStationToPath(pathStationName)

    def _addStationToPath(self, name):
        """Returns true if specified string is a Q code

        Args:
            name (string):  station
        """
        try:
            station = self.stationRepository.getCachedObjectByName(
                name, self.sourceId)
            stationId = station.id

            if (stationId not in self.stationIdPath):
                location = self._getStationLatestLocation(stationId)
                if (location is not None):
                    self.stationNamePath.append(name)
                    self.stationIdPath.append(stationId)
                    self.stationLocationPath.append(location)
        except (TrackDirectMissingStationError) as exp:
            pass

    def _isQCode(self, value):
        """Returns true if specified string is a Q code

        Args:
            value (string): value

        Returns:
            Returns true if specified string is a Q code otherwise false
        """
        if (value.upper().find('QA') == 0 and len(value) == 3):
            return True
        else:
            return False

    def _isStationNameValid(self, name):
        """Returns true if specified station name is valid. This method is used to filter out common station names that is not valid.

        Args:
            name (string):  Station name

        Returns:
            Returns true if specified station name is valid otherwise false
        """
        if (name.find('NONE') == 0):
            return False
        elif (name.find('0') == 0 and len(name) == 1):
            return False
        elif (name.find('1') == 0 and len(name) == 1):
            return False
        elif (name.find('2') == 0 and len(name) == 1):
            return False
        elif (name.find('3') == 0 and len(name) == 1):
            return False
        elif (name.find('4') == 0 and len(name) == 1):
            return False
        elif (name.find('5') == 0 and len(name) == 1):
            return False
        elif (name.find('6') == 0 and len(name) == 1):
            return False
        elif (name.find('7') == 0 and len(name) == 1):
            return False
        elif (name.find('8') == 0 and len(name) == 1):
            return False
        elif (name.find('9') == 0 and len(name) == 1):
            return False
        elif (name.find('APRS') == 0 and len(name) == 4):
            return False
        elif (name.find('1-1') == 0 and len(name) == 3):
            return False
        elif (name.find('2-1') == 0 and len(name) == 3):
            return False
        elif (name.find('2-2') == 0 and len(name) == 3):
            return False
        elif (name.find('3-1') == 0 and len(name) == 3):
            return False
        elif (name.find('3-2') == 0 and len(name) == 3):
            return False
        elif (name.find('3-3') == 0 and len(name) == 3):
            return False
        elif (name.find('4-1') == 0 and len(name) == 3):
            return False
        elif (name.find('4-2') == 0 and len(name) == 3):
            return False
        elif (name.find('4-3') == 0 and len(name) == 3):
            return False
        elif (name.find('4-4') == 0 and len(name) == 3):
            return False
        elif (name.find('DSTAR') == 0):
            return False
        elif (name.find('TCP') == 0):
            return False
        elif (name.find('NULL') == 0):
            return False
        elif (name.find('LOCAL') == 0):
            return False
        elif (name.find('GATE') == 0):
            return False
        elif (name.find('DIRECT') == 0 and len(name) == 6):
            return False
        elif (name.find('CWOP') == 0 and len(name) == 6):
            return False
        elif (name.find('DMR') == 0 and len(name) == 3):
            return False
        elif (name.find('ECHO') == 0 and len(name) == 4):
            return False
        elif (name.find('OR1-') == 0):
            return False
        elif (name.find('OR2-') == 0):
            return False

        else:
            return True

    def _isPathCommand(self, value):
        """Returns true if specified value is a path command

        Args:
            value (string):  value

        Returns:
            Returns true if specified value is a path command otherwise false
        """
        if (value.find('WIDE') == 0):
            return True
        elif (value.find('RELAY') == 0):
            return True
        elif (value.find('TRACE') == 0):
            return True
        elif (value.find('RPN') == 0):
            return True
        else:
            return False

    def _isUsedPathCommand(self, value):
        """Returns true if specified value is a path command and it is completly used

        Args:
            value (string):  value

        Returns:
            Returns true if specified value is a path command (and it is completly used) otherwise false
        """
        if (value.find('*') >= 0):
            # If a star is added it means that the path command is completly used
            return True

        if (value.find('WIDE') == 0 or value.find('TRACE') == 0 or value.find('RPN') == 0):
            if (value.find('-') < 0):
                # if the wide/trace command still has a hyphen it means that it is not used up
                # Example: WIDE2-1 (can be used one more time), WIDE2 (can not be used any more)
                return True
        return False

    def _getStationLatestLocation(self, stationId):
        """Get latest location for at specified station

        Args:
            None

        Returns:
            Returns the location of the specified station as an array, first value is latitude, second is longitude
        """
        station = self.stationRepository.getObjectById(stationId)
        if (station.isExistingObject()):
            if (station.latestConfirmedLatitude is not None and station.latestConfirmedLongitude is not None):
                return [station.latestConfirmedLatitude, station.latestConfirmedLongitude]
        return None
