import os
import os.path
import configparser

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
        configParser = configparser.SafeConfigParser()
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
        except (configparser.NoSectionError, configparser.NoOptionError):
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

        self.saveOgnStationsWithMissingIdentity = False
        try:
            saveOgnStationsWithMissingIdentity = configParser.get(
                'database', 'save_ogn_stations_with_missing_identity').strip('"')
            if (saveOgnStationsWithMissingIdentity == "1"):
                self.saveOgnStationsWithMissingIdentity = True
        except (configparser.NoSectionError, configparser.NoOptionError):
            pass

        # Websocket server
        self.websocketHostname = configParser.get(
            'websocket_server', 'host').strip('"')
        self.websocketPort = int(configParser.get(
            'websocket_server', 'port').strip('"'))

        self.websocketExternalPort = self.websocketPort
        try :
            self.websocketExternalPort = int(configParser.get(
                'websocket_server', 'external_port').strip('"'))
        except (configparser.NoSectionError, configparser.NoOptionError):
            pass

        self.errorLog = configParser.get(
            'websocket_server', 'error_log').strip('"')
        self.websocketFrequencyLimit = configParser.get(
            'websocket_server', 'frequency_limit').strip('"')

        self.maxDefaultTime = int(configParser.get(
            'websocket_server', 'max_default_time').strip('"'))
        self.maxFilterTime = int(configParser.get(
            'websocket_server', 'max_filter_time').strip('"'))
        self.maxClientIdleTime = int(configParser.get(
            'websocket_server', 'max_client_idle_time').strip('"'))
        self.maxQueuedRealtimePackets = int(configParser.get(
            'websocket_server', 'max_queued_realtime_packets').strip('"'))

        allowTimeTravel = configParser.get(
            'websocket_server', 'allow_time_travel').strip('"')
        self.allowTimeTravel = False
        if (allowTimeTravel == "1"):
            self.allowTimeTravel = True

        # Websocket server APRS connection (we support 2 different sources, more can be added...)
        try:
            self.websocketAprsHost1 = configParser.get(
                'websocket_server', 'aprs_host1').strip('"')
            self.websocketAprsPort1 = configParser.get(
                'websocket_server', 'aprs_port1').strip('"')
            self.websocketAprsSourceId1 = int(configParser.get(
                'websocket_server', 'aprs_source_id1').strip('"'))
        except (configparser.NoSectionError, configparser.NoOptionError):
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
        except (configparser.NoSectionError, configparser.NoOptionError):
            self.websocketAprsSourceId2 = None
            self.websocketAprsHost2 = None
            self.websocketAprsPort2 = None

        if (self.websocketAprsSourceId1 == 5 or self.websocketAprsSourceId2 == 5) :
            # At least one source is of type OGN, disable display of older data
            self.allowTimeTravel = False
            if (self.maxDefaultTime > 1440) :
                self.maxDefaultTime = 1440
            if (self.maxFilterTime > 1440) :
                self.maxDefaultTime = 1440

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
                try:
                    self.collector[collectorNumber]['frequency_limit'] = int(configParser.get(
                        'collector' + str(collectorNumber), 'frequency_limit').strip('"'))
                except (configparser.NoSectionError, configparser.NoOptionError):
                    self.collector[collectorNumber]['frequency_limit'] = 0

                try:
                    saveFastPackets = configParser.get(
                        'collector' + str(collectorNumber), 'save_fast_packets').strip('"')
                    self.collector[collectorNumber]['save_fast_packets'] = bool(
                        int(saveFastPackets))
                except (configparser.NoSectionError, configparser.NoOptionError):
                    self.collector[collectorNumber]['save_fast_packets'] = False

                try:
                    detectDuplicates = configParser.get(
                        'collector' + str(collectorNumber), 'detect_duplicates').strip('"')
                    self.collector[collectorNumber]['detect_duplicates'] = bool(
                        int(detectDuplicates))
                except (configparser.NoSectionError, configparser.NoOptionError):
                    self.collector[collectorNumber]['detect_duplicates'] = False

                self.collector[collectorNumber]['error_log'] = configParser.get(
                    'collector' + str(collectorNumber), 'error_log').strip('"')

                if (self.websocketAprsSourceId1 == 5 or self.websocketAprsSourceId2 == 5) :
                    # source is of type OGN, make sure we do not save to many packets (will cause to high load on db)
                    if (self.collector[collectorNumber]['frequency_limit'] < 10) :
                        self.collector[collectorNumber]['frequency_limit'] = 10
                    self.collector[collectorNumber]['save_fast_packets'] = False


            except (configparser.NoSectionError, configparser.NoOptionError):
                self.collector[collectorNumber]['source_id'] = None
                self.collector[collectorNumber]['host'] = None
                self.collector[collectorNumber]['port_full'] = None
                self.collector[collectorNumber]['port_filtered'] = None

                self.collector[collectorNumber]['callsign'] = None
                self.collector[collectorNumber]['passcode'] = None

                self.collector[collectorNumber]['numbers_in_batch'] = "20"
                self.collector[collectorNumber]['frequency_limit'] = "0"
                self.collector[collectorNumber]['save_fast_packets'] = True
                self.collector[collectorNumber]['detect_duplicates'] = False

                self.collector[collectorNumber]['error_log'] = None
