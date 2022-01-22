<?php

class StationTelemetryUnitRepository extends ModelRepository
{

    private static $_singletonInstance = null;

    public function __construct()
    {
        parent::__construct('StationTelemetryUnit');
    }

    /**
     * Returnes an initiated StationTelemetryUnitRepository
     *
     * @return StationTelemetryUnitRepository
     */
    public static function getInstance()
    {
        if (self::$_singletonInstance === null) {
            self::$_singletonInstance = new StationTelemetryUnitRepository();
        }

        return self::$_singletonInstance;
    }

    /**
     * Get object by id
     *
     * @param  int $id
     * @return StationTelemetryUnit
     */
    public function getObjectById($id)
    {
        return $this->getObjectFromSql('select * from station_telemetry_unit where id = ?', [$id]);
    }
}
