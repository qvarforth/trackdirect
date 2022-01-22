<?php

class Database
{

    private $_existingTables;
    private static $_singletonInstance = null;

    /**
     * The constructor
     */
    public function __construct()
    {
        $this->_existingTables = Array();
    }

    /**
     * Returnes an initiated Database
     *
     * @return Database
     */
    public static function getInstance()
    {
        if (self::$_singletonInstance === null) {
            self::$_singletonInstance = new Database();
        }

        return self::$_singletonInstance;
    }

    /**
     * Returnes true if specified table exists in database
     *
     * @param  string $tablename
     * @return boolean
     */
    public function checkTableExists($tablename)
    {

        if (!isset($this->_existingTables[$tablename])) {

            $sql = "SELECT COUNT(*) c
                FROM information_schema.tables
                WHERE table_name = ?";

            $pdo = PDOConnection::getInstance();
            $stmt = $pdo->prepareAndExec($sql, [str_replace('\'', '\'\'', $tablename)]);

            $record = $stmt->fetch(PDO::FETCH_ASSOC);
            if ($record && $record['c'] > 0) {
                $this->_existingTables[$tablename] = true;
            } else {
                $this->_existingTables[$tablename] = false;
            }
        }

        return $this->_existingTables[$tablename];
    }
}
