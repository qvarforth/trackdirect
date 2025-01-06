import datetime


class DatabaseObjectFinder:
    """The DatabaseObjectFinder class can be used to check if a database table exists or not."""

    existingTables = {}

    def __init__(self, db):
        """
        Initialize the DatabaseObjectFinder.

        Args:
            db (psycopg2.Connection): Database connection.
        """
        self.db = db

    def set_table_exists(self, table_name):
        """
        Mark a table as existing.

        Args:
            table_name (str): Table to be marked as existing.
        """
        DatabaseObjectFinder.existingTables[table_name] = True

    def check_table_exists(self, table_name):
        """
        Check if the specified table exists in the database.

        Args:
            table_name (str): Table to check for existence.

        Returns:
            bool: True if the specified table exists in the database, otherwise False.
        """
        today_date_str = datetime.datetime.utcnow().strftime('%Y%m%d')
        yesterday_date_str = (datetime.datetime.utcnow() - datetime.timedelta(days=1)).strftime('%Y%m%d')

        if today_date_str in table_name or yesterday_date_str in table_name:
            # We only trust cache for the latest two days
            if table_name in DatabaseObjectFinder.existingTables:
                return True

        with self.db.cursor() as cur:
            cur.execute("""
                SELECT COUNT(*)
                FROM information_schema.tables
                WHERE table_name = %s
            """, (table_name,))
            if cur.fetchone()[0] == 1:
                DatabaseObjectFinder.existingTables[table_name] = True
                return True
            else:
                return False

    def check_index_exists(self, index):
        """
        Check if the specified index exists in the database.

        Args:
            index (str): Index to check for existence.

        Returns:
            bool: True if the specified index exists in the database, otherwise False.
        """
        with self.db.cursor() as cur:
            cur.execute("SELECT to_regclass(%s) AS name", (index,))
            record = cur.fetchone()
            if record and record['name'] == index:
                return True
            else:
                return False