import os
import os.path
from configparser import ConfigParser
from configparser import NoSectionError
from configparser import NoOptionError
from common.Singleton import Singleton


class TrackDirectConfig(Singleton):
    """Track Direct Config class
    """

    def populate(self, config_file = ""):
        """Populate the configuration from a file.

        Args:
            config_file (string): Config file name
        """
        config_parser = ConfigParser()
        if config_file.startswith('/'):
            config_parser.read(os.path.expanduser(config_file))
        else:
            config_parser.read(os.path.expanduser(
                '~/trackdirect/config/' + config_file))

        # Database
        self.db_hostname = config_parser.get('database', 'host').strip('"')
        self.db_name = config_parser.get('database', 'database').strip('"')
        try:
            self.db_username = config_parser.get('database', 'username').strip('"')
        except (NoSectionError, NoOptionError):
            self.db_username = 'root'
        self.db_password = config_parser.get('database', 'password').strip('"')
        self.db_port = int(config_parser.get('database', 'port').strip('"'))
        self.days_to_save_position_data = int(config_parser.get(
            'database', 'days_to_save_position_data').strip('"'))
        self.days_to_save_station_data = int(config_parser.get(
            'database', 'days_to_save_station_data').strip('"'))
        self.days_to_save_weather_data = int(config_parser.get(
            'database', 'days_to_save_weather_data').strip('"'))
        self.days_to_save_telemetry_data = int(config_parser.get(
            'database', 'days_to_save_telemetry_data').strip('"'))

        self.save_ogn_stations_with_missing_identity = False
        try:
            save_ogn_stations_with_missing_identity = config_parser.get(
                'database', 'save_ogn_stations_with_missing_identity').strip('"')
            if save_ogn_stations_with_missing_identity == "1":
                self.save_ogn_stations_with_missing_identity = True
        except (NoSectionError, NoOptionError):
            pass

        # Websocket server
        self.websocket_hostname = config_parser.get(
            'websocket_server', 'host').strip('"')
        self.websocket_port = int(config_parser.get(
            'websocket_server', 'port').strip('"'))

        self.websocket_external_port = self.websocket_port
        try:
            self.websocket_external_port = int(config_parser.get(
                'websocket_server', 'external_port').strip('"'))
        except (NoSectionError, NoOptionError):
            pass

        self.error_log = config_parser.get(
            'websocket_server', 'error_log').strip('"')
        self.websocket_frequency_limit = config_parser.get(
            'websocket_server', 'frequency_limit').strip('"')

        self.max_default_time = int(config_parser.get(
            'websocket_server', 'max_default_time').strip('"'))
        self.max_filter_time = int(config_parser.get(
            'websocket_server', 'max_filter_time').strip('"'))
        self.max_client_idle_time = int(config_parser.get(
            'websocket_server', 'max_client_idle_time').strip('"'))
        self.max_queued_realtime_packets = int(config_parser.get(
            'websocket_server', 'max_queued_realtime_packets').strip('"'))

        allow_time_travel = config_parser.get(
            'websocket_server', 'allow_time_travel').strip('"')
        self.allow_time_travel = False
        if allow_time_travel == "1":
            self.allow_time_travel = True

        # Websocket server APRS connection (we support 2 different sources, more can be added...)
        try:
            self.websocket_aprs_host1 = config_parser.get(
                'websocket_server', 'aprs_host1').strip('"')
            self.websocket_aprs_port1 = config_parser.get(
                'websocket_server', 'aprs_port1').strip('"')
            self.websocket_aprs_source_id1 = int(config_parser.get(
                'websocket_server', 'aprs_source_id1').strip('"'))
        except (NoSectionError, NoOptionError):
            self.websocket_aprs_source_id1 = None
            self.websocket_aprs_host1 = None
            self.websocket_aprs_port1 = None

        try:
            self.websocket_aprs_host2 = config_parser.get(
                'websocket_server', 'aprs_host2').strip('"')
            self.websocket_aprs_port2 = config_parser.get(
                'websocket_server', 'aprs_port2').strip('"')
            self.websocket_aprs_source_id2 = int(config_parser.get(
                'websocket_server', 'aprs_source_id2').strip('"'))
        except (NoSectionError, NoOptionError):
            self.websocket_aprs_source_id2 = None
            self.websocket_aprs_host2 = None
            self.websocket_aprs_port2 = None

        if self.websocket_aprs_source_id1 == 5 or self.websocket_aprs_source_id2 == 5:
            # At least one source is of type OGN, disable display of older data
            self.allow_time_travel = False
            if self.max_default_time > 1440:
                self.max_default_time = 1440
            if self.max_filter_time > 1440:
                self.max_filter_time = 1440

        # Collectors
        self.collector = {}
        for collector_number in range(0, 5):
            self.collector[collector_number] = {}
            try:
                self.collector[collector_number]['source_id'] = int(config_parser.get(
                    'collector' + str(collector_number), 'source_id').strip('"'))
                self.collector[collector_number]['host'] = config_parser.get(
                    'collector' + str(collector_number), 'host').strip('"')
                self.collector[collector_number]['port_full'] = int(config_parser.get(
                    'collector' + str(collector_number), 'port_full').strip('"'))
                self.collector[collector_number]['port_filtered'] = int(config_parser.get(
                    'collector' + str(collector_number), 'port_filtered').strip('"'))

                self.collector[collector_number]['callsign'] = config_parser.get(
                    'collector' + str(collector_number), 'callsign').strip('"')
                self.collector[collector_number]['passcode'] = config_parser.get(
                    'collector' + str(collector_number), 'passcode').strip('"')

                self.collector[collector_number]['numbers_in_batch'] = config_parser.get(
                    'collector' + str(collector_number), 'numbers_in_batch').strip('"')
                try:
                    self.collector[collector_number]['frequency_limit'] = int(config_parser.get(
                        'collector' + str(collector_number), 'frequency_limit').strip('"'))
                except (NoSectionError, NoOptionError):
                    self.collector[collector_number]['frequency_limit'] = 0

                try:
                    save_fast_packets = config_parser.get(
                        'collector' + str(collector_number), 'save_fast_packets').strip('"')
                    self.collector[collector_number]['save_fast_packets'] = bool(
                        int(save_fast_packets))
                except (NoSectionError, NoOptionError):
                    self.collector[collector_number]['save_fast_packets'] = False

                try:
                    detect_duplicates = config_parser.get(
                        'collector' + str(collector_number), 'detect_duplicates').strip('"')
                    self.collector[collector_number]['detect_duplicates'] = bool(
                        int(detect_duplicates))
                except (NoSectionError, NoOptionError):
                    self.collector[collector_number]['detect_duplicates'] = False

                self.collector[collector_number]['error_log'] = config_parser.get(
                    'collector' + str(collector_number), 'error_log').strip('"')

                if self.websocket_aprs_source_id1 == 5 or self.websocket_aprs_source_id2 == 5:
                    # source is of type OGN, make sure we do not save too many packets (will cause too high load on db)
                    if self.collector[collector_number]['frequency_limit'] < 10:
                        self.collector[collector_number]['frequency_limit'] = 10
                    self.collector[collector_number]['save_fast_packets'] = False

            except (NoSectionError, NoOptionError):
                self.collector[collector_number]['source_id'] = None
                self.collector[collector_number]['host'] = None
                self.collector[collector_number]['port_full'] = None
                self.collector[collector_number]['port_filtered'] = None

                self.collector[collector_number]['callsign'] = None
                self.collector[collector_number]['passcode'] = None

                self.collector[collector_number]['numbers_in_batch'] = "20"
                self.collector[collector_number]['frequency_limit'] = "0"
                self.collector[collector_number]['save_fast_packets'] = True
                self.collector[collector_number]['detect_duplicates'] = False

                self.collector[collector_number]['error_log'] = None
