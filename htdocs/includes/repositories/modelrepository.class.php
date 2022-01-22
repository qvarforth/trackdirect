<?php

class ModelRepository
{

    private $_class;
    private static $_singletonInstance = null;

    public function __construct($class = 'Model')
    {
        $this->_class = $class;
    }

    /**
     * Returnes an initiated ModelRepository
     *
     * @return ModelRepository
     */
    public static function getInstance()
    {
        if (self::$_singletonInstance === null) {
            self::$_singletonInstance = new ModelRepository();
        }

        return self::$_singletonInstance;
    }

    /**
     * Returns an object based on the provided sql
     *
     * @param  string $sql
     * @param  array  $arg
     * @return StandardItem
     */
    public function getObjectFromSql($sql, $arg)
    {
        $pdo = PDOConnection::getInstance();

        $stmt = $pdo->prepareAndExec($sql, $arg);
        if ($record = $stmt->fetch(PDO::FETCH_ASSOC)) {
            return $this->_getObjectFromRecord($record);
        }

        // No object found, return empty object
        return new $this->_class(null);
    }

    /**
     * Returns an array of object based on the provided sql
     *
     * @param  string $sql
     * @param  array  $arg
     * @return array
     */
    public function getObjectListFromSql($sql, $arg)
    {
        $pdo = PDOConnection::getInstance();

        $stmt = $pdo->prepareAndExec($sql, $arg);
        $records = $stmt->fetchAll(PDO::FETCH_ASSOC);
        if (is_array($records) && !empty($records)) {
            return $this->_getObjectListFromRecords($records);
        }

        // No object found, return empty array
        return [];
    }

    /**
     * Returns an object based on the provided record
     *
     * @param  array $record
     * @return StandardItem
     */
    protected function _getObjectFromRecord($record)
    {
        if (isset($record['id'])) {
            $object = new $this->_class($record['id']);
        } else {
            $object = new $this->_class(0);
        }
        $object->updateObjectFromArray($record);
        return $object;
    }

    /**
     * Returns a list of objects filled with values from the provided records
     *
     * @param  array $records
     * @return Array of StandardItem
     */
    protected function _getObjectListFromRecords($records)
    {
        $list = Array();

        foreach ($records as $record) {
            $list[] = $this->_getObjectFromRecord($record);
        }

        return $list;
    }
}