import logging
import psycopg2
from server.trackdirect.websocket.responses.FilterResponseCreator import FilterResponseCreator
from server.trackdirect.websocket.responses.HistoryResponseCreator import HistoryResponseCreator
from server.trackdirect.websocket.responses.FilterHistoryResponseCreator import FilterHistoryResponseCreator

class WebsocketResponseCreator:
    """The WebsocketResponseCreator ensures that a response is created for every valid received request."""

    def __init__(self, state, db):
        """
        Initialize the WebsocketResponseCreator.

        Args:
            state (WebsocketConnectionState): WebsocketConnectionState instance that contains current state.
            db (psycopg2.Connection): Database connection (with autocommit).
        """
        self.state = state
        self.logger = logging.getLogger('trackdirect')
        self.filter_response_creator = FilterResponseCreator(state, db)
        self.history_response_creator = HistoryResponseCreator(state, db)
        self.filter_history_response_creator = FilterHistoryResponseCreator(state, db)

    def get_responses(self, request, request_id):
        """
        Process a received request.

        Args:
            request (dict): The request to process.
            request_id (int): Request id of processed request.

        Returns:
            generator
        """
        try:
            if self.state.is_reset():
                yield self._get_reset_response()

            payload_type = request.get("payload_request_type")
            if payload_type in {1, 11}:
                yield self._get_loading_response()
                if self.state.filter_station_id_dict:
                    response = self.filter_history_response_creator.get_response()
                    if response is not None:
                        yield response
                else:
                    yield from self.history_response_creator.get_responses(request, request_id)

            elif payload_type == 7:
                # Update request for single station
                yield from self.history_response_creator.get_responses(request, request_id)

            elif payload_type in {4, 6, 8}:
                yield self._get_loading_response()
                yield from self.filter_response_creator.get_responses(request)

            else:
                self.logger.error('Unsupported request type: %s', request)

        except psycopg2.InterfaceError as e:
            # Connection to database is lost, better just exit
            raise e
        except Exception as e:
            self.logger.error('An error occurred: %s', e, exc_info=True)

    def _get_loading_response(self):
        """
        Create a loading response.

        Returns:
            dict: Loading response payload.
        """
        return {'payload_response_type': 32}

    def _get_reset_response(self):
        """
        Create a reset response.

        Returns:
            dict: Reset response payload.
        """
        return {'payload_response_type': 40}