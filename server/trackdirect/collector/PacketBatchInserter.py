import logging
import psycopg2
import psycopg2.extras

from trackdirect.collector.StationLatestPacketModifier import StationLatestPacketModifier
from trackdirect.collector.PacketMapIdModifier import PacketMapIdModifier

from trackdirect.database.PacketTableCreator import PacketTableCreator
from trackdirect.database.PacketPathTableCreator import PacketPathTableCreator
from trackdirect.database.PacketWeatherTableCreator import PacketWeatherTableCreator
from trackdirect.database.PacketTelemetryTableCreator import PacketTelemetryTableCreator
from trackdirect.database.PacketOgnTableCreator import PacketOgnTableCreator


class PacketBatchInserter():
    """PacketBatchInserter is used to add a list of packets to the database
    """

    def __init__(self, db, dbNoAutoCommit):
        """The __init__ method.

        Args:
            db (psycopg2.Connection):              Database connection (with autocommit)
            dbNoAutoCommit (psycopg2.Connection):  Database connection (without autocommit)
        """
        self.db = db
        self.dbNoAutoCommit = dbNoAutoCommit
        self.logger = logging.getLogger(__name__)

        self.packetIdList = []
        self.weatherPacketIdList = []
        self.ognPacketIdList = []
        self.telemetryPacketIdList = []
        self.pathPacketIdList = []
        self.positionPacketIdList = []
        self.confirmedPositionPacketIdList = []

    def insert(self, packets, sourceId):
        """Insert this packets into database

        Args:
            packets (array):  Packets to insert
            sourceId (int):   Id that corresponds to id in source-table
        """
        cur = self.dbNoAutoCommit.cursor()
        try:
            # Make sure needed tables exists before starting the main database transaction
            self._makeSureTablesExists(packets)

            # insert telemetry data
            self._insertTelemetryDefinitions(packets)

            # Update mapId on previous packets
            packetTableCreator = PacketTableCreator(self.db)
            packetMapIdModifier = PacketMapIdModifier(cur, packetTableCreator)
            packetMapIdModifier.execute(packets)

            # insert into packet (and packet_path ...)
            self._insertIntoPacketTables(packets, cur)

            self.dbNoAutoCommit.commit()
            cur.close()
        except psycopg2.InterfaceError as e:
            # Connection to database is lost, better just exit
            self.dbNoAutoCommit.rollback()
            cur.close()
            raise e
        except Exception as e:
            # Something went wrong
            self.logger.error(e, exc_info=1)
            self.dbNoAutoCommit.rollback()
            cur.close()
            return
        self._performPostInsertActions(packets)

    def _makeSureTablesExists(self, packets):
        """Make sures all tables needed to insert specified packets exists

        Args:
            packets (array):  Packets to insert
        """
        timestamp = packets[0].timestamp  # All packets is known to be on the same date

        packetTableCreator = PacketTableCreator(self.db)
        packetTable = packetTableCreator.getPacketTable(timestamp)

        packetPathTableCreator = PacketPathTableCreator(self.db)
        packetPathTable = packetPathTableCreator.getPacketPathTable(timestamp)

        packetWeatherTableCreator = PacketWeatherTableCreator(self.db)
        packetWeatherTable = packetWeatherTableCreator.getPacketWeatherTable(
            timestamp)

        packetTelemetryTableCreator = PacketTelemetryTableCreator(self.db)
        packetTelemetryTable = packetTelemetryTableCreator.getPacketTelemetryTable(
            timestamp)

        packetOgnTableCreator = PacketOgnTableCreator(self.db)
        packetOgnTable = packetOgnTableCreator.getPacketOgnTable(timestamp)

    def _performPostInsertActions(self, packets):
        """Perform post insert updates like updating station latest packet and related

        Args:
            packets (array):  Packets to insert
        """
        timestamp = packets[0].timestamp
        latestPacketModifier = StationLatestPacketModifier(self.db)
        latestPacketModifier.updateStationLatestPacket(
            self.packetIdList, timestamp)
        latestPacketModifier.updateStationLatestTelemetryPacket(
            self.telemetryPacketIdList, timestamp)
        latestPacketModifier.updateStationLatestWeatherPacket(
            self.weatherPacketIdList, timestamp)
        latestPacketModifier.updateStationLatestOgnPacket(
            self.ognPacketIdList, timestamp)
        latestPacketModifier.updateStationLatestLocationPacket(
            self.positionPacketIdList, timestamp)
        latestPacketModifier.updateStationLatestConfirmedPacket(
            self.confirmedPositionPacketIdList, timestamp)

    def _insertIntoPacketTables(self, packets, cur):
        """Insert packets into the correct packet tables

        Args:
            packets (array):   Packets to insert
            cur (cursor):      Database curser to use
        """
        self._insertIntoPacketTable(packets, cur)
        self._insertIntoPacketPathTable(packets, cur)
        self._insertIntoPacketWeatherTable(packets, cur)
        self._insertIntoPacketOgnTable(packets, cur)
        self._insertIntoPacketTelemetryTable(packets, cur)

    def _insertIntoPacketTable(self, packets, cur):
        """Insert packets into the correct packet table

        Args:
            packets (array):   Packets to insert
            cur (cursor):      Database curser to use
        """
        timestamp = packets[0].timestamp
        packetTableCreator = PacketTableCreator(self.db)
        packetTable = packetTableCreator.getPacketTable(timestamp)

        datePacketTuples = []
        for packet in packets:

            datePacketTuples.append((packet.stationId,
                                     packet.senderId,
                                     packet.mapId,
                                     packet.sourceId,
                                     packet.packetTypeId,
                                     packet.latitude,
                                     packet.longitude,
                                     packet.posambiguity,
                                     packet.symbol,
                                     packet.symbolTable,
                                     packet.mapSector,
                                     packet.relatedMapSectors,
                                     packet.markerId,
                                     packet.markerCounter,
                                     packet.speed,
                                     packet.course,
                                     packet.altitude,
                                     packet.rng,
                                     packet.phg,
                                     packet.latestPhgTimestamp,
                                     packet.latestRngTimestamp,
                                     packet.timestamp,
                                     packet.packetTailTimestamp,
                                     packet.isMoving,
                                     packet.reportedTimestamp,
                                     packet.positionTimestamp,
                                     packet.comment,
                                     packet.rawPath,
                                     packet.raw))

        try:
            # insert into packetYYYYMMDD
            argString = b','.join(cur.mogrify(
                "(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", x) for x in datePacketTuples)
            sql = "insert into " + packetTable + "(station_id, sender_id, map_id, source_id, packet_type_id, latitude, longitude, posambiguity, symbol, symbol_table, map_sector, related_map_sectors, marker_id, marker_counter, speed, course, altitude, rng, phg, latest_phg_timestamp, latest_rng_timestamp, timestamp, packet_tail_timestamp, is_moving, reported_timestamp, position_timestamp, comment, raw_path, raw) values " + argString.decode() + " RETURNING id"
            cur.execute(sql)
        except psycopg2.InterfaceError as e:
            # Connection to database is lost, better just exit
            raise e
        except Exception as e:
            # Something went wrong, log error so we can fix problem
            self.logger.error(e, exc_info=1)
            self.logger.error(sql)
            return

        i = 0
        for record in cur:
            if packets[i]:
                packets[i].id = record["id"]

                if packets[i].mapId in [1]:
                    self.confirmedPositionPacketIdList.append(record["id"])
                elif packets[i].mapId in [1, 5, 7, 9]:
                    self.positionPacketIdList.append(record["id"])
                else:
                    # We only need to add the packet to the packetIdList if not in the positionPacketIdList or confirmedPositionPacketIdList array's
                    self.packetIdList.append(record["id"])
            i += 1

    def _insertIntoPacketPathTable(self, packets, cur):
        """Insert packets into the correct packet path table

        Args:
            packets (array):   Packets to insert
            cur (cursor):      Database curser to use
        """
        timestamp = packets[0].timestamp
        packetPathTableCreator = PacketPathTableCreator(self.db)
        packetPathTable = packetPathTableCreator.getPacketPathTable(timestamp)

        i = 0
        pathTuples = []
        for packet in packets:
            if (packet.stationIdPath):
                self.pathPacketIdList.append(packet.id)
                number = 0
                for stationId in packet.stationIdPath:
                    if (packet.stationLocationPath
                            and packet.stationLocationPath[number]):
                        latitude = packet.stationLocationPath[number][0]
                        longitude = packet.stationLocationPath[number][1]
                        distance = packet.getTransmitDistance()

                        pathTuples.append(
                            (packet.id, stationId, latitude, longitude, packet.timestamp, distance, number, packet.stationId, packet.latitude, packet.longitude))
                        number += 1
            i += 1

        # insert into packetYYYYMMDD_path
        if pathTuples:
            try:
                argString = b','.join(cur.mogrify(
                    "(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", x) for x in pathTuples)
                cur.execute("insert into " + packetPathTable +
                            "(packet_id, station_id, latitude, longitude, timestamp, distance, number, sending_station_id, sending_latitude, sending_longitude) values " + argString.decode())
            except psycopg2.InterfaceError as e:
                # Connection to database is lost, better just exit
                raise e
            except Exception as e:
                # Something went wrong, log error so we can fix problem
                self.logger.error(e, exc_info=1)
                self.logger.error(argString)

    def _insertIntoPacketWeatherTable(self, packets, cur):
        """Insert packets into the correct packet weather table

        Args:
            packets (array):   Packets to insert
            cur (cursor):      Database curser to use
        """
        timestamp = packets[0].timestamp
        packetWeatherTableCreator = PacketWeatherTableCreator(self.db)
        packetWeatherTable = packetWeatherTableCreator.getPacketWeatherTable(
            timestamp)

        i = 0
        weatherTuples = []
        for packet in packets:
            if (packet.weather):
                self.weatherPacketIdList.append(packet.id)
                weatherTuples.append((packet.id,
                                      packet.stationId,
                                      packet.timestamp,
                                      packet.weather.humidity,
                                      packet.weather.pressure,
                                      packet.weather.rain1h,
                                      packet.weather.rain24h,
                                      packet.weather.rainSinceMidnight,
                                      packet.weather.temperature,
                                      packet.weather.windDirection,
                                      packet.weather.windGust,
                                      packet.weather.windSpeed,
                                      packet.weather.luminosity,
                                      packet.weather.snow,
                                      packet.weather.wxRawTimestamp))
            i += 1

        # insert into packetYYYYMMDD_weather
        if weatherTuples:
            try:
                argString = b','.join(cur.mogrify(
                    "(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", x) for x in weatherTuples)
                cur.execute("insert into " + packetWeatherTable +
                            "(packet_id, station_id, timestamp, humidity, pressure, rain_1h, rain_24h, rain_since_midnight, temperature, wind_direction, wind_gust, wind_speed, luminosity, snow, wx_raw_timestamp) values " + argString.decode())
            except psycopg2.InterfaceError as e:
                # Connection to database is lost, better just exit
                raise e
            except Exception as e:
                # Something went wrong, log error so we can fix problem
                self.logger.error(e, exc_info=1)
                self.logger.error(argString)

    def _insertIntoPacketOgnTable(self, packets, cur):
        """Insert packets into the correct packet OGN table

        Args:
            packets (array):   Packets to insert
            cur (cursor):      Database curser to use
        """
        timestamp = packets[0].timestamp
        packetOgnTableCreator = PacketOgnTableCreator(self.db)
        packetOgnTable = packetOgnTableCreator.getPacketOgnTable(timestamp)

        i = 0
        ognTuples = []
        for packet in packets:
            if (packet.ogn):
                self.ognPacketIdList.append(packet.id)
                ognTuples.append((packet.id,
                                  packet.stationId,
                                  packet.timestamp,
                                  packet.ogn.ognSenderAddress,
                                  packet.ogn.ognAddressTypeId,
                                  packet.ogn.ognAircraftTypeId,
                                  packet.ogn.ognClimbRate,
                                  packet.ogn.ognTurnRate,
                                  packet.ogn.ognSignalToNoiseRatio,
                                  packet.ogn.ognBitErrorsCorrected,
                                  packet.ogn.ognFrequencyOffset))

            i += 1
        # insert into packetYYYYMMDD_ogn
        if ognTuples:
            try:
                argString = b','.join(cur.mogrify(
                    "(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", x) for x in ognTuples)
                cur.execute("insert into " + packetOgnTable + "(packet_id, station_id, timestamp, ogn_sender_address, ogn_address_type_id, ogn_aircraft_type_id, ogn_climb_rate, ogn_turn_rate, ogn_signal_to_noise_ratio, ogn_bit_errors_corrected, ogn_frequency_offset) values " + argString.decode())
            except psycopg2.InterfaceError as e:
                # Connection to database is lost, better just exit
                raise e
            except Exception as e:
                # Something went wrong, log error so we can fix problem
                self.logger.error(e, exc_info=1)
                self.logger.error(argString)

    def _insertIntoPacketTelemetryTable(self, packets, cur):
        """Insert packets into the correct packet telemetry table

        Args:
            packets (array):   Packets to insert
            cur (cursor):      Database curser to use
        """
        timestamp = packets[0].timestamp
        packetTelemetryTableCreator = PacketTelemetryTableCreator(self.db)
        packetTelemetryTable = packetTelemetryTableCreator.getPacketTelemetryTable(
            timestamp)

        i = 0
        telemetryTuples = []
        for packet in packets:
            if (packet.telemetry):
                self.telemetryPacketIdList.append(packet.id)
                if (not packet.telemetry.isDuplicate()):
                    telemetryTuples.append((packet.id,
                                            packet.stationId,
                                            packet.timestamp,
                                            packet.telemetry.val1,
                                            packet.telemetry.val2,
                                            packet.telemetry.val3,
                                            packet.telemetry.val4,
                                            packet.telemetry.val5,
                                            packet.telemetry.bits,
                                            packet.telemetry.seq))
            i += 1

        # insert into packetYYYYMMDD_telemetry
        if telemetryTuples:
            try:
                argString = b','.join(cur.mogrify(
                    "(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", x) for x in telemetryTuples)
                cur.execute("insert into " + packetTelemetryTable +
                            "(packet_id, station_id, timestamp, val1, val2, val3, val4, val5, bits, seq) values " + argString.decode() + " returning id")
            except psycopg2.InterfaceError as e:
                # Connection to database is lost, better just exit
                raise e
            except Exception as e:
                # Something went wrong, log error so we can fix problem
                self.logger.error(e, exc_info=1)

            packetTelemetryIds = []
            record = cur.fetchone()
            while record:
                packetTelemetryIds.append(record['id'])
                record = cur.fetchone()

            try:
                cur.execute("""update """ + packetTelemetryTable + """ packet_telemetry set
                        station_telemetry_param_id = (select id from station_telemetry_param where station_id = packet_telemetry.station_id and valid_to_ts is null),
                        station_telemetry_unit_id = (select id from station_telemetry_unit where station_id = packet_telemetry.station_id and valid_to_ts is null),
                        station_telemetry_eqns_id = (select id from station_telemetry_eqns where station_id = packet_telemetry.station_id and valid_to_ts is null),
                        station_telemetry_bits_id = (select id from station_telemetry_bits where station_id = packet_telemetry.station_id and valid_to_ts is null)
                    where id in %s""", (tuple(packetTelemetryIds), ))
            except psycopg2.InterfaceError as e:
                # Connection to database is lost, better just exit
                raise e
            except Exception as e:
                # Something went wrong, log error so we can fix problem
                self.logger.error(e, exc_info=1)

    def _insertTelemetryDefinitions(self, packets):
        """Insert telemetry definitions (PARAM, UNIT, EQNS, BITS) if any exists in current packets

        Args:
            packets (array):  Packets to insert
        """
        for packet in packets:
            if (packet.stationTelemetryBits):
                packet.stationTelemetryBits.save()

            if (packet.stationTelemetryEqns):
                packet.stationTelemetryEqns.save()

            if (packet.stationTelemetryParam):
                packet.stationTelemetryParam.save()

            if (packet.stationTelemetryUnit):
                packet.stationTelemetryUnit.save()
