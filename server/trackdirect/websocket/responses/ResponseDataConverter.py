import logging
from twisted.python import log

from math import floor, ceil
import datetime, time

import psycopg2, psycopg2.extras

from trackdirect.repositories.PacketRepository import PacketRepository
from trackdirect.repositories.StationRepository import StationRepository
from trackdirect.repositories.PacketWeatherRepository import PacketWeatherRepository
from trackdirect.repositories.PacketOgnRepository import PacketOgnRepository
from trackdirect.repositories.OgnDeviceRepository import OgnDeviceRepository

from trackdirect.database.DatabaseObjectFinder import DatabaseObjectFinder
from trackdirect.database.DatabaseConnection import DatabaseConnection

from trackdirect.websocket.queries.MostRecentPacketsQuery import MostRecentPacketsQuery
from trackdirect.websocket.queries.MissingPacketsQuery import MissingPacketsQuery


class ResponseDataConverter():
    """An ResponseDataConverter instance is used to create response content data based on packet objects
    """


    def __init__(self, state, db):
        """The __init__ method.

        Args:
            state (WebsocketConnectionState):
            db (psycopg2.Connection):            Database connection (with autocommit)
        """
        self.state = state
        self.logger = logging.getLogger('trackdirect')

        self.db = db
        self.packetRepository = PacketRepository(db)
        self.stationRepository = StationRepository(db)
        self.packetWeatherRepository = PacketWeatherRepository(db)
        self.dbObjectFinder = DatabaseObjectFinder(db)
        self.packetOgnRepository = PacketOgnRepository(db)
        self.ognDeviceRepository = OgnDeviceRepository(db)


    def getResponseData(self, packets, mapSectorList = None, flags = [], iterationCounter = 0) :
        """Create response data based on specified packets

        Args:
            packets (array):                    An array of the Packet's that should be converted to packet dict responses
            mapSectorList (array):              An array of the current handled map sectors
            flags (array):                      An array with additional flags (like "realtime", "latest")
            iterationCounter (int)              This functionality will call itself to find related packets, this argument is used to remember the number of iterations

        Returns:
            An array of packet dicts
        """
        responseData = []
        for index, packet in enumerate(packets) :
            packetDict = packet.getDict(True)
            packetDict['packet_order_id'] = self._getPacketOrderId(packets, index, flags)

            self._updateState(packet, mapSectorList, flags)
            self._addOverwriteStatus(packetDict)
            if (("latest" not in flags and "realtime" not in flags) or self.state.isStationHistoryOnMap(packet.stationId)) :
                if (packetDict['packet_order_id'] == 1) :
                    self._addStationWeatherData(packetDict)
                    self._addStationTelemetryData(packetDict)
                    if (packet.sourceId == 5) :
                        self._addStationOgnData(packetDict)
                if (packet.sourceId == 5) :
                    self._addStationOgnDeviceData(packetDict)
                self._addPacketPhgRng(packetDict)

            if ("realtime" not in flags) :
                self._addStationIdPath(packetDict)

            self._setFlags(packetDict, flags)
            responseData.append(packetDict)
        return self._extendResponseWithMorePackets(responseData, flags, iterationCounter)


    def _getPacketOrderId(self, packets, index, flags) :
        """Returns the order id of the packet at specified index

        Args:
            packets (array):     An array of the Packet's that should be converted to packet dict responses
            index (int):         Index of the packet that we want an order id for
            flags (array):       An array with additional flags (like "realtime", "latest")

        Returns:
            int
        """
        if ("realtime" in flags) :
            return 1
        elif (len(packets) -1 == index):
            # This is the last packet of all
            return 1 # Last packet in response for this marker
        elif (packets[index].markerId != packets[index + 1].markerId) :
            # This is the last packet for this marker
            return 1 # Last packet in response for this marker
        elif (index == 0 or packets[index].markerId != packets[index - 1].markerId) :
            # This is the first packet for this marker
            return 3 # First packet in response for this marker
        else :
            return 2 # Middle packet in response for this marker


    def _updateState(self, packet, mapSectorList, flags) :
        """Update connection state based on packet on the way to client

        Args:
            packet (Packet):                     The packet that is on the way to client
            mapSectorList (array):               An array of the current handled map sectors
            flags (array):                       An array with additional flags (like "realtime", "latest")
        """
        self.state.setStationLatestTimestamp(packet.stationId, packet.timestamp)

        if (packet.stationId not in self.state.stationsOnMapDict) :
            # Station should be added to stationsOnMapDict even if only latest packet is added
            self.state.stationsOnMapDict[packet.stationId] = True

        # self.state.setCompleteStationLatestTimestamp
        # Note that we depend on that the real-time aprs-is sender make sure to send previous missing packets when a new is sent
        if (self.state.isStationHistoryOnMap(packet.stationId)) :
            self.state.setCompleteStationLatestTimestamp(packet.stationId, packet.timestamp)
        elif ("latest" not in flags and "realtime" not in flags and "related" not in flags) :
            self.state.setCompleteStationLatestTimestamp(packet.stationId, packet.timestamp)
        elif ("related" in flags and packet.packetTailTimestamp == packet.timestamp) :
            self.state.setCompleteStationLatestTimestamp(packet.stationId, packet.timestamp)

        if (mapSectorList and packet.mapSector is not None and packet.mapSector in mapSectorList) :
            if "latest" not in flags:
                self.state.setMapSectorLatestTimeStamp(packet.mapSector, packet.timestamp)
            else :
                self.state.setMapSectorLatestOverwriteTimeStamp(packet.mapSector, packet.timestamp)


    def _setFlags(self, packetDict, flags) :
        """Set additional flags that will tell client a bit more about the packet

        Args:
            packetDict (dict):   The packet to which we should modify
            flags (array):       An array with additional flags (like "realtime", "latest")
        """
        if ("realtime" in flags) :
            packetDict["db"] = 0
            packetDict["realtime"] = 1
        else :
            packetDict["db"] = 1
            packetDict["realtime"] = 0

    def _addOverwriteStatus(self, packetDict) :
        """Set packet overwrite status

        Args:
            packetDict (dict):                  The packet to which we should modify
        """
        packetDict['overwrite'] = 0

        # We assume that this method is called after the "complete station on map"-state has been updated
        if (not self.state.isStationHistoryOnMap(packetDict["station_id"])) :
            packetDict['overwrite'] = 1


    def _addPacketPhgRng(self, packetDict) :
        """Add previous reported phg and rng to the specified packet

        Args:
            packetDict (dict):  The packet to which we should modify
        """
        if ('phg' in packetDict and 'rng' in packetDict) :
            if (packetDict['phg'] is None and packetDict['latest_phg_timestamp'] is not None and packetDict['latest_phg_timestamp'] < packetDict['timestamp']) :
                relatedPacket = self.packetRepository.getObjectByStationIdAndTimestamp(packetDict['station_id'], packetDict['latest_phg_timestamp'])
                if (relatedPacket.phg is not None and relatedPacket.markerId == packetDict['marker_id']) :
                    packetDict['phg'] = relatedPacket.phg

            if (packetDict['rng'] is None and packetDict['latest_rng_timestamp'] is not None and packetDict['latest_rng_timestamp'] < packetDict['timestamp']) :
                relatedPacket = self.packetRepository.getObjectByStationIdAndTimestamp(packetDict['station_id'], packetDict['latest_rng_timestamp'])
                if (relatedPacket.rng is not None and relatedPacket.markerId == packetDict['marker_id']) :
                    packetDict['rng'] = relatedPacket.rng


    def _addStationOgnData(self, packetDict) :
        """Add OGN data to packet

        Args:
            packetDict (dict):  The packet to which we should add the related data
        """
        if ('ogn' not in packetDict or packetDict['ogn'] is None) :
            station = self.stationRepository.getObjectById(packetDict['station_id'])
            ts = int(packetDict['timestamp']) - (24*60*60)
            if (station.latestOgnPacketTimestamp is not None
                    and station.latestOgnPacketTimestamp > ts) :
                packetDict['latest_ogn_packet_timestamp'] = station.latestOgnPacketTimestamp

                relatedPacketDict = None
                if (station.latestOgnPacketId == packetDict['id']) :
                    relatedPacketDict = packetDict
                else :
                    relatedPacket = self.packetRepository.getObjectByIdAndTimestamp(station.latestOgnPacketId, station.latestOgnPacketTimestamp)
                    if (relatedPacket.isExistingObject()) :
                        relatedPacketDict = relatedPacket.getDict()

                if (relatedPacketDict is not None) :
                    if (relatedPacketDict['marker_id'] is not None and relatedPacketDict['marker_id'] == packetDict['marker_id']) :
                        packetOgn = self.packetOgnRepository.getObjectByPacketIdAndTimestamp(station.latestOgnPacketId, station.latestOgnPacketTimestamp)
                        if (packetOgn.isExistingObject()) :
                            packetDict['ogn'] = packetOgn.getDict()


    def _addStationOgnDeviceData(self, packetDict) :
        """Add OGN device data to packet

        Args:
            packetDict (dict):  The packet to which we should add the related data
        """
        station = self.stationRepository.getObjectById(packetDict['station_id'])
        if (station.latestOgnSenderAddress is not None) :
            ognDevice = self.ognDeviceRepository.getObjectByDeviceId(station.latestOgnSenderAddress)
            if (ognDevice.isExistingObject()) :
                packetDict['ogn_device'] = ognDevice.getDict()


    def _addStationWeatherData(self, packetDict) :
        """Add weather data to packet

        Args:
            packetDict (dict):  The packet to which we should add the related data
        """
        if ('weather' not in packetDict or packetDict['weather'] is None) :
            station = self.stationRepository.getObjectById(packetDict['station_id'])
            ts = int(packetDict['timestamp']) - (24*60*60)
            if (station.latestWeatherPacketTimestamp is not None
                    and station.latestWeatherPacketTimestamp > ts) :
                packetDict['latest_weather_packet_timestamp'] = station.latestWeatherPacketTimestamp

                relatedPacketDict = None
                if (station.latestWeatherPacketId == packetDict['id']) :
                    relatedPacketDict = packetDict
                else :
                    relatedPacket = self.packetRepository.getObjectByIdAndTimestamp(station.latestWeatherPacketId, station.latestWeatherPacketTimestamp)
                    if (relatedPacket.isExistingObject()) :
                        relatedPacketDict = relatedPacket.getDict()

                if (relatedPacketDict is not None) :
                    if (relatedPacketDict['marker_id'] is not None and relatedPacketDict['marker_id'] == packetDict['marker_id']) :
                        packetWeather = self.packetWeatherRepository.getObjectByPacketIdAndTimestamp(station.latestWeatherPacketId, station.latestWeatherPacketTimestamp)
                        if (packetWeather.isExistingObject()) :
                            packetDict['weather'] = packetWeather.getDict()


    def _addStationTelemetryData(self, packetDict) :
        """Add telemetry data to packet

        Args:
            packetDict (dict):  The packet to which we should add the related data
        """
        if ('telemetry' not in packetDict or packetDict['telemetry'] is None) :
            station = self.stationRepository.getObjectById(packetDict['station_id'])
            ts = int(packetDict['timestamp']) - (24*60*60)
            if (station.latestTelemetryPacketTimestamp is not None
                    and station.latestTelemetryPacketTimestamp > ts) :
                packetDict['latest_telemetry_packet_timestamp'] = station.latestTelemetryPacketTimestamp


    def _addStationIdPath(self, packetDict) :
        """Add the station id path to the specified packet

        Args:
            packetDict (dict):  The packet to which we should add the related station id path
        """
        stationIdPath = []
        stationNamePath = []
        stationLocationPath = []

        if (packetDict['raw_path'] is not None and "TCPIP*" not in packetDict['raw_path'] and "TCPXX*" not in packetDict['raw_path']) :
            packetDate = datetime.datetime.utcfromtimestamp(int(packetDict['timestamp'])).strftime('%Y%m%d')
            datePacketTable = 'packet' + packetDate
            datePacketPathTable = datePacketTable + '_path'

            if (self.dbObjectFinder.checkTableExists(datePacketPathTable)) :
                selectCursor = self.db.cursor()
                sql = """select station_id, station.name station_name, latitude, longitude from """ + datePacketPathTable + """, station where station.id = station_id and packet_id = %s order by number""" % (packetDict['id'])
                selectCursor.execute(sql)

                for record in selectCursor :
                    stationIdPath.append(record[0])
                    stationNamePath.append(record[1])
                    stationLocationPath.append([record[2], record[3]])
                selectCursor.close()
        packetDict['station_id_path'] = stationIdPath
        packetDict['station_name_path'] = stationNamePath
        packetDict['station_location_path'] = stationLocationPath


    def getDictListFromPacketList(self, packets) :
        """Returns a packet dict list from a packet list

        Args:
            packets (array):  Array of Packet instances

        Returns:
            A array och packet dicts
        """
        packetDicts = []
        for packet in packets :
            packetDicts.append(packet.getDict())
        return packetDicts


    def _extendResponseWithMorePackets(self, packetDicts, flags, iterationCounter) :
        """Extend the specified array with related packets

        Args:
            packetDicts (array):     An array of the packet response dicts
            flags (array):           An array with additional flags (like "realtime", "latest")
            iterationCounter (int):  This functionality will call itself to find related packets, this argument is used to remember the number of iterations

        Returns:
            The modified packet array
        """
        allPacketDicts = []
        hasSeveralSendersForOneStation = False

        # Add related packets (stations that the original packets depend on)
        if (packetDicts) :
            relatedStationIds = {}
            for index, packetDict in enumerate(packetDicts) :
                if (packetDict['is_moving'] == 1 or packetDict['packet_order_id'] == 1) :
                    # Only fetch related stations for the last stationary packet (in some cases query will return older packets)
                    if (packetDict['station_id_path']) :
                        # Also add latest packets from stations that has been involved in sending any packets in array "packets"
                        for stationId in packetDict['station_id_path'] :
                            if (stationId not in self.state.stationsOnMapDict) :
                                relatedStationIds[stationId] = True

            for index, packetDict in enumerate(packetDicts) :
                if (packetDict['station_id'] in relatedStationIds) :
                    del relatedStationIds[packetDict['station_id']]

            if (relatedStationIds) :
                relatedStationPackets = self._getRelatedStationPacketsByStationIds(list(relatedStationIds.keys()))

                # To avoid infinit loop we mark all related stations as added to map even we we failed doing it
                for relatedStationId in list(relatedStationIds.keys()):
                    if (relatedStationId not in self.state.stationsOnMapDict) :
                        self.state.stationsOnMapDict[relatedStationId] = True

                if (relatedStationPackets) :
                    if ("latest" in flags) :
                        relatedStationPacketDicts = self.getResponseData(relatedStationPackets, None, ["latest", "related"], iterationCounter + 1)
                    else :
                        relatedStationPacketDicts = self.getResponseData(relatedStationPackets, None, ["related"], iterationCounter + 1)
                    allPacketDicts.extend(relatedStationPacketDicts)

        # Add original packets
        allPacketDicts.extend(packetDicts)

        #return allPacketDicts.sort(key=lambda x: x['id'], reverse=False)
        return allPacketDicts

    def _getRelatedStationPacketsByStationIds(self, relatedStationIdList) :
        """Returns a list of the latest packet for the specified stations, this method should be used to find packets for a packet's related stations

        Args:
            relatedStationIdList (array):  Array of related station id's

        Returns:
            An array of the latest packet for the specified stations
        """
        if (relatedStationIdList) :
            query = MostRecentPacketsQuery(self.state, self.db)
            query.enableSimulateEmptyStation()
            return query.getPackets(relatedStationIdList)
        return []

