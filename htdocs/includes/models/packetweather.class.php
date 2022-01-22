<?php

class PacketWeather extends Model
{
    public function __construct($id)
    {
        parent::__construct($id);

    }

    /**
     * Returnes a rain summary string
     *
     * @param  boolean $showRain1h
     * @param  boolean $showRain24h
     * @param  boolean $showRainSinceMidnight
     * @return string
     */
    public function getRainSummary($showRain1h = true, $showRain24h = true, $showRainSinceMidnight = true)
    {
        $result = $this->getRainSummaryList($showRain1h, $showRain24h, $showRainSinceMidnight);

        if (empty($result)) {
            if ($this->rain_1h === null && $this->rain_24h === null && $this->rain_since_midnight === null) {
                return 'No rain measurements received';
            } else {
                return 'No other rain measurements received';
            }
        } else {
            return implode('&#010;', $result);
        }
    }

    /**
     * Returnes a rain summary array
     *
     * @param  boolean $showRain1h
     * @param  boolean $showRain24h
     * @param  boolean $showRainSinceMidnight
     * @return string
     */
    public function getRainSummaryList($showRain1h = true, $showRain24h = true, $showRainSinceMidnight = true)
    {
        $result = [];

        if ($showRain1h && $this->rain_1h !== null) {
            if (isImperialUnitUser()) {
                $result[] = "Rain latest hour: " . round(convertMmToInch($this->rain_1h), 2) . " in";
            } else {
                $result[] = "Rain latest hour: " . round($this->rain_1h, 2) . " mm";
            }
        }

        if ($showRain24h && $this->rain_24h !== null) {
            if (isImperialUnitUser()) {
                $result[] = "Rain latest 24h hours: " . round(convertMmToInch($this->rain_24h), 2) . " in";
            } else {
                $result[] = "Rain latest 24h hours: " . round($this->rain_24h, 2) . " mm";
            }
        }

        if ($showRainSinceMidnight && $this->rain_since_midnight !== null) {
            if (isImperialUnitUser()) {
                $result[] = "Rain since midnight: " . round(convertMmToInch($this->rain_since_midnight), 2) . " in";
            } else {
                $result[] = "Rain since midnight: " . round($this->rain_since_midnight, 2) . " mm";
            }
        }

        return $result;
    }
}
