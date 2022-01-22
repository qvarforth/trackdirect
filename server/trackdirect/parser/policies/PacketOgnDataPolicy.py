import logging
from twisted.python import log

from trackdirect.parser.policies.AprsPacketSymbolPolicy import AprsPacketSymbolPolicy
from trackdirect.parser.policies.PacketPathTcpPolicy import PacketPathTcpPolicy


class PacketOgnDataPolicy():
    """PacketOgnDataPolicy can answer questions about OGN data in the packet
    """

    def __init__(self, data, ognDeviceRepository, sourceId):
        """The __init__ method.

        Args:
            data (dict):                          Raw packet data
            ognDeviceRepository (OgnDeviceRepository):  OgnDeviceRepository instance
            sourceId (int):                       Source Id
        """
        self.data = data
        self.ognDeviceRepository = ognDeviceRepository

        self.logger = logging.getLogger('trackdirect')

        self.isOgnPositionPacket = self.isOgnPositionPacket(sourceId)
        self.isAllowedToTrack = True
        self.isAllowedToIdentify = True

        self.result = {}
        self._parse()

    def getOgnData(self):
        """Returnes raw OGN data

        Returns:
            Dict of OGN data
        """
        return self.result

    def isOgnPositionPacket(self, sourceId):
        """Returnes true if packet is a OGN Position packet

        Args:
            sourceId (int): Source Id

        Returns:
            Boolean
        """
        if (sourceId == 5):
            if ("comment" in self.data
                    and self.data["comment"] is not None
                    and len(self.data["comment"].strip()) > 10
                    and self.data["comment"].strip().startswith("id")):
                return True

            symbol = self.data['symbol'] if ('symbol' in self.data) else None
            symbolTable = self.data['symbol_table'] if (
                'symbol_table' in self.data) else None
            aprsPacketSymbolPolicy = AprsPacketSymbolPolicy()
            if (aprsPacketSymbolPolicy.isMaybeMovingSymbol(symbol, symbolTable)):
                return True
        else:
            if ("comment" in self.data
                    and self.data["comment"] is not None
                    and len(self.data["comment"].strip()) > 10
                    and self.data["comment"].strip().startswith("id")
                    and "fpm " in self.data["comment"] + " "
                    and "rot " in self.data["comment"] + " "
                    and "dB " in self.data["comment"] + " "):
                return True
        return False

    def _parse(self):
        """Parse the OGN data in packet
        """
        if (not self.isOgnPositionPacket):
            self.result = None
        else:
            packetPathTcpPolicy = PacketPathTcpPolicy(self.data['path'])
            if (not packetPathTcpPolicy.isSentByTCP()):
                self.isAllowedToIdentify = False

            if ("comment" in self.data and self.data["comment"] is not None):
                ognParts = self.data["comment"].split()
                for part in ognParts:
                    if (part.startswith('id')):
                        part = part.replace("-", "")
                        self._parseSenderAddress(part)
                        self._parseSenderDetails(part)

                    elif (part.endswith('fpm')):
                        self._parseClimbRate(part)

                    elif (part.endswith('rot')):
                        self._parseTurnRate(part)

                    elif (part.endswith('dB')):
                        if (self.isAllowedToIdentify and self.isAllowedToTrack):
                            self._parseSignalToNoiseRatio(part)

                    elif (part.endswith('e')):
                        if (self.isAllowedToIdentify and self.isAllowedToTrack):
                            self._parseBitErrorsCorrected(part)

                    elif (part.endswith('kHz')):
                        if (self.isAllowedToIdentify and self.isAllowedToTrack):
                            self._parseFrequencyOffset(part)
                    if (not self.isAllowedToTrack):
                        return

        if (not self.isAllowedToIdentify):
            if ('ogn_sender_address' in self.result):
                self.result['ogn_sender_address'] = None

    def _parseSenderAddress(self, content):
        """Parse th OGN sender address

        Arguments:
            content (string) :  String that contains information to parse
        """
        if ('ogn_sender_address' not in self.result):
            self.isAllowedToIdentify = True
            self.result['ogn_sender_address'] = content[4:10].strip()

            ognDevice = self.ognDeviceRepository.getObjectByDeviceId(
                self.result['ogn_sender_address'])
            if (ognDevice.isExistingObject() and not ognDevice.tracked):
                # Pilot do not want to be tracked, so we skip saving the packet
                self.isAllowedToIdentify = False
                self.isAllowedToTrack = False

            elif (self.result['ogn_sender_address'] == 'ICAFFFFFF'):
                # The Device ID ICAFFFFFF is used by several aircrafts, we can not know what to do with them...
                self.isAllowedToIdentify = False
                self.isAllowedToTrack = False

            elif (not ognDevice.isExistingObject() or not ognDevice.identified):
                # Pilot has not approved to show identifiable data, so we make up a random station name and clear all identifiable data
                self.isAllowedToIdentify = False
        else:
            self.isAllowedToIdentify = False

    def _parseSenderDetails(self, content):
        """Parse OGN aircraft type and OGN address type

        Arguments:
            content (string) :  String that contains information to parse
        """
        if ('ogn_aircraft_type_id' not in self.result):
            try:
                ognSenderDetailsHex = content[2:4]
                ognSenderDetailsBinary = bin(
                    int(ognSenderDetailsHex, 16))[2:].zfill(8)

                stealth = ognSenderDetailsBinary[0:1]
                noTracking = ognSenderDetailsBinary[1:2]
                ognAircraftTypeIdBinary = ognSenderDetailsBinary[2:6]
                ognAddressTypeIdBinary = ognSenderDetailsBinary[6:8]

                self.result['ogn_aircraft_type_id'] = int(
                    ognAircraftTypeIdBinary, 2)
                if (self.result['ogn_aircraft_type_id'] == 0 or self.result['ogn_aircraft_type_id'] > 15):
                    self.result['ogn_aircraft_type_id'] = None

                self.result['ogn_address_type_id'] = int(
                    ognAddressTypeIdBinary, 2)
                if (self.result['ogn_address_type_id'] == 0 or self.result['ogn_address_type_id'] > 4):
                    self.result['ogn_address_type_id'] = None

            except ValueError:
                # Assume that we should track this aircraft (we should not receive packets that has the noTracking or stealth flag set)
                noTracking = '0'
                stealth = '0'

            if (stealth == '1' or noTracking == '1'):
                self.isAllowedToIdentify = False
                self.isAllowedToTrack = False

    def _parseClimbRate(self, content):
        """Parse OGN climb rate

        Arguments:
            content (string) :  String that contains information to parse
        """
        if ('ogn_climb_rate' not in self.result and content.endswith('fpm')):
            content = content.replace("fpm", "")
            try:
                self.result['ogn_climb_rate'] = int(content)
            except ValueError:
                pass

    def _parseTurnRate(self, content):
        """Parse OGN turn rate

        Arguments:
            content (string) :  String that contains information to parse
        """
        if ('ogn_turn_rate' not in self.result and content.endswith('rot')):
            content = content.replace("rot", "")
            try:
                self.result['ogn_turn_rate'] = float(content)
            except ValueError:
                pass

    def _parseSignalToNoiseRatio(self, content):
        """Parse OGN SNR

        Arguments:
            content (string) :  String that contains information to parse
        """
        if ('ogn_signal_to_noise_ratio' not in self.result and content.endswith('dB')):
            content = content.replace("dB", "")
            try:
                self.result['ogn_signal_to_noise_ratio'] = float(content)
            except ValueError:
                pass

    def _parseBitErrorsCorrected(self, content):
        """Parse OGN number of bit errors corrected in the packet upon reception

        Arguments:
            content (string) :  String that contains information to parse
        """
        if ('ogn_bit_errors_corrected' not in self.result and content.endswith('e')):
            content = content.replace("e", "")
            try:
                self.result['ogn_bit_errors_corrected'] = int(content)
            except ValueError:
                pass

    def _parseFrequencyOffset(self, content):
        """Parse OGN frequency offset measured upon reception

        Arguments:
            content (string) :  String that contains information to parse
        """
        if ('ogn_frequency_offset' not in self.result and content.endswith('kHz')):
            content = content.replace("kHz", "")
            try:
                self.result['ogn_frequency_offset'] = float(content)
            except ValueError:
                pass
