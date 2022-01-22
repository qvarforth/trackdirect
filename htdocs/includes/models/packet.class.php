<?php

class Packet extends Model
{

    public function __construct($id)
    {
        parent::__construct($id);
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
        if (strlen($this->symbol) >= 1 && strlen($this->symbolTable) >= 1) {
            $symbolAsciiValue = ord(substr($this->symbol, 0, 1));
            $symbolTableAsciiValue = ord(substr($this->symbolTable, 0, 1));
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
     * Get PGH range in meters
     *
     * @return float
     */
    public function getPHGRange()
    {
        if ($this->getPhg() != null) {
            $p = $this->getPhgPower();
            $h = $this->getPhgHaat(false);
            $g = $this->getPhgGain();

            $gain = pow(10, ($g/10)); //converts from DB to decimal
            $range = sqrt(2 * $h * sqrt(($p / 10) * ($gain / 2)));
            return $range / 0.000621371192; // convert to m and return
        }
        return null;
    }

    /**
     * Get PGH description
     *
     * @return String
     */
    public function getPHGDescription()
    {
        if ($this->getPhg() != null) {
            $power = $this->getPhgPower();
            $haat = $this->getPhgHaat();
            $gain = $this->getPhgGain();
            $direction = $this->getPhgDirection();
            $range = $this->getPHGRange();

            $description = '';
            if ($power !== null) {
                $description .= 'Power ' . $power . ' W';
            }

            if ($haat !== null) {

                if (strlen($description) > 0) {
                    $description .= ', ';
                }

                if (isImperialUnitUser()) {
                    $description .= 'Height ' . round(convertMeterToFeet($haat), 0) . ' ft';
                } else {
                    $description .= 'Height ' . $haat . ' m';
                }
            }

            if ($gain !== null && $direction !== null) {
                if (strlen($description) > 0) {
                    $description .= ', ';
                }
                $description .= 'Gain ' . $gain . ' dB ' . $direction;
            }

            return $description;
        }
        return null;
    }

    /**
     * Get PGH string
     *
     * @return string
     */
    public function getPhg()
    {
        if ($this->phg != null) {
            if ($this->phg == 0) {
                return null; // 0000 is considered not to be used (power == 0!)
            } else if ($this->phg < 10) {
                return '000' + strval($this->phg);
            }  else if ($this->phg < 100) {
                return '00' + strval($this->phg);
            } else if ($this->phg < 1000) {
                return '0' + strval($this->phg);
            } else {
                return strval($this->phg);
            }
        }
        return null;
    }

    /**
     *  Get PGH power
     *
     * @return int
     */
    public function getPhgPower()
    {
        if ($this->getPhg() != null) {
            return pow(intval(substr($this->getPhg(), 0, 1)), 2);
        }
        return null;
    }

    /**
     * Get PGH hight (above averange terrain)
     *
     * @param  boolean $inMeters
     * @return int
     */
    public function getPhgHaat($inMeters = true)
    {
        if ($this->getPhg() != null) {
            $value = intval(substr($this->getPhg(), 1, 1));

            $haat = 0;
            if ($value != 0) {
                $haat = 10 * pow(2, $value);
            }

            if ($inMeters) {
                return intval(round($haat * 0.3048));
            } else {
                return $haat;
            }

        }
        return null;
    }

    /**
     *  Get PGH Gain
     *
     * @return int
     */
    public function getPhgGain()
    {
        if ($this->getPhg() != null) {
            return intval(substr($this->getPhg(), 2, 1));
        }
        return null;
    }

    /**
     * Get PGH Direction
     *
     * @return String
     */
    public function getPhgDirection()
    {
        if ($this->getPhg() != null) {

            switch (substr($this->getPhg(), 3, 1)) {
            case 0:
                return 'omni';
                    break;
            case 1:
                return 'North East';
                    break;
            case 2:
                return 'East';
                    break;
            case 3:
                return 'South East';
                    break;
            case 4:
                return 'South';
                    break;
            case 5:
                return 'South West';
                    break;
            case 6:
                return 'West';
                    break;
            case 7:
                return 'North West';
                    break;
            case 8:
                return 'North';
                    break;
            case 9:
                return null;
                    break;
            }
        }
        return null;
    }

    /**
     * Get PGH Direction Degree
     *
     * @return int
     */
    public function getPhgDirectionDegree()
    {
        if ($this->getPhg() != null) {

            switch (substr($this->getPhg(), 3, 1)) {
            case 0:
                return null;
                    break;
            case 1:
                return 45;
                    break;
            case 2:
                return 90;
                    break;
            case 3:
                return 135;
                    break;
            case 4:
                return 180;
                    break;
            case 5:
                return 225;
                    break;
            case 6:
                return 270;
                    break;
            case 7:
                return 315;
                    break;
            case 8:
                return 360;
                    break;
            case 9:
                return null;
                    break;
            }
        }
        return null;
    }

    /**
     * Get RNG
     *
     * @return float
     */
    public function getRng()
    {
        if ($this->rng != null) {
            return $this->rng;
        }
        return null;
    }

    /**
     * Get packet type description
     *
     * @return Station
     */
    public function getPacketTypeName()
    {
        switch ($this->packetTypeId) {
        case 1:
            return 'Position';
                break;
        case 2:
            return 'Direction';
                break;
        case 3:
            return 'Weather';
                break;
        case 4:
            return 'Object';
                break;
        case 5:
            return 'Item';
                break;
        case 6:
            return 'Telemetry';
                break;
        case 7:
            return 'Message';
                break;
        case 8:
            return 'Query';
                break;
        case 9:
            return 'Response';
                break;
        case 10:
            return 'Status';
                break;
        case 11:
            return 'Other';
                break;
        default:
            return 'Unknown';
                break;
        }
    }

    /**
     * Get releted packet weather
     * @return PacketWeather
     */
    public function getPacketWeather() {
        return PacketWeatherRepository::getInstance()->getObjectByPacketId($this->id, $this->timestamp);
    }

    /**
     * Get releted packet telemetry
     * @return PacketTelemetry
     */
    public function getPacketTelemetry() {
        return PacketTelemetryRepository::getInstance()->getObjectByPacketId($this->id, $this->timestamp);
    }

    /**
     * Returns OGN part of packet
     *
     * @return PacketOgn
     */
    public function getPacketOgn()
    {
        static $cache = array();
        $key = $this->id;
        if (!isset($cache[$key])) {
            if ($this->sourceId == 5) {
                $cache[$key] = PacketOgnRepository::getInstance()->getObjectByPacketId($this->id);
            } else {
                $cache[$key] = new PacketOgn(null);
            }
        }
        return $cache[$key];
    }

    /**
     * Get Station
     * @return Station
     */
    public function getStationObject() {
        return StationRepository::getInstance()->getObjectById($this->stationId);
    }

    /**
     * Get Sender
     * @return Sender
     */
    public function getSenderObject() {
        return SenderRepository::getInstance()->getObjectById($this->senderId);
    }
}
