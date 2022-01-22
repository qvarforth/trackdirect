import collections
import datetime
import time
import calendar
from math import sin, cos, sqrt, atan2, radians, floor, ceil

import logging
from twisted.python import log

from trackdirect.common.Repository import Repository
from trackdirect.objects.Station import Station
from trackdirect.database.DatabaseObjectFinder import DatabaseObjectFinder
from trackdirect.database.PacketTableCreator import PacketTableCreator
from trackdirect.exceptions.TrackDirectMissingStationError import TrackDirectMissingStationError


class StationRepository(Repository):
    """A Repository class for the Station class
    """

    # static class variables
    stationIdCache = {}
    stationNameCache = {}

    def __init__(self, db):
        """The __init__ method.

        Args:
            db (psycopg2.Connection): Database connection
        """
        self.db = db
        self.logger = logging.getLogger('trackdirect')
        self.dbObjectFinder = DatabaseObjectFinder(db)
        self.packetTableCreator = PacketTableCreator(db)

    def getObjectById(self, id):
        """The getObjectById method is supposed to return an object based on the specified id in database

        Args:
            id (int):  Database row id

        Returns:
            Station
        """
        selectCursor = self.db.cursor()
        selectCursor.execute("""select * from station where id = %s""", (id,))
        record = selectCursor.fetchone()

        dbObject = self.create()
        if (record is not None):
            dbObject = self.getObjectFromRecord(record)
        else:
            # station do not exists, return empty object
            pass

        selectCursor.close()
        return dbObject

    def getObjectListByStationIdList(self, stationIdList):
        """Returns a list of station objects

        Args:
            stationIdList (int):           Array of station ids

        Returns:
            array
        """
        selectCursor = self.db.cursor()
        selectCursor.execute(
            """select * from station where id in %s""", (tuple(stationIdList), ))

        result = []
        for record in selectCursor:
            if (record is not None):
                dbObject = self.getObjectFromRecord(record)
                result.append(dbObject)

        selectCursor.close()
        return result

    def getTinyObjectList(self):
        """Returns a list of all station id's

        Args:
            None

        Returns:
            array
        """
        selectCursor = self.db.cursor()
        selectCursor.execute(
            """select id, latest_packet_timestamp from station order by id""")

        result = []
        for record in selectCursor:
            if (record is not None):
                dbObject = self.create()
                dbObject.id = int(record["id"])
                dbObject.latestPacketTimestamp = record["latest_packet_timestamp"]
                result.append(dbObject)
        selectCursor.close()
        return result

    def getObjectList(self):
        """Returns a list of all station object's

        Args:
            None

        Returns:
            array
        """
        selectCursor = self.db.cursor()
        selectCursor.execute("""select * from station order by id""")

        result = []
        for record in selectCursor:
            dbObject = self.getObjectFromRecord(record)
            result.append(dbObject)
        selectCursor.close()
        return result

    def getObjectListByName(self, name, stationTypeId=None, sourceId=None, minTimestamp=None):
        """Returns a list of stations based on the specified name

        Args:
            name (string):             Name of station
            stationTypeId (int):       Station type id
            sourceId (int):            Station source id

        Returns:
            array
        """
        if (sourceId is not None and sourceId == 3):
            # If source is "APRS DUPLICATE" we use "APRS"
            sourceId = 1

        if (minTimestamp is None):
            minTimestamp = 0

        selectCursor = self.db.cursor()
        if (sourceId is not None and sourceId is not None):
            selectCursor.execute("""select *
                from station
                where station_type_id = %s
                    and name = %s
                    and (source_id = %s or source_id is null)
                    and latest_confirmed_packet_timestamp > %s""", (stationTypeId, name, sourceId, minTimestamp,))
        elif (sourceId is not None):
            selectCursor.execute("""select *
                from station
                where station_type_id = %s
                    and name = %s
                    and latest_confirmed_packet_timestamp > %s""", (stationTypeId, name, minTimestamp,))
        else:
            selectCursor.execute("""select *
                from station
                where name = %s
                    and latest_confirmed_packet_timestamp > %s""", (name, minTimestamp,))

        result = []
        for record in selectCursor:
            dbObject = self.getObjectFromRecord(record)
            result.append(dbObject)
        selectCursor.close()
        return result

    def getObjectByName(self, name, sourceId, stationTypeId=1, createNewIfMissing=True):
        """Returns an object based on the specified name of the station

        Args:
            name (str):                    Name of the station
            sourceId (int):                Station source id
            createNewIfMissing (boolean):  Set to true if a new station should be created if no one is found

        Returns:
            Station
        """
        if (sourceId == 3):
            # If source is "APRS DUPLICATE" we use "APRS"
            sourceId = 1

        selectCursor = self.db.cursor()
        if (sourceId is not None):
            selectCursor.execute(
                """select * from station where name = %s and (source_id is null or source_id = %s) order by id desc""", (name.strip(), sourceId))
        else:
            selectCursor.execute(
                """select * from station where name = %s order by id desc""", (name.strip()))
        record = selectCursor.fetchone()

        # Make sure we at least have an empty object...
        dbObject = self.create()
        if (record is not None):
            dbObject = self.getObjectFromRecord(record)
            if (dbObject.sourceId is None and dbObject.sourceId != sourceId):
                dbObject.sourceId = sourceId
                dbObject.save()
            if (dbObject.stationTypeId != stationTypeId and stationTypeId == 1):
                dbObject.stationTypeId = stationTypeId
                dbObject.save()

        elif (createNewIfMissing):
            # station do not exists, create it
            dbObject.name = name
            dbObject.sourceId = sourceId
            dbObject.stationTypeId = stationTypeId
            dbObject.save()

        selectCursor.close()
        return dbObject

    def getObjectListBySearchParameter(self, searchParameter, minTimestamp, limit):
        """Returns an array of the latest packet objects specified by searchParameter

        Args:
            searchParameter (str):  String to use when searching for packets (will be compared to station name)
            minTimestamp (int):     Min unix timestamp
            limit (int):            Max number of hits

        Returns:
            Array
        """
        searchParameter = searchParameter.strip().replace('%', '\%').replace('*', '%')
        selectCursor = self.db.cursor()
        result = []

        # Search for ogn registration
        if (self.dbObjectFinder.checkTableExists('ogn_device')):
            selectCursor.execute("""select * from ogn_device limit 1""")
            record = selectCursor.fetchone()
            if (record is not None):
                selectCursor.execute("""select * from station where latest_confirmed_packet_timestamp is not null and latest_confirmed_packet_timestamp > %s and latest_ogn_sender_address is not null and exists (select 1 from ogn_device where registration ilike %s and device_id = station.latest_ogn_sender_address) limit %s""", (minTimestamp, searchParameter, (limit - len(result)), ))
                for record in selectCursor:
                    dbObject = self.getObjectFromRecord(record)
                    result.append(dbObject)

            # Search for ogn sender address
            if (len(result) < limit):
                selectCursor.execute("""select * from station where latest_confirmed_packet_timestamp is not null and latest_confirmed_packet_timestamp > %s and latest_ogn_sender_address ilike %s limit %s""",
                                     (minTimestamp, searchParameter, (limit - len(result)), ))
                for record in selectCursor:
                    dbObject = self.getObjectFromRecord(record)
                    result.append(dbObject)

        # Search for station name
        if (len(result) < limit):
            selectCursor.execute("""select * from station where latest_confirmed_packet_timestamp is not null and latest_confirmed_packet_timestamp > %s and name ilike %s limit %s""",
                                 (minTimestamp, searchParameter, (limit - len(result)), ))
            for record in selectCursor:
                dbObject = self.getObjectFromRecord(record)
                result.append(dbObject)

        return result

    def getCachedObjectById(self, stationId):
        """Get Station based on station id

        Args:
            stationId (int):     Id of the station

        Returns:
            Station
        """
        if (stationId not in StationRepository.stationIdCache):
            station = self.getObjectById(stationId)
            if (station.isExistingObject()):
                maxNumberOfStations = 100
                if (len(StationRepository.stationIdCache) > maxNumberOfStations):
                    # reset cache
                    StationRepository.stationIdCache = {}
                StationRepository.stationIdCache[stationId] = station
                return station
        else:
            try:
                return StationRepository.stationIdCache[stationId]
            except KeyError as e:
                station = self.getObjectById(stationId)
                if (station.isExistingObject()):
                    return station
        raise TrackDirectMissingStationError(
            'No station with specified id found')

    def getCachedObjectByName(self, stationName, sourceId):
        """Get Station based on station name

        Args:
            stationName (string): Station name
            sourceId (int):       Station source id

        Returns:
            Station
        """
        if (sourceId == 3):
            # If source is "APRS DUPLICATE" we use "APRS"
            sourceId = 1

        if (sourceId is not None):
            key = hash(stationName + ';' + str(sourceId))
        else:
            key = hash(stationName)
        if (key not in StationRepository.stationNameCache):
            station = self.getObjectByName(stationName, sourceId, None, False)
            if (station.isExistingObject()):
                maxNumberOfStations = 100
                if (len(StationRepository.stationNameCache) > maxNumberOfStations):
                    # reset cache
                    StationRepository.stationNameCache = {}
                StationRepository.stationNameCache[key] = station
                return station
        else:
            try:
                return StationRepository.stationNameCache[key]
            except KeyError as e:
                station = self.getObjectByName(
                    stationName, sourceId, None, False)
                if (station.isExistingObject()):
                    return station
        raise TrackDirectMissingStationError(
            'No station with specified station name found')

    def getObjectFromRecord(self, record):
        """Returns a station object based on the specified database record dict

        Args:
            record (dict):  A database record dict from the station database table

        Returns:
            Station
        """
        dbObject = self.create()
        if (record is not None):
            dbObject.id = int(record["id"])
            dbObject.name = record["name"]
            if (record["latest_sender_id"] is not None):
                dbObject.latestSenderId = int(record["latest_sender_id"])
            dbObject.stationTypeId = int(record["station_type_id"])
            if (record["source_id"] is not None):
                dbObject.sourceId = int(record["source_id"])

            dbObject.latestLocationPacketId = record["latest_location_packet_id"]
            dbObject.latestLocationPacketTimestamp = record["latest_location_packet_timestamp"]

            dbObject.latestConfirmedPacketId = record["latest_confirmed_packet_id"]
            dbObject.latestConfirmedPacketTimestamp = record["latest_confirmed_packet_timestamp"]
            dbObject.latestConfirmedSymbol = record["latest_confirmed_symbol"]
            dbObject.latestConfirmedSymbolTable = record["latest_confirmed_symbol_table"]
            dbObject.latestConfirmedLatitude = record["latest_confirmed_latitude"]
            dbObject.latestConfirmedLongitude = record["latest_confirmed_longitude"]
            dbObject.latestConfirmedMarkerId = record["latest_confirmed_marker_id"]

            dbObject.latestPacketId = record["latest_packet_id"]
            dbObject.latestPacketTimestamp = record["latest_packet_timestamp"]

            dbObject.latestWeatherPacketId = record["latest_weather_packet_id"]
            dbObject.latestWeatherPacketTimestamp = record["latest_weather_packet_timestamp"]

            dbObject.latestTelemetryPacketId = record["latest_telemetry_packet_id"]
            dbObject.latestTelemetryPacketTimestamp = record["latest_telemetry_packet_timestamp"]

            dbObject.latestOgnPacketId = record["latest_ogn_packet_id"]
            dbObject.latestOgnPacketTimestamp = record["latest_ogn_packet_timestamp"]
            dbObject.latestOgnSenderAddress = record["latest_ogn_sender_address"]
            dbObject.latestOgnAircraftTypeId = record["latest_ogn_aircraft_type_id"]
            dbObject.latestOgnAddressTypeId = record["latest_ogn_address_type_id"]

        return dbObject

    def create(self):
        """Creates an empty Station object

        Returns:
            Station
        """
        return Station(self.db)
