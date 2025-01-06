import logging
import psycopg2
import psycopg2.extras
from server.trackdirect.TrackDirectConfig import TrackDirectConfig

class DatabaseConnection:
    """The DatabaseConnection class handles the most basic communication with the database."""

    def __init__(self):
        """Initialize the DatabaseConnection with configuration parameters."""
        config = TrackDirectConfig()

        self.logger = logging.getLogger('trackdirect')
        self.logger.warning("Creating DB connection to %s", config.db_hostname)

        self.host = config.db_hostname
        self.database = config.db_name
        self.username = config.db_username
        self.password = config.db_password
        self.port = config.db_port
        self.db = None
        self.db_no_autocommit = None

    def get_connection(self, autocommit=True, create_new_connection=False):
        """Returns a connection to the database.

        Args:
            autocommit (bool): Set to True if you want the connection to autocommit, otherwise False.
            create_new_connection (bool): Set to True to force a new connection.

        Returns:
            psycopg2.Connection: The database connection.
        """
        if create_new_connection:
            return self._create_new_connection(autocommit)

        if autocommit:
            if self.db is None:
                self.db = self._create_new_connection(autocommit)
            return self.db

        if self.db_no_autocommit is None:
            self.db_no_autocommit = self._create_new_connection(autocommit)
        return self.db_no_autocommit

    def _create_new_connection(self, autocommit):
        """Creates a new connection to the database.

        Args:
            autocommit (bool): Set to True if you want the connection to autocommit, otherwise False.

        Returns:
            psycopg2.Connection: The new database connection.
        """
        connection = psycopg2.connect(
            host=self.host,
            database=self.database,
            user=self.username,
            password=self.password,
            port=self.port,
            sslmode='disable',
            cursor_factory=psycopg2.extras.DictCursor
        )
        connection.autocommit = autocommit
        return connection