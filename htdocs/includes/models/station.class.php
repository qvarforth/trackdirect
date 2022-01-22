<?php

class Station extends Model
{
    public function __construct($id)
    {
        parent::__construct($id);
    }

    /**
     * Returnes likly ham radio callsign
     *
     * @return string
     */
    public function getLiklyHamRadioCallsign()
    {
        if ($this->sourceId == 1 && $this->stationTypeId == 1) {
            $pos = strpos($this->name, '-');
            if ($pos !== false) {
                $callsign = substr($this->name, 0, $pos);
            } else {
                $callsign = $this->name;
            }

            if (strlen($callsign) >= 3 && preg_match('~[0-9]~', substr($callsign, 1, strlen($callsign)-1))) {
                // At least 3 letters and a digit somewhere in the middle
                return $callsign;
            }
        }

        return null;
    }


    /**
     * Returns OGN sender address
     *
     * @return string
     */
    public function getOgnSenderAddress()
    {
        if (isset($this->latestOgnSenderAddress) && $this->latestOgnSenderAddress != '') {
            return $this->latestOgnSenderAddress;
        }
        return null;
    }

    /**
     * Returns OGN device
     *
     * @return Model
     */
    public function getOgnDevice()
    {
        static $cache = array();
        $key = $this->id;
        if (!isset($cache[$key])) {
            if (isset($this->latestOgnSenderAddress) && $this->latestOgnSenderAddress != '') {
                $cache[$key] = ModelRepository::getInstance()->getObjectFromSql('select * from ogn_device where device_id = ?', [$this->latestOgnSenderAddress]);
            } else {
                $cache[$key] = null;
            }
        }
        return $cache[$key];
    }

    /**
     * Returns OGN device DB aircraft type name
     *
     * @return string
     */
    public function getOgnDdbAircraftTypeName()
    {
        $ognDevice = $this->getOgnDevice();
        if ($ognDevice) {
             switch ($ognDevice->ddbAircraftType) {
            case 1:
                return 'Glider/Motoglider';
            case 2:
                return 'Plane';
            case 3:
                return 'Ultralight';
            case 4:
                return 'Helicopter';
            case 5:
                return 'Drone/UAV';
            case 6:
                return 'Other';
             }
        }
        return null;
    }

    /**
     * Returns OGN aircraft type name
     *
     * @return string
     */
    public function getOgnAircraftTypeName()
    {
        if (isset($this->latestOgnAircraftTypeId) && $this->latestOgnAircraftTypeId != '') {
            switch ($this->latestOgnAircraftTypeId) {
            case 1:
                return 'Glider';
            case 2:
                return 'Tow Plane';
            case 3:
                return 'Helicopter';
            case 4:
                return 'Parachute';
            case 5:
                return 'Drop Plane';
            case 6:
                return 'Hang Glider';
            case 7:
                return 'Para Glider';
            case 8:
                return 'Powered Aircraft';
            case 9:
                return 'Jet Aircraft';
            case 10:
                return 'UFO';
            case 11:
                return 'Balloon';
            case 12:
                return 'Airship';
            case 13:
                return 'UAV';
            case 14:
                return '';
            case 15:
                return 'Static Object';
            }
        }
        return null;
    }

    /**
     * Returns source description
     *
     * @return string
     */
    public function getSourceDescription()
    {
        if (isset($this->sourceId) && $this->sourceId != '') {
            if ($this->sourceId == 1) {
                return '<a target="_blank" rel="nofollow" href="http://www.aprs-is.net/">APRS-IS</a>';
            } elseif ($this->sourceId == 2) {
                return '<a target="_blank" rel="nofollow" href="http://wxqa.com/">CWOP (Citizen Weather Observer Program)</a>';
            } elseif ($this->sourceId == 5) {
                return '<a target="_blank" rel="nofollow" href="http://wiki.glidernet.org/">OGN (Open Glider Network)</a>';
            }
        }
        return null;
    }

    /**
     * Get distance between specified lat/lng and the station latest position (confirmed position if exists)
     *
     * @param  float $lat
     * @param  float $lng
     * @return int;
     */
    public function getDistance($lat, $lng)
    {
        static $cache = array();
        $key = $this->id . ':' . $lat . ':' . $lng;
        if (!isset($cache[$key])) {

            $latestLatitude = null;
            $latestLongitude = null;
            if ($this->latestConfirmedLongitude !== null && $this->latestConfirmedLatitude !== null) {
                $latestLatitude = $this->latestConfirmedLatitude;
                $latestLongitude = $this->latestConfirmedLongitude;
            } else if ($this->latestLongitude !== null && $this->latestLatitude !== null) {
                $latestLatitude = $this->latestLatitude;
                $latestLongitude = $this->latestLongitude;
            }

            if ($lat !== null && $lng !== null && $latestLatitude !== null && $latestLongitude !== null) {
                $theta = $lng - $latestLongitude;
                $dist = sin(deg2rad($lat)) * sin(deg2rad($latestLatitude)) +  cos(deg2rad($lat)) * cos(deg2rad($latestLatitude)) * cos(deg2rad($theta));
                $dist = acos($dist);
                $dist = rad2deg($dist);
                $miles = $dist * 60 * 1.1515;
                $cache[$key] = round($miles * 1609.344, 0);
            } else {
                $cache[$key] = null;
            }
        }
        return $cache[$key];
    }

    /**
     * Returnes icon http path
     *
     * @param  int $scaleWidth
     * @param  int $scaleHeight
     * @return string
     */
    public function getIconFilePath($scaleWidth = null, $scaleHeight = null)
    {
        if (strlen($this->latestConfirmedSymbol) >= 1 && strlen($this->latestConfirmedSymbolTable) >= 1) {
            $symbolAsciiValue = ord(substr($this->latestConfirmedSymbol, 0, 1));
            $symbolTableAsciiValue = ord(substr($this->latestConfirmedSymbolTable, 0, 1));
        } else {
            // Default values
            $symbolAsciiValue = 125;
            $symbolTableAsciiValue = 47;
        }

        $scaleStrValue = '';
        if ($scaleWidth !== null && $scaleHeight !== null) {
            $scaleStrValue = '-scale' . $scaleWidth . 'x' . $scaleHeight;
        }

        return '/symbols/symbol-' . $symbolAsciiValue . '-' . $symbolTableAsciiValue . $scaleStrValue . '.png';
    }

    /**
     * Get array of the latest used symbols for this station
     *
     * @param  int $scaleWidth
     * @param  int $scaleHeight
     * @return array
     */
    public function getLatestIconFilePaths($scaleWidth = 24, $scaleHeight = 24)
    {
        $result = Array();
        if ($this->latestConfirmedPacketTimestamp > (time() - (60*60*24))) {
            // Latest packet is not that old, go on

            $scaleStrValue = '';
            if ($scaleWidth !== null && $scaleHeight !== null) {
                $scaleStrValue = '-scale' . $scaleWidth . 'x' . $scaleHeight;
            }

            $sql = 'select symbol, symbol_table from packet where station_id = ? and timestamp > ? group by symbol, symbol_table';
            $stmt = PDOConnection::getInstance()->prepareAndExec($sql, [$this->id, $this->latestConfirmedPacketTimestamp - (60*60*24)]);

            $records = $stmt->fetchAll(PDO::FETCH_ASSOC);
            foreach ($records as $record) {

                if (strlen($record['symbol']) >= 1 && strlen($record['symbol_table']) >= 1) {
                    $key = $record['symbol'] . ':' . $record['symbol_table'];

                    $symbolAsciiValue = ord(substr($record['symbol'], 0, 1));
                    $symbolTableAsciiValue = ord(substr($record['symbol_table'], 0, 1));
                    $result[$key] = '/symbols/symbol-' . $symbolAsciiValue . '-' . $symbolTableAsciiValue . $scaleStrValue . '.png';
                }
            }
        }

        return array_values($result);
    }

    /**
     * Get packet frequency in number of seconds for the latest 10 packets
     *
     * @param  string $date
     * @param  int    &$numberOfPackets
     * @return int
     */
    public function getPacketFrequency($date = null, &$numberOfPackets)
    {
        $pdo = PDOConnection::getInstance();
        if ($this->latestPacketTimestamp !== null) {
            $timestamp = $this->latestPacketTimestamp;
        } else {
            return null;
        }

        // Find start timestamp
        $sql = 'select timestamp ts from packet where station_id = ? and map_id in (1,2,5,7,9) and timestamp < ? order by timestamp desc limit 1';
        $stmt = $pdo->prepareAndExec($sql, [$this->id, $timestamp - 1]);

        $record = $stmt->fetch(PDO::FETCH_ASSOC);
        if (!empty($record) && $record['ts'] != null && $record['ts'] < $timestamp) {
            $startTimestamp = $timestamp - (($timestamp - $record['ts'])*10);
            if ($timestamp - $startTimestamp < 600) {
                $startTimestamp = $timestamp - 600;
            }
        } else {
            if ($date === null) {
                // Try to find frequency for the date before
                $date = strftime('%Y-%m-%d', $timestamp - 86400);
                return $this->getPacketFrequency($date, $numberOfPackets);
            } else {
                // Give up
                return null;
            }
        }

        $sql = 'select (max(timestamp) - min(timestamp)) / count(*) freq, count(*) c from packet  where station_id = ? and map_id in (1,2,5,7,9) and timestamp >= ?';
        $stmt = $pdo->prepareAndExec($sql, [$this->id, $startTimestamp]);
        $record = $stmt->fetch(PDO::FETCH_ASSOC);
        if (!empty($record) && $record['freq'] > 0) {
            $numberOfPackets = $record['c'];
            return $record['freq'];
        } else {
            return null;
        }
    }

    /*
     * Returnes symbol description
     * @param boolean $includeUndefinedOverlay
     * @return string
     */
    public function getLatestSymbolDescription($includeUndefinedOverlay = true)
    {
        $symbol = null;
        $symbolTable = null;

        if (strlen($this->latestConfirmedSymbol) >= 1 && strlen($this->latestConfirmedSymbolTable) >= 1) {
            $symbol = $this->latestConfirmedSymbol;
            $symbolTable = $this->latestConfirmedSymbolTable;
        }

        return getSymbolDescription($symbolTable, $symbol, $includeUndefinedOverlay);
    }
}
