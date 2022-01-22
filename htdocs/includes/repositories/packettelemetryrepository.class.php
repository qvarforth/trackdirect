<?php

class PacketTelemetryRepository extends ModelRepository
{

    private static $_singletonInstance = null;

    public function __construct()
    {
        parent::__construct('PacketTelemetry');
    }

    /**
     * Returnes an initiated PacketTelemetryRepository
     *
     * @return PacketTelemetryRepository
     */
    public static function getInstance()
    {
        if (self::$_singletonInstance === null) {
            self::$_singletonInstance = new PacketTelemetryRepository();
        }

        return self::$_singletonInstance;
    }

    /**
     * Get object by id
     *
     * @param  int $id
     * @param  int $timestamp
     * @return PacketTelemetry
     */
    public function getObjectById($id, $timestamp)
    {
        if (!isInt($id) || !isInt($timestamp)) {
            return new PacketTelemetry(0);
        }
        return $this->getObjectFromSql('select * from packet_telemetry where id = ? and timestamp = ?', [$id, $timestamp]);
    }

    /**
     * Get object by packet id
     *
     * @param  int $id
     * @param  int $timestamp
     * @return PacketTelemetry
     */
    public function getObjectByPacketId($id, $timestamp)
    {
        if (!isInt($id) || !isInt($timestamp)) {
            return new PacketTelemetry(0);
        }
        return $this->getObjectFromSql('select * from packet_telemetry where packet_id = ? and timestamp = ?', [$id, $timestamp]);
    }

    /**
     * Get latest object by station id (for the latest 3 days)
     *
     * @param  int $stationId
     * @return array
     */
    public function getLatestObjectByStationId($stationId)
    {
        if (!isInt($stationId)) {
            return new PacketTelemetry(0);
        }
        return $this->getObjectFromSql(
            'select * from packet_telemetry
            where station_id = ?
                and timestamp > ?
            order by timestamp desc limit 1', [$stationId, (time() - 24*60*60*3)]
        );
    }

    /**
     * Get latest object list by station id (useful for creating a chart)
     *
     * @param  int   $stationId
     * @param  int   $endTimestamp
     * @param  int   $hours
     * @param  array $columns
     * @return array
     */
    public function getLatestDataListByStationId($stationId, $endTimestamp , $hours, $columns)
    {
        if (!isInt($stationId) || !isInt($endTimestamp) || !isInt($hours)) {
            return [];
        }
        $minTimestamp = $endTimestamp - (60*60*$hours);

        $sql = 'select ' . implode(',', $columns) . ' from ' . $table . '
            where station_id = ?
                and timestamp >= ?
                and timestamp <= ?
            order by timestamp';
        $arg = [$stationId, $minTimestamp, $endTimestamp];

        $pdo = PDOConnection::getInstance();
        $stmt = $pdo->prepareAndExec($sql, $arg);
        return $stmt->fetchAll(PDO::FETCH_ASSOC);
    }

    /**
     * Get latest object list by station id
     * We only include telemetry that has the same params, units and eqns as the latest telemetry packet
     *
     * @param  int             $stationId
     * @param  int             $limit
     * @param  int             $offset
     * @param  int             $maxDays
     * @return array
     */
    public function getLatestObjectListByStationId($stationId, $limit, $offset, $maxDays = 7)
    {
        if (!isInt($stationId) || !isInt($limit) || !isInt($offset) || !isInt($maxDays)) {
            return [];
        }
        $latestObject = $this->getLatestObjectByStationId($stationId);

        $sqlParameters = Array();
        $sql = 'select * from packet_telemetry where station_id = ? and timestamp > ?';
        $sqlParameters[] = $stationId;
        $sqlParameters[] = (time() - 24*60*60*$maxDays);

        if ($latestObject->stationTelemetryParamId !== null) {
            $sql .= ' and station_telemetry_param_id = ?';
            $sqlParameters[] = $latestObject->stationTelemetryParamId;
        } else {
            $sql .= ' and station_telemetry_param_id is null';
        }

        if ($latestObject->stationTelemetryUnitId !== null) {
            $sql .= ' and station_telemetry_unit_id = ?';
            $sqlParameters[] = $latestObject->stationTelemetryUnitId;
        } else {
            $sql .= ' and station_telemetry_unit_id is null';
        }

        // if ($latestObject->stationTelemetryEqnsId !== null) {
        // $sql .= ' and station_telemetry_eqns_id = ?';
        // $sqlParameters[] = $latestObject->stationTelemetryEqnsId;
        // } else {
        // $sql .= ' and station_telemetry_eqns_id is null';
        // }

        if ($latestObject->stationTelemetryBitsId !== null) {
            $sql .= ' and station_telemetry_bits_id = ?';
            $sqlParameters[] = $latestObject->stationTelemetryBitsId;
        } else {
            $sql .= ' and station_telemetry_bits_id is null';
        }

        $sql .= ' order by timestamp desc limit ? offset ?';
        $sqlParameters[] = $limit;
        $sqlParameters[] = $offset;

        return $this->getObjectListFromSql($sql, $sqlParameters);
    }


    /**
     * Get latest number of packets by station id
     * We only include telemetry that has the same params, units and eqns as the latest telemetry packet
     *
     * @param  int             $stationId
     * @param  int             $maxDays
     * @return int
     */
    public function getLatestNumberOfPacketsByStationId($stationId, $maxDays = 7)
    {
        if (!isInt($stationId) || !isInt($maxDays)) {
            return 0;
        }
        $latestObject = $this->getLatestObjectByStationId($stationId);

        $sqlParameters = Array();
        $sql = 'select count(*) c from packet_telemetry where station_id = ? and timestamp > ?';
        $sqlParameters[] = $stationId;
        $sqlParameters[] = (time() - 24*60*60*$maxDays);

        if ($latestObject->stationTelemetryParamId !== null) {
            $sql .= ' and station_telemetry_param_id = ?';
            $sqlParameters[] = $latestObject->stationTelemetryParamId;
        } else {
            $sql .= ' and station_telemetry_param_id is null';
        }

        if ($latestObject->stationTelemetryUnitId !== null) {
            $sql .= ' and station_telemetry_unit_id = ?';
            $sqlParameters[] = $latestObject->stationTelemetryUnitId;
        } else {
            $sql .= ' and station_telemetry_unit_id is null';
        }

        // if ($latestObject->stationTelemetryEqnsId !== null) {
        // $sql .= ' and station_telemetry_eqns_id = ?';
        // $sqlParameters[] = $latestObject->stationTelemetryEqnsId;
        // } else {
        // $sql .= ' and station_telemetry_eqns_id is null';
        // }

        if ($latestObject->stationTelemetryBitsId !== null) {
            $sql .= ' and station_telemetry_bits_id = ?';
            $sqlParameters[] = $latestObject->stationTelemetryBitsId;
        } else {
            $sql .= ' and station_telemetry_bits_id is null';
        }

        $pdo = PDOConnection::getInstance();
        $stmt = $pdo->prepareAndExec($sql, $sqlParameters);
        $rows = $stmt->fetchAll(PDO::FETCH_ASSOC);

        $sum = 0;
        foreach($rows as $row) {
            $sum += $row['c'];
        }

        return $sum;
    }
}
