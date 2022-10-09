import psycopg2
import psycopg2.extras

import trackdirect


class DatabaseConnection():
    """The DatabaseConnection class handles the most basic communication with the database
    """

    db = None
    dbNoAutoCommit = None

    def __init__(self):
        """The __init__ method.
        """
        config = trackdirect.TrackDirectConfig()
        self.host = config.dbHostname
        self.database = config.dbName
        self.username = config.dbUsername
        self.password = config.dbPassword
        self.port = config.dbPort

    def getConnection(self, autocommit=True, createNewConnection=False):
        """Returns a connection to the database

        Args:
            autocommit (boolean):            set to true if you want the connection to autocommit otherwise false
            createNewConnection (boolean):   set to true to force a new connection
        Returns:
            psycopg2.Connection
        """
        if (createNewConnection):
            db = self._createNewConnection()
            if (autocommit):
                # Active autocommit to avoid open transactions laying around
                DatabaseConnection.db.autocommit = True
            return db

        elif (autocommit):
            if (DatabaseConnection.db is None):
                DatabaseConnection.db = self._createNewConnection()
                # Active autocommit to avoid open transactions laying around
                DatabaseConnection.db.autocommit = True
            return DatabaseConnection.db

        else:
            if (DatabaseConnection.dbNoAutoCommit is None):
                DatabaseConnection.dbNoAutoCommit = self._createNewConnection()
            return DatabaseConnection.dbNoAutoCommit

    def _createNewConnection(self):
        """Returns a connection to the database

        Returns:
            psycopg2.Connection
        """
        return psycopg2.connect(host=self.host,
                                database=self.database,
                                user=self.username,
                                password=self.password,
                                port=self.port,
                                sslmode='disable',
                                cursor_factory=psycopg2.extras.DictCursor)
