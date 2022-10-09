import time
import trackdirect
from math import ceil
from trackdirect.parser.policies.MapSectorPolicy import MapSectorPolicy

class WebsocketConnectionState():
    """An WebsocketConnectionState instance contains information about the current state of a websocket connection
    """

    def __init__(self) :
        """The __init__ method.
        """
        self.totalReset()
        self.latestRequestType = None
        self.latestRequestTimestamp = 0
        self.latestRequestId = 0
        self.latestHandledRequestId = 0
        self.config = trackdirect.TrackDirectConfig()
        self.noRealTime = False
        self.disconnected = False


    def isReset(self) :
        """Returns true if state just has been reset

        Returns:
            Boolean
        """
        return (not self.stationsOnMapDict
            and not self.maxCompleteStationTimestampDict
            and not self.maxAllStationTimestampDict
            and not self.maxMapSectorPacketTimestampDict
            and not self.maxMapSectorOverwritePacketTimestampDict)


    def reset(self) :
        """This function will reset information related to what stations that has been added to map
        (this is for example used when the number of minutes is changed by the client)
        """
        self.stationsOnMapDict = {}
        self.maxCompleteStationTimestampDict = {}
        self.maxAllStationTimestampDict = {}
        self.maxMapSectorPacketTimestampDict = {}
        self.maxMapSectorOverwritePacketTimestampDict = {}


    def totalReset(self) :
        """This function will reset everything
        (this is for example used when client seems to be inactive and we just want to stop everything)
        """
        self.reset()
        self.latestMinutesRequest = 60
        self.latestTimeTravelRequest = None
        self.onlyLatestPacketRequested = None
        self.latestNeLat = 0
        self.latestNeLng = 0
        self.latestSwLat = 0
        self.latestSwLng = 0
        self.filterStationIdDict = {}


    def isMapEmpty(self) :
        """Returns true if map is empty

        Returns:
            Boolean
        """
        if (not self.maxMapSectorPacketTimestampDict
                and not self.maxMapSectorOverwritePacketTimestampDict
                and not self.maxCompleteStationTimestampDict
                and not self.maxAllStationTimestampDict) :
            return True
        else :
            return False


    def isStationsOnMap(self, stationIds) :
        """Returns true if all specified stations allready exists on map

        Args:
            stationIds (int):    The station id's that we are interested in

        Returns:
            boolean
        """
        for stationId in stationIds :
            if (stationId not in self.stationsOnMapDict) :
                return False
        return True


    def isStationHistoryOnMap(self, stationId) :
        """Returns true if specified station allready has it's history on map

        Args:
            stationId (int):    The station id that we are interested in

        Returns:
            boolean
        """
        if (stationId not in self.maxCompleteStationTimestampDict) :
            return False
        else :
            return True


    def getStationLatestTimestampOnMap(self, stationId, onlyIncludeComplete = True) :
        """Returns the timestamp of the latest sent packet to client

        Args:
            stationId (int):             The station id that we are interested in
            onlyIncludeComplete (bool):  When true we only return timestamp data for complete stations

        Returns:
            boolean
        """
        if (not onlyIncludeComplete and stationId in self.maxAllStationTimestampDict) :
            return self.maxAllStationTimestampDict[stationId]
        elif (stationId in self.maxCompleteStationTimestampDict) :
            return self.maxCompleteStationTimestampDict[stationId]
        else :
            return None


    def isValidLatestPosition(self) :
        """Returns true if latest requested map bounds is valid

        Note:
            If we received 0,0,0,0 as map bounds we should not send anything,
            not even in filtering mode (filtering mode should send 90,180,-90,-180 when it wants data)

        Returns:
            Boolean
        """
        if (self.latestNeLat == 0
                and self.latestNeLng == 0
                and self.latestSwLat == 0
                and self.latestSwLng == 0) :
            return False
        else :
            return True


    def isMapSectorKnown(self, mapSector):
        """Returns True if we have added any stations with complete history to this map sector

        Args:
            mapSector (int):  The map sector that we are interested in

        Returns:
            Boolean
        """
        if (mapSector in self.maxMapSectorPacketTimestampDict) :
            return True
        else :
            return False


    def getMapSectorTimestamp(self, mapSector) :
        """Returns the latest handled timestamp in specified map sector (as a Unix timestamp as an integer)

        Args:
            mapSector (int):  The map sector that we are interested in

        Returns:
            int
        """
        if (mapSector in self.maxMapSectorPacketTimestampDict) :
            return self.maxMapSectorPacketTimestampDict[mapSector];
        elif (self.onlyLatestPacketRequested and mapSector in self.maxMapSectorOverwritePacketTimestampDict) :
            return self.maxMapSectorOverwritePacketTimestampDict[mapSector]
        elif (self.latestTimeTravelRequest is not None) :
            return int(self.latestTimeTravelRequest) - (int(self.latestMinutesRequest)*60)
        else :
            return int(time.time()) - (int(self.latestMinutesRequest)*60)


    def getVisibleMapSectors(self) :
        """Get the map sectors currently visible

        Returns:
            Array of map sectors (array of integers)
        """
        maxLat = self.latestNeLat
        maxLng = self.latestNeLng
        minLat = self.latestSwLat
        minLng = self.latestSwLng

        result = []
        if (maxLng < minLng) :
            result.extend(self.getMapSectorsByInterval(minLat, maxLat, minLng, 180.0));
            minLng = -180.0;

        result.extend(self.getMapSectorsByInterval(minLat, maxLat, minLng, maxLng))

        # Add the world wide area code
        # This seems to result in very bad performance....
        #result.append(99999999)

        return result[::-1]


    def getMapSectorsByInterval(self, minLat, maxLat, minLng, maxLng) :
        """Get the map sectors for specified interval

        Returns:
            Array of map sectors (array of integers)
        """
        result = []
        mapSectorPolicy = MapSectorPolicy()
        minAreaCode = mapSectorPolicy.getMapSector(minLat,minLng)
        maxAreaCode = mapSectorPolicy.getMapSector(maxLat,maxLng)
        if (minAreaCode is not None and maxAreaCode is not None) :
            lngDiff = int(ceil(maxLng)) - int(ceil(minLng))
            areaCode = minAreaCode
            while (areaCode <= maxAreaCode) :
                if (areaCode % 10 == 5) :
                    result.append(areaCode)
                else :
                    result.append(areaCode)
                    result.append(areaCode + 5)

                for i in range(1, lngDiff+1) :
                    if (areaCode % 10 == 5) :
                        result.append(areaCode + (10*i) - 5)
                        result.append(areaCode + (10*i))
                    else :
                        result.append(areaCode + (10*i))
                        result.append(areaCode + (10*i) + 5)

                # Lat takes 0.2 jumps
                areaCode = areaCode + 20000

        return result


    def setLatestMinutes(self, minutes, referenceTime) :
        """Set the latest requested number of minutes, returnes true if something has changed

        Args:
            minutes (int):           latest requested number of minutes
            referenceTime (int):     latest requested reference time

        Returns:
            Boolean
        """
        if (minutes is None) :
            minutes = 60
        elif (len(self.filterStationIdDict) == 0
                and int(minutes) > int(self.config.maxDefaultTime)) :
            # max 24h
            minutes = int(self.config.maxDefaultTime)
        elif (len(self.filterStationIdDict) > 0
                and int(minutes) > int(self.config.maxFilterTime)) :
            # max 10 days
            minutes = int(self.config.maxFilterTime)

        if (not self.config.allowTimeTravel
                and int(minutes) > int(1440)) :
            # max 24h
            minutes = 1440

        if referenceTime is not None and referenceTime < 0 :
            referenceTime = 0

        changed = False
        if (self.config.allowTimeTravel) :
            if ((self.latestTimeTravelRequest is not None
                        and referenceTime is not None
                        and self.latestTimeTravelRequest != referenceTime)
                    or (self.latestTimeTravelRequest is not None
                        and referenceTime is None)
                    or (self.latestTimeTravelRequest is None
                        and referenceTime is not None)) :
                self.latestTimeTravelRequest = referenceTime
                self.reset()
                changed = True

        if (self.latestMinutesRequest is None
                or self.latestMinutesRequest != minutes) :
            self.latestMinutesRequest = minutes
            self.reset()
            changed = True
        return changed


    def setOnlyLatestPacketRequested(self, onlyLatestPacketRequested) :
        """Set if only latest packets is requested or not

        Args:
            onlyLatestPacketRequested (Boolean):  Boolean that sys if

        """
        self.onlyLatestPacketRequested = onlyLatestPacketRequested


    def setLatestMapBounds(self, neLat, neLng, swLat, swLng) :
        """Set map bounds requested by client

        Args:
            neLat (float): Requested north east latitude
            neLng (float): Requested north east longitude
            swLat (float): Requested south west latitude
            swLng (float): Requested south west longitude
        """
        if (neLat is None or neLng is None or swLat is None or swLng is None) :
            self.latestNeLat = 0
            self.latestNeLng = 0
            self.latestSwLat = 0
            self.latestSwLng = 0
        else :
            self.latestNeLat = neLat
            self.latestNeLng = neLng
            self.latestSwLat = swLat
            self.latestSwLng = swLng


    def setMapSectorLatestOverwriteTimeStamp(self, mapSector, timestamp) :
        """Set a new latest handled timestamp for a map sector (in this case the overwritable type of packets)

        Args:
            mapSector (int):  The map sector that we should add a new timestamp to
            timestamp (int):  The unix timestamp that should be added
        """
        if (mapSector not in self.maxMapSectorOverwritePacketTimestampDict or self.maxMapSectorOverwritePacketTimestampDict[mapSector] < timestamp) :
            self.maxMapSectorOverwritePacketTimestampDict[mapSector] = timestamp


    def setMapSectorLatestTimeStamp(self, mapSector, timestamp) :
        """Set a new latest handled timestamp for a map sector

        Args:
            mapSector (int):  The map sector that we should add a new timestamp to
            timestamp (int):  The unix timestamp that should be added
        """
        if (mapSector not in self.maxMapSectorPacketTimestampDict or self.maxMapSectorPacketTimestampDict[mapSector] < timestamp) :
            # To avoid that we miss packet that was recived later during the same second we mark map-sector to be complete for the previous second.
            # This may result in that we sent the same apcket twice but client will handle that.
            self.maxMapSectorPacketTimestampDict[mapSector] = timestamp - 1


    def setCompleteStationLatestTimestamp(self, stationId, timestamp) :
        """Set a new latest handled timestamp for a complete station (a station with all packets added to map)

        Args:
            stationId (int):  The station that we add want to add a new timestamp for
            timestamp (int):  The unix timestamp that should be added
        """
        if (stationId not in self.maxCompleteStationTimestampDict or self.maxCompleteStationTimestampDict[stationId] < timestamp) :
            # For stations we do not need to set the previous second since a station is rarly sending several packets the same second
            self.maxCompleteStationTimestampDict[stationId] = timestamp


    def setStationLatestTimestamp(self, stationId, timestamp) :
        """Set a new latest handled timestamp for station

        Args:
            stationId (int):  The station that we add want to add a new timestamp for
            timestamp (int):  The unix timestamp that should be added
        """
        if (stationId not in self.maxAllStationTimestampDict or self.maxAllStationTimestampDict[stationId] < timestamp) :
            # For stations we do not need to set the previous second since a station is rarly sending several packets the same second
            self.maxAllStationTimestampDict[stationId] = timestamp


    def disableRealTime(self) :
        """Disable real time functionality
        """
        self.noRealTime = True