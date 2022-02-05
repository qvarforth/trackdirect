<?php

class PacketRepository extends ModelRepository
{

    private static $_singletonInstance = null;

    public function __construct()
    {
        parent::__construct('Packet');
    }

    /**
     * Returnes an initiated PacketRepository
     *
     * @return PacketRepository
     */
    public static function getInstance()
    {
        if (self::$_singletonInstance === null) {
            self::$_singletonInstance = new PacketRepository();
        }

        return self::$_singletonInstance;
    }

    /**
     * Get object by id
     *
     * @param  int $id
     * @param  int $timestamp
     * @return Packet
     */
    public function getObjectById($id, $timestamp)
    {
        if (!isInt($id) || !isInt($timestamp)) {
            return new Packet(0);
        }
        return $this->getObjectFromSql('select * from packet where id = ? and timestamp = ?', [$id, $timestamp]);
    }

    /**
     * Get object list with raw by station id for the latest 24 hours
     *
     * @param  int $stationId
     * @param  int $limit
     * @param  int $offset
     * @return array
     */
    public function getObjectListWithRawByStationId($stationId, $limit, $offset)
    {
        if (!isInt($stationId) || !isInt($limit) || !isInt($offset)) {
            return [];
        }
        $sql = 'select packet.* from packet packet where station_id = ? and timestamp > ? and raw is not null order by timestamp desc, id desc limit ? offset ?';
        $parameters = [$stationId, time() - (24*60*60), $limit, $offset];
        return $this->getObjectListFromSql($sql, $parameters);
    }

    /**
     * Get number of packets with raw by station id for the latest 24 hours
     *
     * @param  int $stationId
     * @return int
     */
    public function getNumberOfPacketsWithRawByStationId($stationId)
    {
        if (!isInt($stationId)) {
            return 0;
        }
        $sql = 'select count(*) c from packet where station_id = ? and timestamp > ? and raw is not null';
        $parameters = [$stationId, time() - (24*60*60)];

        $pdo = PDOConnection::getInstance();
        $stmt = $pdo->prepareAndExec($sql, $parameters);
        $rows = $stmt->fetchAll(PDO::FETCH_ASSOC);

        $sum = 0;
        foreach($rows as $row) {
            $sum += $row['c'];
        }

        return $sum;
    }

    /**
     * Get object list with raw by sender station id for the latest 24 hours
     *
     * @param  int $stationId
     * @param  int $limit
     * @param  int $offset
     * @return array
     */
    public function getObjectListWithRawBySenderStationId($stationId, $limit, $offset)
    {
        if (!isInt($stationId) || !isInt($limit) || !isInt($offset)) {
            return [];
        }
        $sql = 'select packet.* from packet where sender_id in (select latest_sender_id from station where id = ?) and timestamp > ? and raw is not null order by timestamp desc, id desc limit ? offset ?';
        $parameters = [$stationId, time() - (24*60*60), $limit, $offset];
        return $this->getObjectListFromSql($sql, $parameters);
    }

    /**
     * Get number of packets with raw by sender station id for the latest 24 hours
     *
     * @param  int $stationId
     * @return int
     */
    public function getNumberOfPacketsWithRawBySenderStationId($stationId)
    {
        if (!isInt($stationId)) {
            return 0;
        }
        $sql = 'select count(*) c from packet where sender_id in (select latest_sender_id from station where id = ?) and timestamp > ? and raw is not null';
        $parameters = [$stationId, time() - (24*60*60)];

        $pdo = PDOConnection::getInstance();
        $stmt = $pdo->prepareAndExec($sql, $parameters);
        $rows = $stmt->fetchAll(PDO::FETCH_ASSOC);

        $sum = 0;
        foreach($rows as $row) {
            $sum += $row['c'];
        }
        return $sum;
    }

    /**
     * Get latest confirmed position packet object by station id
     *
     * @param  int $stationId
     * @return Packet
     */
    public function getLatestConfirmedObjectByStationId($stationId)
    {
        if (!isInt($stationId)) {
            return new Packet(0);
        }
        $station = StationRepository::getInstance()->getObjectById($stationId);
        if ($station->isExistingObject()) {
            return $this->getObjectById($station->latestConfirmedPacketId, $station->latestConfirmedPacketTimestamp);
        }
        return new Packet(null);
    }

    /**
     * Get latest packet data list by station id  (useful for creating a chart)
     *
     * @param  int   $stationId
     * @param  int   $numberOfHours
     * @param  array $columns
     * @return Array
     */
    public function getLatestDataListByStationId($stationId, $numberOfHours, $columns)
    {
        $result = Array();
        if (!isInt($stationId) || !isInt($numberOfHours)) {
            return $result;
        }

        if (!in_array('timestamp', $columns)) {
            // Just to be sure
            $columns[] = 'timestamp';
        }

        $startTimestamp = time() - $numberOfHours*60*60;
        $sql = 'select ' . implode(',', $columns) . ', position_timestamp from packet
            where station_id = ?
                and timestamp >= ?
                and (speed is not null or altitude is not null)
                and map_id in (1,12,5,7,9)
            order by timestamp';
        $arg = [$stationId, $startTimestamp];

        $pdo = PDOConnection::getInstance();
        $stmt = $pdo->prepareAndExec($sql, $arg);
        $records = $stmt->fetchAll(PDO::FETCH_ASSOC);
        foreach ($records as $record) {

            // Add value for position start if position start is within interval
            if ($record['position_timestamp'] != null && $record['position_timestamp'] < $record['timestamp'] && $record['position_timestamp'] >= $startTimestamp) {
                $posRecord = $record;
                $posRecord['timestamp'] = $posRecord['position_timestamp'];
                unset($posRecord['position_timestamp']);
                $result[] = $posRecord;
            }

            // Add value from found packet
            unset($record['position_timestamp']);
            $result[] = $record;
        }

        return $result;
    }

    /**
     * Get object list (only confirmed)
     * @param array $stationIdList
     * @param int $startTimestamp
     * @param int $endTimestamp
     * @return array
     */
    public function getConfirmedObjectListByStationIdList($stationIdList, $startTimestamp, $endTimestamp) {
        if (!isInt($startTimestamp) || !isInt($endTimestamp)) {
            return $result;
        }

        $sql = 'select * from packet where station_id in (' . implode(',', $stationIdList) . ') and timestamp > ? and timestamp < ? and map_id = 1 order by timestamp';
        $parameters = [$startTimestamp, $endTimestamp];
        return $this->getObjectListFromSql($sql, $parameters);
    }
}
