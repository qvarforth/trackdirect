<?php

class StationTelemetryParamRepository extends ModelRepository
{

    private static $_singletonInstance = null;

    public function __construct()
    {
        parent::__construct('StationTelemetryParam');
    }

    /**
     * Returnes an initiated StationTelemetryParamRepository
     *
     * @return StationTelemetryParamRepository
     */
    public static function getInstance()
    {
        if (self::$_singletonInstance === null) {
            self::$_singletonInstance = new StationTelemetryParamRepository();
        }

        return self::$_singletonInstance;
    }

    /**
     * Get object by id
     *
     * @param  int $id
     * @return StationTelemetryParam
     */
    public function getObjectById($id)
    {
        return $this->getObjectFromSql('select * from station_telemetry_param where id = ?', [$id]);
    }
}
