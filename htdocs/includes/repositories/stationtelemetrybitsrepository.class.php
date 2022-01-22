<?php

class StationTelemetryBitsRepository extends ModelRepository
{

    private static $_singletonInstance = null;

    public function __construct()
    {
        parent::__construct('StationTelemetryBits');
    }

    /**
     * Returnes an initiated StationTelemetryBitsRepository
     *
     * @return StationTelemetryBitsRepository
     */
    public static function getInstance()
    {
        if (self::$_singletonInstance === null) {
            self::$_singletonInstance = new StationTelemetryBitsRepository();
        }

        return self::$_singletonInstance;
    }

    /**
     * Get object by id
     *
     * @param  int $id
     * @return StationTelemetryBits
     */
    public function getObjectById($id)
    {
        return $this->getObjectFromSql('select * from station_telemetry_bits where id = ?', [$id]);
    }
}
