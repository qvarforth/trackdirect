<?php

class StationTelemetryEqnsRepository extends ModelRepository
{

    private static $_singletonInstance = null;

    public function __construct()
    {
        parent::__construct('StationTelemetryEqns');
    }

    /**
     * Returnes an initiated StationTelemetryEqnsRepository
     *
     * @return StationTelemetryEqnsRepository
     */
    public static function getInstance()
    {
        if (self::$_singletonInstance === null) {
            self::$_singletonInstance = new StationTelemetryEqnsRepository();
        }

        return self::$_singletonInstance;
    }

    /**
     * Get object by id
     *
     * @param  int $id
     * @return StationTelemetryEqns
     */
    public function getObjectById($id)
    {
        return $this->getObjectFromSql('select * from station_telemetry_eqns where id = ?', [$id]);
    }
}
