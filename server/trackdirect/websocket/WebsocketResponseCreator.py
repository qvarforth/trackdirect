import logging
from twisted.python import log

from math import floor, ceil
import datetime, time

import psycopg2, psycopg2.extras

from trackdirect.websocket.responses.FilterResponseCreator import FilterResponseCreator
from trackdirect.websocket.responses.HistoryResponseCreator import HistoryResponseCreator
from trackdirect.websocket.responses.FilterHistoryResponseCreator import FilterHistoryResponseCreator

class WebsocketResponseCreator():
    """The WebsocketResponseCreator will make sure that we create a response for every valid received request
    """

    def __init__(self, state, db):
        """The __init__ method.

        Args:
            state (WebsocketConnectionState):    WebsocketConnectionState instance that contains current state
            db (psycopg2.Connection):            Database connection (with autocommit)
        """
        self.state = state

        self.logger = logging.getLogger('trackdirect')

        self.filterResponseCreator = FilterResponseCreator(state, db)
        self.historyResponseCreator = HistoryResponseCreator(state, db)
        self.filterHistoryResponseCreator = FilterHistoryResponseCreator(state, db)

    def getResponses(self, request, requestId) :
        """Process a received request

        Args:
            request (dict):    The request to process
            requestId (int):   Request id of processed request

        Returns:
            generator
        """
        try:
            if (self.state.isReset()) :
                yield self._getResetResponse()

            if (request["payload_request_type"] == 1 or request["payload_request_type"] == 11) :
                yield self._getLoadingResponse()
                if (len(self.state.filterStationIdDict) > 0) :
                    response = self.filterHistoryResponseCreator.getResponse()
                    if (response is not None) :
                        yield response
                else :
                    for response in self.historyResponseCreator.getResponses(request, requestId) :
                        yield response

            elif (request["payload_request_type"] == 7) :
                # Update request for single station
                for response in self.historyResponseCreator.getResponses(request, requestId) :
                    yield response

            elif (request["payload_request_type"] in [4, 6, 8]) :
                yield self._getLoadingResponse()
                for response in self.filterResponseCreator.getResponses(request) :
                    yield response

            else :
                self.logger.error('Request is not supported')
                self.logger.error(request)

        except psycopg2.InterfaceError as e:
            # Connection to database is lost, better just exit
            raise e
        except Exception as e:
            self.logger.error(e, exc_info=1)

    def _getLoadingResponse(self) :
        """This method creates a loading response

        Returns:
            Dict
        """
        return {'payload_response_type': 32}

    def _getResetResponse(self) :
        """This method creates a reset response

        Returns:
            Dict
        """
        payload =  {'payload_response_type': 40}
        return payload
