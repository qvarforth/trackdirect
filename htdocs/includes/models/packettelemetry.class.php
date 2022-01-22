<?php

class PacketTelemetry extends Model
{

    private $_stationTelemetryParam;
    private $_stationTelemetryEqns;
    private $_stationTelemetryBits;
    private $_stationTelemetryUnit;

    public function __construct($id)
    {
        parent::__construct($id);
        $this->_stationTelemetryParam = null;
        $this->_stationTelemetryEqns = null;
        $this->_stationTelemetryBits = null;
        $this->_stationTelemetryUnit = null;
    }

    /**
     * Get value parameter name
     *
     * @param  int $valNumber
     * @return string
     */
    public function getValueParameterName($valNumber)
    {
        if ($this->_stationTelemetryParam === null && $this->stationTelemetryParamId !== null) {
            $this->_stationTelemetryParam = StationTelemetryParamRepository::getInstance()->getObjectById($this->stationTelemetryParamId);
        }

        if ($this->_stationTelemetryParam !== null
            && $this->_stationTelemetryParam->isExistingObject()
            && isset($this->_stationTelemetryParam->{'p'.$valNumber})
            && $this->_stationTelemetryParam->{'p'.$valNumber} != ''
        ) {

            return $this->_stationTelemetryParam->{'p'.$valNumber};
        } else {
            return "Value$valNumber";
        }
    }

    /**
     * Get bit parameter name
     *
     * @param  int $valNumber
     * @return string
     */
    public function getBitParameterName($valNumber)
    {
        if ($this->_stationTelemetryParam === null && $this->stationTelemetryParamId !== null) {
            $this->_stationTelemetryParam = StationTelemetryParamRepository::getInstance()->getObjectById($this->stationTelemetryParamId);
        }

        if ($this->_stationTelemetryParam !== null && $this->_stationTelemetryParam->isExistingObject() && $this->_stationTelemetryParam->{'b'.$valNumber} != '') {
            return $this->_stationTelemetryParam->{'b'.$valNumber};
        } else {
            return "Bit$valNumber";
        }
    }

    /**
     * Get value eqns
     *
     * @param  int $valNumber
     * @return numeric
     */
    public function getEqnsValue($valNumber)
    {
        if ($this->_stationTelemetryEqns === null && $this->stationTelemetryEqnsId !== null) {
            $this->_stationTelemetryEqns = StationTelemetryEqnsRepository::getInstance()->getObjectById($this->stationTelemetryEqnsId);
        }

        if ($this->_stationTelemetryEqns !== null && $this->_stationTelemetryEqns->isExistingObject()) {
            $a = $this->_stationTelemetryEqns->{'a'.$valNumber};
            $b = $this->_stationTelemetryEqns->{'b'.$valNumber};
            $c = $this->_stationTelemetryEqns->{'c'.$valNumber};

            if ($a === null && $b === null) {
                // User has sent us a faulty eqns, just return raw value
                return Array(0, 1, 0);
            } else {
                if ($a === null) {
                    $a = 0;
                }
                if ($b === null) {
                    $b = 0;
                }
                if ($c === null) {
                    $c = 0;
                }
                return Array($a, $b, $c);
            }

        } else {
            // We have no eqns, just return raw value
            return Array(0, 1, 0);
        }
    }

    /**
     * Check if value is set value
     *
     * @param  int $valNumber
     * @return bool
     */
    public function isValueSet($valNumber)
    {
        $val = $this->{'val'.$valNumber};
        if ($val !== null) {
            return true;
        }
        return false;
    }

    /**
     * Get value
     *
     * @param  int $valNumber
     * @return numeric
     */
    public function getValue($valNumber)
    {
        $val = $this->{'val'.$valNumber};

        $eqns = $this->getEqnsValue($valNumber);
        $a = $eqns[0];
        $b = $eqns[1];
        $c = $eqns[2];

        if ($a == null && $b == null) {
            // User has sent us a faulty eqns, just return raw value
            return $val;

        } else {
            $result = 0;

            if ($a != null) {
                $result += $a * $val * $val;
            }

            if ($b != null) {
                $result += $b * $val;
            }

            if ($c != null) {
                $result += $c;
            }

            return $result;
        }
    }

    /**
     * Get value unit
     *
     * @param  int $valNumber
     * @return string
     */
    public function getValueUnit($valNumber)
    {
        $unit = ''; // default
        if ($this->_stationTelemetryUnit === null && $this->stationTelemetryUnitId !== null) {
            $this->_stationTelemetryUnit = StationTelemetryUnitRepository::getInstance()->getObjectById($this->stationTelemetryUnitId);
        }

        if ($this->_stationTelemetryUnit !== null && $this->_stationTelemetryUnit->isExistingObject()) {
            $unit = ' ' . $this->_stationTelemetryUnit->{'u'.$valNumber};
        }

        return $unit;
    }

    /**
     * Get bit sense
     *
     * @param  int $valNumber
     * @return int
     */
    public function getBitSense($valNumber)
    {
        if ($this->_stationTelemetryBits === null && $this->stationTelemetryBitsId !== null) {
            $this->_stationTelemetryBits = StationTelemetryBitsRepository::getInstance()->getObjectById($this->stationTelemetryBitsId);
        }

        $sense = 1; // default to 1
        if ($this->_stationTelemetryBits !== null && $this->_stationTelemetryBits->isExistingObject()) {
            $sense = substr($this->_stationTelemetryBits->bits, $valNumber-1, 1);
        }

        return $sense;
    }

    /**
     * Get bit
     *
     * @param  int $valNumber
     * @return int
     */
    public function getBit($valNumber)
    {
        if ($this->_stationTelemetryBits === null && $this->stationTelemetryBitsId !== null) {
            $this->_stationTelemetryBits = StationTelemetryBitsRepository::getInstance()->getObjectById($this->stationTelemetryBitsId);
        }

        $sense = $this->getBitSense($valNumber);

        $bit = substr($this->bits, $valNumber-1, 1);
        if (($sense == 1 && $bit == 1) || ($sense == 0 && $bit == 0)) {
            return 1;
        } else {
            return 0;
        }
    }

    /**
     * Get bit label
     *
     * @param  int $valNumber
     * @return int
     */
    public function getBitLabel($valNumber)
    {
        if ($this->_stationTelemetryUnit === null && $this->stationTelemetryUnitId !== null) {
            $this->_stationTelemetryUnit = StationTelemetryUnitRepository::getInstance()->getObjectById($this->stationTelemetryUnitId);
        }

        $label = 'On'; // default
        if ($this->_stationTelemetryUnit !== null && $this->_stationTelemetryUnit->isExistingObject()) {
            $label = $this->_stationTelemetryUnit->{'l'.$valNumber};
        }

        return $label;
    }
}
