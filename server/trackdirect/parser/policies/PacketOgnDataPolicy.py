import logging
from server.trackdirect.parser.policies.AprsPacketSymbolPolicy import AprsPacketSymbolPolicy
from server.trackdirect.parser.policies.PacketPathTcpPolicy import PacketPathTcpPolicy


class PacketOgnDataPolicy:
    """PacketOgnDataPolicy can answer questions about OGN data in the packet."""

    def __init__(self, data, ogn_device_repository, source_id):
        """
        The __init__ method.

        Args:
            data (dict): Raw packet data
            ogn_device_repository (OgnDeviceRepository): OgnDeviceRepository instance
            source_id (int): Source Id
        """
        self.data = data
        self.ogn_device_repository = ogn_device_repository
        self.logger = logging.getLogger('trackdirect')

        self.is_ogn_position_packet = self.is_ogn_position_packet(source_id)
        self.is_allowed_to_track = True
        self.is_allowed_to_identify = True

        self.result = {}
        self._parse()

    def get_ogn_data(self):
        """
        Returns raw OGN data.

        Returns:
            dict: OGN data
        """
        return self.result

    def is_ogn_position_packet(self, source_id):
        """
        Returns true if packet is an OGN Position packet.

        Args:
            source_id (int): Source Id

        Returns:
            bool: True if OGN Position packet, otherwise False
        """
        if source_id == 5:
            if self._is_valid_comment() and self.data["comment"].strip().startswith("id"):
                return True

            symbol = self.data.get('symbol')
            symbol_table = self.data.get('symbol_table')
            aprs_packet_symbol_policy = AprsPacketSymbolPolicy()
            if aprs_packet_symbol_policy.is_maybe_moving_symbol(symbol, symbol_table):
                return True
        else:
            if (self._is_valid_comment() and self.data["comment"].strip().startswith("id")
                    and all(keyword in self.data["comment"] + " " for keyword in ["fpm ", "rot ", "dB "])):
                return True
        return False

    def _is_valid_comment(self):
        """Check if the comment field is valid."""
        return "comment" in self.data and self.data["comment"] is not None and len(self.data["comment"].strip()) > 10

    def _parse(self):
        """Parse the OGN data in packet."""
        if not self.is_ogn_position_packet:
            self.result = None
            return

        packet_path_tcp_policy = PacketPathTcpPolicy(self.data['path'])
        if not packet_path_tcp_policy.is_sent_by_tcp():
            self.is_allowed_to_identify = False

        if "comment" in self.data and self.data["comment"] is not None:
            ogn_parts = self.data["comment"].split()
            for part in ogn_parts:
                if part.startswith('id'):
                    part = part.replace("-", "")
                    self._parse_sender_address(part)
                    self._parse_sender_details(part)
                elif part.endswith('fpm'):
                    self._parse_climb_rate(part)
                elif part.endswith('rot'):
                    self._parse_turn_rate(part)
                elif part.endswith('dB'):
                    if self.is_allowed_to_identify and self.is_allowed_to_track:
                        self._parse_signal_to_noise_ratio(part)
                elif part.endswith('e'):
                    if self.is_allowed_to_identify and self.is_allowed_to_track:
                        self._parse_bit_errors_corrected(part)
                elif part.endswith('kHz'):
                    if self.is_allowed_to_identify and self.is_allowed_to_track:
                        self._parse_frequency_offset(part)
                if not self.is_allowed_to_track:
                    return

        if not self.is_allowed_to_identify and 'ogn_sender_address' in self.result:
            self.result['ogn_sender_address'] = None

    def _parse_sender_address(self, content):
        """
        Parse the OGN sender address.

        Args:
            content (str): String that contains information to parse
        """
        if 'ogn_sender_address' not in self.result:
            self.is_allowed_to_identify = True
            self.result['ogn_sender_address'] = content[4:10].strip()

            ogn_device = self.ogn_device_repository.get_object_by_device_id(self.result['ogn_sender_address'])
            if ogn_device.device_id is not None and not ogn_device.tracked:
                self.is_allowed_to_identify = False
                self.is_allowed_to_track = False
            elif self.result['ogn_sender_address'] == 'ICAFFFFFF':
                self.is_allowed_to_identify = False
                self.is_allowed_to_track = False
            elif ogn_device.device_id is not None and not ogn_device.identified:
                self.is_allowed_to_identify = False
        else:
            self.is_allowed_to_identify = False

    def _parse_sender_details(self, content):
        """
        Parse OGN aircraft type and OGN address type.

        Args:
            content (str): String that contains information to parse
        """
        if 'ogn_aircraft_type_id' not in self.result:
            try:
                ogn_sender_details_hex = content[2:4]
                ogn_sender_details_binary = bin(int(ogn_sender_details_hex, 16))[2:].zfill(8)

                stealth = ogn_sender_details_binary[0]
                no_tracking = ogn_sender_details_binary[1]
                ogn_aircraft_type_id_binary = ogn_sender_details_binary[2:6]
                ogn_address_type_id_binary = ogn_sender_details_binary[6:8]

                self.result['ogn_aircraft_type_id'] = int(ogn_aircraft_type_id_binary, 2)
                if self.result['ogn_aircraft_type_id'] == 0 or self.result['ogn_aircraft_type_id'] > 15:
                    self.result['ogn_aircraft_type_id'] = None

                self.result['ogn_address_type_id'] = int(ogn_address_type_id_binary, 2)
                if self.result['ogn_address_type_id'] == 0 or self.result['ogn_address_type_id'] > 4:
                    self.result['ogn_address_type_id'] = None

            except ValueError:
                no_tracking = '0'
                stealth = '0'

            if stealth == '1' or no_tracking == '1':
                self.is_allowed_to_identify = False
                self.is_allowed_to_track = False

    def _parse_climb_rate(self, content):
        """
        Parse OGN climb rate.

        Args:
            content (str): String that contains information to parse
        """
        if 'ogn_climb_rate' not in self.result and content.endswith('fpm'):
            content = content.replace("fpm", "")
            try:
                self.result['ogn_climb_rate'] = int(content)
            except ValueError:
                pass

    def _parse_turn_rate(self, content):
        """
        Parse OGN turn rate.

        Args:
            content (str): String that contains information to parse
        """
        if 'ogn_turn_rate' not in self.result and content.endswith('rot'):
            content = content.replace("rot", "")
            try:
                self.result['ogn_turn_rate'] = float(content)
            except ValueError:
                pass

    def _parse_signal_to_noise_ratio(self, content):
        """
        Parse OGN SNR.

        Args:
            content (str): String that contains information to parse
        """
        if 'ogn_signal_to_noise_ratio' not in self.result and content.endswith('dB'):
            content = content.replace("dB", "")
            try:
                self.result['ogn_signal_to_noise_ratio'] = float(content)
            except ValueError:
                pass

    def _parse_bit_errors_corrected(self, content):
        """
        Parse OGN number of bit errors corrected in the packet upon reception.

        Args:
            content (str): String that contains information to parse
        """
        if 'ogn_bit_errors_corrected' not in self.result and content.endswith('e'):
            content = content.replace("e", "")
            try:
                self.result['ogn_bit_errors_corrected'] = int(content)
            except ValueError:
                pass

    def _parse_frequency_offset(self, content):
        """
        Parse OGN frequency offset measured upon reception.

        Args:
            content (str): String that contains information to parse
        """
        if 'ogn_frequency_offset' not in self.result and content.endswith('kHz'):
            content = content.replace("kHz", "")
            try:
                self.result['ogn_frequency_offset'] = float(content)
            except ValueError:
                pass