<?php

class SenderRepository extends ModelRepository
{

    private static $_singletonInstance = null;

    public function __construct()
    {
        parent::__construct('Sender');
    }

    /**
     * Returnes an initiated SenderRepository
     *
     * @return SenderRepository
     */
    public static function getInstance()
    {
        if (self::$_singletonInstance === null) {
            self::$_singletonInstance = new SenderRepository();
        }

        return self::$_singletonInstance;
    }

    /**
     * Get object by id
     *
     * @param  int $id
     * @return Sender
     */
    public function getObjectById($id)
    {
        if (!isInt($id)) {
            return new Sender(0);
        }

        static $cache = array();
        $key = $id;
        if (!isset($cache[$key])) {
            $cache[$key] = $this->getObjectFromSql('select * from sender where id = ?', [$id]);
        }
        return $cache[$key];
    }
}
