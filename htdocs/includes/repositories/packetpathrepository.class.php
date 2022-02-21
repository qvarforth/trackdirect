<?php

class PacketPathRepository extends ModelRepository
{

    private static $_singletonInstance = null;

    public function __construct()
    {
        parent::__construct('PacketPath');
    }

    /**
     * Returnes an initiated PacketPathRepository
     *
     * @return PacketPathRepository
     */
    public static function getInstance()
    {
        if (self::$_singletonInstance === null) {
            self::$_singletonInstance = new PacketPathRepository();
        }

        return self::$_singletonInstance;
    }

    /**
     * Get object by id
     *
     * @param  int $id
     * @return PacketPath
     */
    public function getObjectById($id)
    {
        if (!isInt($packetId)) {
            return new PacketPath(0);
        }
        return $this->getObjectFromSql('select * from packet_path where id = ?', [$id]);
    }

    /**
     * Get object by packet id
     *
     * @param  int $id
     * @return PacketPath
     */
    public function getObjectListByPacketId($id)
    {
        if (!isInt($id)) {
            return [];
        }
        return $this->getObjectListFromSql('select * from packet_path where packet_id = ?', [$id]);
    }

    /**
     * Get packet path statistics for sending station
     *
     * @param  int $stationId
     * @param  int $minTimestamp
     * @return array
     */
    public function getSenderPacketPathSatistics($stationId, $minTimestamp = null)
    {
        if (!isInt($stationId)) {
            return [];
        }
        if ($minTimestamp == null || !isInt($minTimestamp)) {
            $minTimestamp = time() - (60*60*24*10); // Default to 10 days
        }
        $sql = 'select station_id, count(*) number_of_packets, max(timestamp) latest_timestamp, max(distance) longest_distance from packet_path where sending_station_id = ? and timestamp > ? and number = 0 and station_id != sending_station_id group by station_id order by max(timestamp) desc';
        $args = [$stationId, $minTimestamp];
        $pdo = PDOConnection::getInstance();
        $stmt = $pdo->prepareAndExec($sql, $args);
        return $stmt->fetchAll(PDO::FETCH_ASSOC);
    }

    /**
     * Get packet path statistics for receiving station
     *
     * @param  int $stationId
     * @param  int $minTimestamp
     * @return array
     */
    public function getReceiverPacketPathSatistics($stationId, $minTimestamp = null)
    {
        if (!isInt($stationId)) {
            return [];
        }
        if ($minTimestamp == null || !isInt($minTimestamp)) {
            $minTimestamp = time() - (60*60*24*10); // Default to 10 days
        }
        $sql = 'select sending_station_id station_id, count(*) number_of_packets, max(timestamp) latest_timestamp, max(distance) longest_distance from packet_path where station_id = ? and timestamp > ? and number = 0 and station_id != sending_station_id group by sending_station_id order by max(timestamp) desc';
        $args = [$stationId, $minTimestamp];
        $pdo = PDOConnection::getInstance();
        $stmt = $pdo->prepareAndExec($sql, $args);
        return $stmt->fetchAll(PDO::FETCH_ASSOC);
    }

    /**
     * Get latest data list by receiving station id
     *
     * @param  int     $stationId
     * @param  int     $hours
     * @param  int     $limit
     * @return array
     */
    public function getLatestDataListByReceivingStationId($stationId, $hours, $limit)
    {
        if (!isInt($stationId) || !isInt($hours)) {
            return [];
        }
        $minTimestamp = time() - (60*60*$hours);

        $sql = 'select pp.*
            from packet_path pp
            where pp.station_id = ?
                and pp.timestamp >= ?
                and pp.number = 0
                and pp.sending_latitude is not null
                and pp.sending_longitude is not null
            order by pp.timestamp
            limit ?';

        $arg = [$stationId, $minTimestamp, $limit];

        $pdo = PDOConnection::getInstance();
        $stmt = $pdo->prepareAndExec($sql, $arg);
        return $stmt->fetchAll(PDO::FETCH_ASSOC);
    }

    /**
     * Get latest data list by receiving station id (will try to exclude stationary sending stations)
     *
     * @param  int     $stationId
     * @param  int     $hours
     * @param  int     $limit
     * @return array
     */
    public function getLatestMovingDataListByReceivingStationId($stationId, $hours, $limit)
    {
        if (!isInt($stationId) || !isInt($hours)) {
            return [];
        }
        $minTimestamp = time() - (60*60*$hours);

        $sql = 'select pp.*
            from packet_path pp
                join station s on s.id = pp.sending_station_id
            where pp.station_id = ?
                and pp.timestamp >= ?
                and pp.number = 0
                and pp.sending_latitude is not null
                and pp.sending_longitude is not null
                and pp.sending_latitude != s.latest_confirmed_latitude
                and pp.sending_longitude != s.latest_confirmed_longitude
            order by pp.timestamp
            limit ?';

        $arg = [$stationId, $minTimestamp, $limit];

        $pdo = PDOConnection::getInstance();
        $stmt = $pdo->prepareAndExec($sql, $arg);
        return $stmt->fetchAll(PDO::FETCH_ASSOC);
    }
}
