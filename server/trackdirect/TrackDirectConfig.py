import sys
import os
import os.path
import ConfigParser
from ConfigParser import SafeConfigParser

from trackdirect.common.Singleton import Singleton


class TrackDirectConfig(Singleton):
    """Track Direct Config class
    """

    def __init__(self):
        """The __init__ method.
        """
        self.collector = {}

    def populate(self, configFile):
        """The __init__ method.

        Args:
            configFile (string):  Config file name
        """
        configParser = SafeConfigParser()
        if (configFile.startswith('/')):
            configParser.read(os.path.expanduser(configFile))
        else:
            configParser.read(os.path.expanduser(
                '~/trackdirect/config/' + configFile))

        # Database
        self.dbHostname = configParser.get('database', 'host').strip('"')
        self.dbName = configParser.get('database', 'database').strip('"')
        try:
            self.dbUsername = configParser.get(
                'database', 'username').strip('"')
        except (ConfigParser.NoSectionError, ConfigParser.NoOptionError):
            self.dbUsername = os.getlogin()
        self.dbPassword = configParser.get('database', 'password').strip('"')
        self.dbPort = int(configParser.get('database', 'port').strip('"'))
        self.daysToSavePositionData = int(configParser.get(
            'database', 'days_to_save_position_data').strip('"'))
        self.daysToSaveStationData = int(configParser.get(
            'database', 'days_to_save_station_data').strip('"'))
        self.daysToSaveWeatherData = int(configParser.get(
            'database', 'days_to_save_weather_data').strip('"'))
        self.daysToSaveTelemetryData = int(configParser.get(
            'database', 'days_to_save_telemetry_data').strip('"'))

        # Websocket server
        self.websocketHostname = configParser.get(
            'websocket_server', 'host').strip('"')
        self.websocketPort = int(configParser.get(
            'websocket_server', 'port').strip('"'))
        self.errorLog = configParser.get(
            'websocket_server', 'error_log').strip('"')
        self.websocketFrequencyLimit = configParser.get(
            'websocket_server', 'frequency_limit').strip('"')

        self.maxDefaultTime = configParser.get(
            'websocket_server', 'max_default_time').strip('"')
        self.maxFilterTime = configParser.get(
            'websocket_server', 'max_filter_time').strip('"')
        self.maxClientIdleTime = configParser.get(
            'websocket_server', 'max_client_idle_time').strip('"')
        self.maxQueuedRealtimePackets = configParser.get(
            'websocket_server', 'max_queued_realtime_packets').strip('"')

        allowTimeTravel = configParser.get(
            'websocket_server', 'allow_time_travel').strip('"')
        self.allowTimeTravel = True
        if (allowTimeTravel == "0"):
            self.allowTimeTravel = False

        # Websocket server APRS-IS connection
        try:
            self.websocketAprsHost1 = configParser.get(
                'websocket_server', 'aprs_host1').strip('"')
            self.websocketAprsPort1 = configParser.get(
                'websocket_server', 'aprs_port1').strip('"')
            self.websocketAprsSourceId1 = int(configParser.get(
                'websocket_server', 'aprs_source_id1').strip('"'))
        except (ConfigParser.NoSectionError, ConfigParser.NoOptionError):
            self.websocketAprsSourceId1 = None
            self.websocketAprsHost1 = None
            self.websocketAprsPort1 = None

        try:
            self.websocketAprsHost2 = configParser.get(
                'websocket_server', 'aprs_host2').strip('"')
            self.websocketAprsPort2 = configParser.get(
                'websocket_server', 'aprs_port2').strip('"')
            self.websocketAprsSourceId2 = int(configParser.get(
                'websocket_server', 'aprs_source_id2').strip('"'))
        except (ConfigParser.NoSectionError, ConfigParser.NoOptionError):
            self.websocketAprsSourceId2 = None
            self.websocketAprsHost2 = None
            self.websocketAprsPort2 = None

        # Collectors
        for collectorNumber in range(0, 5):
            self.collector[collectorNumber] = {}
            try:
                self.collector[collectorNumber]['source_id'] = int(configParser.get(
                    'collector' + str(collectorNumber), 'source_id').strip('"'))
                self.collector[collectorNumber]['host'] = configParser.get(
                    'collector' + str(collectorNumber), 'host').strip('"')
                self.collector[collectorNumber]['port_full'] = int(configParser.get(
                    'collector' + str(collectorNumber), 'port_full').strip('"'))
                self.collector[collectorNumber]['port_filtered'] = int(configParser.get(
                    'collector' + str(collectorNumber), 'port_filtered').strip('"'))

                self.collector[collectorNumber]['callsign'] = configParser.get(
                    'collector' + str(collectorNumber), 'callsign').strip('"')
                self.collector[collectorNumber]['passcode'] = configParser.get(
                    'collector' + str(collectorNumber), 'passcode').strip('"')

                self.collector[collectorNumber]['numbers_in_batch'] = configParser.get(
                    'collector' + str(collectorNumber), 'numbers_in_batch').strip('"')
                self.collector[collectorNumber]['frequency_limit'] = configParser.get(
                    'collector' + str(collectorNumber), 'frequency_limit').strip('"')

                saveFastPackets = configParser.get(
                    'collector' + str(collectorNumber), 'save_fast_packets').strip('"')
                self.collector[collectorNumber]['save_fast_packets'] = bool(
                    int(saveFastPackets))

                self.collector[collectorNumber]['error_log'] = configParser.get(
                    'collector' + str(collectorNumber), 'error_log').strip('"')

            except (ConfigParser.NoSectionError, ConfigParser.NoOptionError):
                self.collector[collectorNumber]['source_id'] = None
                self.collector[collectorNumber]['host'] = None
                self.collector[collectorNumber]['port_full'] = None
                self.collector[collectorNumber]['port_filtered'] = None

                self.collector[collectorNumber]['callsign'] = None
                self.collector[collectorNumber]['passcode'] = None

                self.collector[collectorNumber]['numbers_in_batch'] = "20"
                self.collector[collectorNumber]['frequency_limit'] = "0"
                self.collector[collectorNumber]['save_fast_packets'] = True

                self.collector[collectorNumber]['error_log'] = None
