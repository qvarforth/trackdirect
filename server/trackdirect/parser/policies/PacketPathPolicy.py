from server.trackdirect.exceptions.TrackDirectMissingStationError import TrackDirectMissingStationError
from server.trackdirect.parser.policies.PacketPathTcpPolicy import PacketPathTcpPolicy


class PacketPathPolicy:
    """PacketPathPolicy handles logic to generate the path for a specified packet."""

    def __init__(self, path, source_id, station_repository, sender_repository):
        """
        Args:
            path (list): Raw packet path list
            source_id (int): Packet source id
            station_repository (StationRepository): StationRepository instance
            sender_repository (SenderRepository): SenderRepository instance
        """
        self.path = path
        self.source_id = source_id
        self.station_repository = station_repository
        self.sender_repository = sender_repository

        self.station_id_path = []
        self.station_name_path = []
        self.station_location_path = []
        self._parse_path()

    def get_station_id_path(self):
        """Returns station id path."""
        return self.station_id_path

    def get_station_name_path(self):
        """Returns station name path."""
        return self.station_name_path

    def get_station_location_path(self):
        """Returns station location path, a list of longitude and latitude values."""
        return self.station_location_path

    def _parse_path(self):
        """Parse Station path."""
        is_q_code_found = False
        is_non_used_path_command_found = False
        packet_path_tcp_policy = PacketPathTcpPolicy(self.path)
        if packet_path_tcp_policy.is_sent_by_tcp():
            return

        for name in self.path:
            if isinstance(name, int):
                name = str(name)

            if self._is_q_code(name):
                is_q_code_found = True
                continue

            if self._is_path_command(name):
                if not self._is_used_path_command(name):
                    is_non_used_path_command_found = True
                continue

            path_station_name = name.replace('*', '')
            if not self._is_station_name_valid(path_station_name):
                continue

            if is_q_code_found or '*' in name or not is_non_used_path_command_found:
                self._add_station_to_path(path_station_name)

    def _add_station_to_path(self, name):
        """Add station to path if valid."""
        try:
            station = self.station_repository.get_cached_object_by_name(name, self.source_id)
            station_id = station.id

            if station_id not in self.station_id_path:
                location = self._get_station_latest_location(station_id)
                if location is not None:
                    self.station_name_path.append(name)
                    self.station_id_path.append(station_id)
                    self.station_location_path.append(location)
        except TrackDirectMissingStationError:
            pass

    def _is_q_code(self, value):
        """Returns true if specified string is a Q code."""
        return value.upper().startswith('QA') and len(value) == 3

    def _is_station_name_valid(self, name):
        """Returns true if specified station name is valid."""
        invalid_names = {
            'NONE', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'APRS', '1-1', '2-1', '2-2', '3-1', '3-2', '3-3',
            '4-1', '4-2', '4-3', '4-4', 'DSTAR', 'TCP', 'NULL', 'LOCAL', 'GATE', 'DIRECT', 'CWOP', 'DMR', 'ECHO', 'OR1-', 'OR2-'
        }
        return not any(name.startswith(invalid) for invalid in invalid_names)

    def _is_path_command(self, value):
        """Returns true if specified value is a path command."""
        return any(value.startswith(cmd) for cmd in ['WIDE', 'RELAY', 'TRACE', 'RPN'])

    def _is_used_path_command(self, value):
        """Returns true if specified value is a path command and it is completely used."""
        if '*' in value:
            return True
        if any(value.startswith(cmd) for cmd in ['WIDE', 'TRACE', 'RPN']):
            return '-' not in value
        return False

    def _get_station_latest_location(self, station_id):
        """Get latest location for a specified station."""
        station = self.station_repository.get_object_by_id(station_id)
        if station.is_existing_object():
            if station.latest_confirmed_latitude is not None and station.latest_confirmed_longitude is not None:
                return [station.latest_confirmed_latitude, station.latest_confirmed_longitude]
        return None