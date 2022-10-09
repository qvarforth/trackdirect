import logging

import time

import aprslib

from trackdirect.parser.AprsPacketParser import AprsPacketParser


import trackdirect

from trackdirect.exceptions.TrackDirectParseError import TrackDirectParseError

from trackdirect.websocket.responses.ResponseDataConverter import ResponseDataConverter
from trackdirect.websocket.responses.HistoryResponseCreator import HistoryResponseCreator


class AprsISPayloadCreator():
    """The AprsISPayloadCreator creates a payload to send to client based on data received form the APRS-IS server
    """

    def __init__(self, state, db):
        """The __init__ method.

        Args:
            state (ConnectionState):   Instance of ConnectionState which contains the current state of the connection
            db (psycopg2.Connection):  Database connection (with autocommit)
        """
        self.logger = logging.getLogger('trackdirect')
        self.state = state
        self.db = db
        self.responseDataConverter = ResponseDataConverter(state, db)
        self.historyResponseCreator = HistoryResponseCreator(state, db)
        self.config = trackdirect.TrackDirectConfig()
        self.stationHashTimestamps = {}

        self.saveOgnStationsWithMissingIdentity = False
        if (self.config.saveOgnStationsWithMissingIdentity) :
            self.saveOgnStationsWithMissingIdentity = True


    def getPayloads(self, line, sourceId):
        """Takes a raw packet and returnes a dict with the parsed result

        Args:
            line (string):        The raw packet as a string
            sourceId (int):       The id of the source

        Returns:
            generator
        """
        try :
            packet = self._parse(line, sourceId)
            if (not self._isPacketValid(packet)) :
                return

            if (packet.stationId not in self.state.stationsOnMapDict) :
                self.state.stationsOnMapDict[packet.stationId] = True

            if (len(self.state.filterStationIdDict) > 0 and packet.stationId in self.state.filterStationIdDict) :
                for response in self._getPreviousPacketsPayload(packet):
                    yield response

            yield self._getRealTimePacketPayload(packet)
        except (aprslib.ParseError, aprslib.UnknownFormat, TrackDirectParseError) as exp:
            # We could send the raw part even if we failed to parse it...
            pass
        except (UnicodeDecodeError) as exp:
            # just forget about this packet
            pass


    def _parse(self, line, sourceId) :
        """Parse packet raw

        Args:
            line (string):   The raw packet as a string
            sourceId (int):  The id of the source

        Returns:
            Packet
        """
        basicPacketDict = aprslib.parse(line)
        parser = AprsPacketParser(self.db, self.saveOgnStationsWithMissingIdentity)
        parser.setDatabaseWriteAccess(False)
        parser.setSourceId(sourceId)
        try :
            packet = parser.getPacket(basicPacketDict)
            if (packet.mapId == 15) :
                return None

            if (packet.mapId == 4) :
                # Looks like we don't have enough info in db to get a markerId, wait some and try again
                time.sleep(1)
                return parser.getPacket(basicPacketDict)

            return packet
        except (aprslib.ParseError, aprslib.UnknownFormat, TrackDirectParseError) as exp:
            return None


    def _isPacketValid(self, packet) :
        """Returns True if specified packet is valid to send to client

        Args:
            packet (Packet):   Found packet that we may want to send to client

        Returns:
            True if specified packet is valid to send to client
        """
        if (packet is None) :
            return False

        if (packet.mapId == 4) :
            return False

        if (packet.stationId is None) :
            return False

        if (packet.markerId is None or packet.markerId == 1) :
            return False

        if (packet.latitude is None or packet.longitude is None) :
            return False

        if (len(self.state.filterStationIdDict) > 0) :
            if (packet.stationId not in self.state.filterStationIdDict) :
                # This packet does not belong to the station Id that the user is filtering on
                return False
        return True


    def _getRealTimePacketPayload(self, packet) :
        """Takes a packet received directly from APRS-IS and a creates a payload response

        Args:
            packet (Packet):     The packet direclty received from APRS-IS

        Returns:
            Dict
        """
        options = ["realtime"]
        data = self.responseDataConverter.getResponseData([packet], None, options)
        payload = {'payload_response_type': 2, 'data': data}
        return payload


    def _getPreviousPacketsPayload(self, packet) :
        """Creates payload that contains previous packets for the station that has sent the specified packet

        Args:
            packet (Packet):   The packet direclty received from APRS-IS

        Returns:
            generator
        """
        latestTimestampOnMap = self.state.getStationLatestTimestampOnMap(packet.stationId)
        if (latestTimestampOnMap is None) :
            latestTimestampOnMap = 0
        latestTimestampOnMap = latestTimestampOnMap + 5
        if (self.state.isStationHistoryOnMap(packet.stationId)
                and packet.markerPrevPacketTimestamp is not None
                and packet.timestamp > latestTimestampOnMap
                and packet.markerPrevPacketTimestamp > latestTimestampOnMap) :
            # Ups! We got a problem, the previous packet for this station has not been sent to client
            # If no packets at all had been sent we would have marked the realtime-packet to be overwritten,
            # but now we have a missing packet from current station that may never be sent!
            # Send it now! This may result in that we send the same packet twice (but client should handle that)
            request = {}
            request["station_id"] = packet.stationId
            request["payload_request_type"] = 7

            # This request will send all packets that is missing (maybe also this real-time packet, but we can live with that...)
            for response in self.historyResponseCreator.getResponses(request, None) :
                yield response
