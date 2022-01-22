<?php

class PDOConnection
{

    private static $_singletonInstance = null;
    private $_db;
    private $_config;

    public function __construct()
    {
        $this->_config = parse_ini_file(ROOT . '/../config/trackdirect.ini', true);
    }

    /**
     * Connect to the database.
     */
    private function createConnection()
    {
        if (is_array($this->_config) && isset($this->_config['database'])) {
            $databaseconfig = $this->_config['database'];

            if (!isset($databaseconfig['username'])) {
                $databaseconfig['username'] = get_current_user();
            }

            try {
                $this->_db = new PDO(
                    sprintf(
                        'pgsql:dbname=%s;host=%s;port=%s;user=%s;password=%s',
                        $databaseconfig['database'],
                        $databaseconfig['host'],
                        $databaseconfig['port'],
                        $databaseconfig['username'],
                        $databaseconfig['password']
                    ), null, null,
                    array(
                        PDO::ATTR_PERSISTENT => false,
                        PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION
                    )
                );
            } catch (PDOException $e) {
                echo $e;
                throw new Exception("Failed to connect to database.");
            }
        } else {
            throw new Exception("Failed to parse database ini file.");
        }
    }

    /**
     * Returnes a PDO db connection
     *
     * @return PDO
     */
    private function getConnection()
    {
        if($this->_db === null) {
            $this->createConnection();
        }

        return $this->_db;
    }

    /**
     * Executes an SQL statement, returning a result set as a PDOStatement object
     *
     * @param  string $sql
     * @return PDOStatement
     */
    public function query($sql)
    {
        return $this->getConnection()->query($sql);
    }

    /**
     * Prepares a statement for execution and returns a statement object
     *
     * @param  string $sql
     * @return PDOStatement
     */
    public function prepare($sql)
    {
        return $this->getConnection()->prepare($sql);
    }

    /**
     * Prepares a statement for execution and execute the prepared statement. Returnes the statment object
     *
     * @param  string $sql
     * @param  array  $arguments
     * @return PDOStatement
     */
    public function prepareAndExec($sql, array $arguments = array())
    {
        $statement = $this->prepare($sql);
        $statement->execute($arguments);
        return $statement;
    }

    /**
     * Initiates a transaction. Turns off autocommit mode. Returns TRUE on success or FALSE on failure.
     *
     * @return boolean
     */
    public function beginTransaction()
    {
        $this->getConnection()->beginTransaction();
    }

    /**
     * Commits a transaction. Returns TRUE on success or FALSE on failure.
     *
     * @return boolean
     */
    public function commit()
    {
        $this->getConnection()->commit();
    }

    /**
     * Rolls back the current transaction (that was started by beginTransaction). Returns TRUE on success or FALSE on failure.
     *
     * @return boolean
     */
    public function rollBack()
    {
        $this->getConnection()->rollBack();
    }

    /**
     * Get the ID of the last inserted record.
     *
     * @param  string $table
     * @param  string $column
     * @return int
     */
    public function lastInsertId($table, $column)
    {
        $suffix = '_' . $column . '_seq';

        /* The max length of an identifier is 63 characters,
         * if table_column_seq exceeds this postgres cuts the
         * table name by default. */
        $table = substr($table, 0, 63 - (strlen($suffix)));
        $sequenceName = $table . $suffix;

        return $this->getConnection()->lastInsertId($sequenceName);
    }

    /**
     * Returnes an initiated PDOConnection
     *
     * @return PDOConnection
     */
    public static function getInstance()
    {
        if (self::$_singletonInstance === null) {
            self::$_singletonInstance = new PDOConnection();
        }

        return self::$_singletonInstance;
    }
}
