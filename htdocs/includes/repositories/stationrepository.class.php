<?php

class StationRepository extends ModelRepository
{

    private static $_singletonInstance = null;
    private $_config;

    public function __construct()
    {
        parent::__construct('Station');
        $this->_config = parse_ini_file(ROOT . '/../config/trackdirect.ini', true);
    }

    /**
     * Returnes an initiated StationRepository
     *
     * @return StationRepository
     */
    public static function getInstance()
    {
        if (self::$_singletonInstance === null) {
            self::$_singletonInstance = new StationRepository();
        }

        return self::$_singletonInstance;
    }

    /**
     * Get object by id
     *
     * @param  int $id
     * @return Station
     */
    public function getObjectById($id)
    {
        if (!isInt($id)) {
            return new Station(0);
        }

        static $cache = array();
        $key = $id;
        if (!isset($cache[$key])) {
            $cache[$key] = $this->getObjectFromSql('select * from station where id = ?', [$id]);
        }
        return $cache[$key];
    }

    /**
     * Get object by name
     *
     * @param  string $name
     * @return Station
     */
    public function getObjectByName($name)
    {
        if (!is_string($name)) {
            return new Station(0);
        }

        static $cache = array();
        $key = $name;
        if (!isset($cache[$key])) {
            $cache[$key] = $this->getObjectFromSql('select * from station where name = ? order by latest_location_packet_timestamp desc limit 1', [$name]);
        }
        return $cache[$key];
    }

    /**
     * Get sender station object by sender id
     *
     * @param  string $name
     * @param  int    $senderId
     * @return Station
     */
    public function getSenderStationObjectBySenderId($senderId)
    {
        if (!isInt($senderId)) {
            return new Station(0);
        }

        static $cache = array();
        $key = $senderId;
        if (!isset($cache[$key])) {
            $cache[$key] = $this->getObjectFromSql('select station.* from station, sender where station.latest_sender_id = sender.id and sender.name = station.name and sender.id = ? and station.station_type_id = 1', [$senderId]);
        }
        return $cache[$key];
    }

    /**
     * Get object by name and sender id
     *
     * @param  string $name
     * @param  int    $senderId
     * @return Station
     */
    public function getObjectByNameAndSenderId($name, $senderId)
    {
        if (!is_string($name) || !isInt($senderId)) {
            return new Station(0);
        }

        static $cache = array();
        $key = $name . ';' . $senderId;
        if (!isset($cache[$key])) {
            $cache[$key] = $this->getObjectFromSql('select * from station where name = ? and latest_sender_id = ?', [$name, $senderId]);
        }
        return $cache[$key];
    }


    /**
     * Get object list
     *
     * @param  int   $activeDuringLatestNumberOfSeconds
     * @param  int   $limit
     * @param  int   $offset
     * @return array
     */
    public function getObjectList($activeDuringLatestNumberOfSeconds = (24*60*60), $limit, $offset)
    {
        if ($activeDuringLatestNumberOfSeconds == 0) {
            $activeDuringLatestNumberOfSeconds = time();
        }

        $pdo = PDOConnection::getInstance();
        $stmt = $pdo->prepare(
            'select * from station
            where latest_confirmed_packet_timestamp is not null
                and latest_confirmed_packet_timestamp > ?
                and (source_id != 5 or latest_confirmed_packet_timestamp > ?)
            order by latest_confirmed_packet_timestamp desc
            limit ? offset ?'
        );
        $stmt->bindValue(1, (time() - $activeDuringLatestNumberOfSeconds));
        $stmt->bindValue(2, (time() - (60*60*24))); // OGN data should be deleted after 24h, but just to be safe we avoid including older data when searching
        $stmt->bindValue(3, $limit);
        $stmt->bindValue(4, $offset);

        $stmt->execute();
        $records = $stmt->fetchAll(PDO::FETCH_ASSOC);
        if (is_array($records) && !empty($records)) {
            return $this->_getObjectListFromRecords($records);
        }

        // No object found, return empty array
        return [];
    }

    /**
     * Get number of stations
     *
     * @param  int   $activeDuringLatestNumberOfSeconds
     * @return int
     */
    public function getNumberOfStations($activeDuringLatestNumberOfSeconds = (24*60*60))
    {
        if ($activeDuringLatestNumberOfSeconds == 0) {
            $activeDuringLatestNumberOfSeconds = time();
        }

        $sql = 'select count(*) c from station
            where latest_confirmed_packet_timestamp is not null
                and latest_confirmed_packet_timestamp > ?
                and (source_id != 5 or latest_confirmed_packet_timestamp > ?)';
        $parameters = [(time() - $activeDuringLatestNumberOfSeconds), (time() - (60*60*24))];

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
     * Get object list by query string
     *
     * @param  int   $q
     * @param  int   $activeDuringLatestNumberOfSeconds
     * @param  int   $limit
     * @param  int   $offset
     * @return array
     */
    public function getObjectListByQueryString($q, $activeDuringLatestNumberOfSeconds = (24*60*60), $limit, $offset)
    {
        if (!is_string($q) || !isInt($limit)) {
            return [];
        }

        if ($activeDuringLatestNumberOfSeconds == 0) {
            $activeDuringLatestNumberOfSeconds = time();
        }

        $pdo = PDOConnection::getInstance();
        $stmt = $pdo->prepare('
	    select s.*
            from station s
	        left outer join ogn_device d on d.device_id = s.latest_ogn_sender_address
            where s.latest_confirmed_packet_timestamp is not null
                and s.latest_confirmed_packet_timestamp > ?
                and (s.source_id != 5 or s.latest_confirmed_packet_timestamp > ?)
                and (s.name ilike ? or d.registration ilike ? or d.cn ilike ?)
            order by name
            limit ? offset ?'
        );
        $stmt->bindValue(1, (time() - $activeDuringLatestNumberOfSeconds));
        $stmt->bindValue(2, (time() - (60*60*24))); // OGN data should be deleted after 24h, but just to be safe we avoid including older data when searching
	$stmt->bindValue(3, "$q%");
	$stmt->bindValue(4, "$q%");
	$stmt->bindValue(5, "$q%");
        $stmt->bindValue(6, $limit);
        $stmt->bindValue(7, $offset);

        $stmt->execute();
        $records = $stmt->fetchAll(PDO::FETCH_ASSOC);
        if (is_array($records) && !empty($records)) {
            return $this->_getObjectListFromRecords($records);
        }

        // No object found, return empty array
        return [];
    }

    /**
     * Get number of stations by query string
     *
     * @param  int   $q
     * @param  int   $activeDuringLatestNumberOfSeconds
     * @return int
     */
    public function getNumberOfStationsByQueryString($q, $activeDuringLatestNumberOfSeconds = (24*60*60))
    {
        if (!is_string($q)) {
            return 0;
        }

        if ($activeDuringLatestNumberOfSeconds == 0) {
            $activeDuringLatestNumberOfSeconds = time();
        }

        $sql = 'select count(*) c from station
            where latest_confirmed_packet_timestamp is not null
                and latest_confirmed_packet_timestamp > ?
                and (source_id != 5 or latest_confirmed_packet_timestamp > ?)
                and name ilike ?';
        $parameters = [(time() - $activeDuringLatestNumberOfSeconds), (time() - (60*60*24)), "$q%"];

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
     * Get object list by sender id (close to specified lat/lng)
     *
     * @param  int   $senderId
     * @param  int   $limit
     * @param  float $latitude
     * @param  float $longitude
     * @return array
     */
    public function getObjectListBySenderId($senderId, $limit, $latitude = null, $longitude = null)
    {
        if (!isInt($senderId) || !isFloat($latitude) || !isFloat($longitude) || !isInt($limit)) {
            return [];
        }

        $pdo = PDOConnection::getInstance();

        if ($latitude === null || $longitude === null) {
            $stmt = $pdo->prepare(
                'select * from station
                where latest_confirmed_packet_timestamp is not null
                    and latest_confirmed_packet_timestamp > ?
                    and latest_sender_id = ?
                limit ?'
            );
            $stmt->bindValue(1, (time() - 60*60*24));
            $stmt->bindValue(2, $senderId);
            $stmt->bindValue(3, $limit);
        } else {
            $stmt = $pdo->prepare(
                'select * from station
                where latest_confirmed_packet_timestamp is not null
                    and latest_confirmed_packet_timestamp > ?
                    and latest_sender_id = ?
                order by (abs(latest_confirmed_latitude - ?) + abs(latest_confirmed_longitude - ?))
                limit ?'
            );
            $stmt->bindValue(1, (time() - 60*60*24));
            $stmt->bindValue(2, $senderId);
            $stmt->bindValue(3, $latitude);
            $stmt->bindValue(4, $longitude);
            $stmt->bindValue(5, $limit);
        }
        $stmt->execute();
        $records = $stmt->fetchAll(PDO::FETCH_ASSOC);
        if (is_array($records) && !empty($records)) {
            return $this->_getObjectListFromRecords($records);
        }

        // No object found, return empty array
        return [];
    }

    /**
     * Get related object list by station id (stations with same name but different SSID)
     *
     * @param  int $stationId
     * @param  int $limit
     * @return array
     */
    public function getRelatedObjectListByStationId($stationId, $limit)
    {
        if (!isInt($stationId) || !isInt($limit)) {
            return [];
        }

        $station = $this->getObjectById($stationId);
        $name = $station->name;
        $pos = strrpos($name, '-');
        if ($pos) {
            $call = substr($name, 0, $pos);
        } else {
            // No object found, return empty array
            return [];
        }

        if ($station->latestPacketTimestamp !== null) {
            $time = $station->latestPacketTimestamp;
        } else {
            $time = time();
        }

        $pdo = PDOConnection::getInstance();

        if ($station->latestConfirmedLatitude === null || $station->latestConfirmedLongitude === null) {
            $stmt = $pdo->prepare(
                'select * from station
                where latest_confirmed_packet_timestamp is not null
                    and latest_confirmed_packet_timestamp > ?
                    and name like ?
                limit ?'
            );
            $stmt->bindValue(1, $time - 60*60*24, PDO::PARAM_STR);
            $stmt->bindValue(2, "$call%", PDO::PARAM_STR);
            $stmt->bindValue(3, $limit);
        } else {
            $stmt = $pdo->prepare(
                'select * from station
                where latest_confirmed_packet_timestamp is not null
                    and latest_confirmed_packet_timestamp > ?
                    and name like ?
                order by (abs(latest_confirmed_latitude - ?) + abs(latest_confirmed_longitude - ?))
                limit ?'
            );
            $stmt->bindValue(1, $station->latestPacketTimestamp - 60*60*24, PDO::PARAM_STR);
            $stmt->bindValue(2, "$call%", PDO::PARAM_STR);
            $stmt->bindValue(3, $station->latestConfirmedLatitude);
            $stmt->bindValue(4, $station->latestConfirmedLongitude);
            $stmt->bindValue(5, $limit);
        }
        $stmt->execute();
        $records = $stmt->fetchAll(PDO::FETCH_ASSOC);
        if (is_array($records) && !empty($records)) {
            return $this->_getObjectListFromRecords($records);
        }

        // No object found, return empty array
        return [];
    }

    /**
     * Get object list of stations near specified position
     *
     * @param  int $latitude
     * @param  int $longitude
     * @param  int $maxDistanceInKm
     * @param  int $limit
     * @return array
     */
    public function getCloseByObjectListByPosition($latitude, $longitude, $maxDistanceInKm = 100, $limit = 10000)
    {
        if (!isFloat($latitude) || !isFloat($longitude) || !isInt($maxDistanceInKm) || !isInt($limit)) {
            return [];
        }

        if ($maxDistanceInKm <= 10) {
            // Plus 0.1 should be about 11km
            $minLatitude = $latitude - 0.1;
            $maxLatitude = $latitude + 0.1;
            $minLongitude = $longitude - 0.1;
            $maxLongitude = $longitude + 0.1;
        } else {
            // Plus 1 should be about 111km
            $minLatitude = $latitude - 1;
            $maxLatitude = $latitude + 1;
            $minLongitude = $longitude - 1;
            $maxLongitude = $longitude + 1;
        }

        $minTimestamp = time() - 60*60; // Latest 1h is pretty fast

        // The order by used here is not 100% accurate, but it's fast :-)
        $list = $this->getObjectListFromSql(
            'select * from station
            where latest_confirmed_latitude > ?
                and latest_confirmed_latitude < ?
                and latest_confirmed_longitude > ?
                and latest_confirmed_longitude < ?
                and latest_confirmed_packet_timestamp > ?
            order by (abs(latest_confirmed_latitude - ?) + abs(latest_confirmed_longitude - ?))
            limit ?', [$minLatitude, $maxLatitude, $minLongitude, $maxLongitude, $minTimestamp, $latitude, $longitude, $limit]
        );

        $orderedList = [];
        foreach ($list as $closeByStation) {
            $distance = $closeByStation->getDistance($latitude, $longitude);
            if ($distance !== null && $distance <= ($maxDistanceInKm*1000)) {
                $key = intval($distance);
                while (isset($orderedList[$key])) {
                    $key++;
                }
                $orderedList[$key] = $closeByStation;
            }
        }
        ksort($orderedList);
        return array_values($orderedList);
    }

    /**
     * Get object list of stations near specified station
     *
     * @param  int $stationId
     * @param  int $limit
     * @return array
     */
    public function getCloseByObjectListByStationId($stationId, $limit)
    {
        if (!isInt($stationId) || !isInt($limit)) {
            return [];
        }

        $station = $this->getObjectById($stationId);
        if ($station->latestConfirmedLatitude === null || $station->latestConfirmedLongitude === null) {
            return [];
        }

        $closeByStationList = self::getCloseByObjectListByPosition($station->latestConfirmedLatitude, $station->latestConfirmedLongitude, 100, $limit + 1);
        $result = Array();
        foreach ($closeByStationList as $key => $closeByStation) {
            if ($station->getId() == $closeByStation->getId()) {
                break;
            }
        }
        if (isset($key)) {
            unset($closeByStationList[$key]);
        }
        return $closeByStationList;
    }
}
