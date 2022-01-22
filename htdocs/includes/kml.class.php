<?php

class Kml {

    private $_class;
    private static $_singletonInstance = null;

    public function __construct($class = 'Kml')
    {
        $this->_class = $class;
    }

    public static function getInstance()
    {
        if (self::$_singletonInstance === null) {
            self::$_singletonInstance = new Kml();
        }

        return self::$_singletonInstance;
    }

    public function getKmlDomDocument($station, $packets, $startTimestamp, $endTimestamp, $color)
    {
        $dom = new DOMDocument('1.0', 'UTF-8');
        $node = $dom->createElementNS('http://earth.google.com/kml/2.2', 'kml');
        $parNode = $dom->appendChild($node);

        $dnode = $dom->createElement('Document');
        $docNode = $parNode->appendChild($dnode);

        if (!empty($packets)) {
            $lastPacket = $packets[count($packets) - 1];
            $makrerStyleNode = $this->getMarkerStyleNode($dom, $lastPacket, $color);
            $docNode->appendChild($makrerStyleNode);

            $folderNode = $dom->createElement('Folder');
            $docNode->appendChild($folderNode);

            $nameNode = $dom->createElement('name', $station->name
                . ' (' . $startTimestamp . ' - ' . $endTimestamp . ')');
            $folderNode->appendChild($nameNode);

            $stationNode = $this->getStationNode($dom, $station, $packets);
            $folderNode->appendChild($stationNode);
        }
        return $dom;
    }

    public function formatKmlContent($kmlContent, $tab="\t", $tabCount = 1)
    {
        $kmlContent = preg_replace('/(>)(<)(\/*)/', "$1\n$2$3", $kmlContent);

        $token = strtok($kmlContent, "\n");
        $result = '';
        $pad = 0;
        $matches = array();

        while ($token !== false)
        {
            $token = trim($token);
            if (preg_match('/.+<\/\w[^>]*>$/', $token, $matches)) $indent=0;
            elseif (preg_match('/^<\/\w/', $token, $matches))
            {
                $pad--;
                if($indent>0) $indent=0;
            }
            elseif (preg_match('/^<\w[^>]*[^\/]>.*$/', $token, $matches))
            {
                $indent=1;
            }
            else $indent = 0;

            $line = str_pad($token, strlen($token)+($pad*$tabCount), $tab, STR_PAD_LEFT);
            $result .= $line."\n";
            $token = strtok("\n");
            $pad += $indent;
        }

        return $result;
    }

    private function getMarkerStyleNode($dom, $packet, $color)
    {
        $styleNode = $dom->createElement('Style');
        $styleNode->setAttribute('id', 'markerStyle' . $packet->stationId);

        $iconstyleNode = $dom->createElement('IconStyle');
        $iconNode = $dom->createElement('Icon');
        $href = $dom->createElement('href', $this->getWebsiteURL() . $packet->getIconFilePath(null, null, true));
        $iconNode->appendChild($href);
        $iconstyleNode->appendChild($iconNode);
        $styleNode->appendChild($iconstyleNode);

        $linestyleNode = $dom->createElement('LineStyle');

        if (preg_match('/^[A-F0-9]{8}$/', $color)) {
            $colorNode = $dom->createElement('color', $color);
            $linestyleNode->appendChild($colorNode);
        } else {
            $colorNode = $dom->createElement('color', 'ff55ff55');
            $linestyleNode->appendChild($colorNode);
        }

        $widthNode = $dom->createElement('width', '5');
        $linestyleNode->appendChild($widthNode);
        $styleNode->appendChild($linestyleNode);

        return $styleNode;
    }

    private function getStationNode($dom, $station, $packets) {
        $lastPacket = $packets[count($packets) - 1];

        $placeNode = $dom->createElement('Placemark');
        $placeNode->setAttribute('id', 'station-' . $station->getId());
        $styleUrl = $dom->createElement('styleUrl', '#markerStyle' . $station->getId());
        $placeNode->appendChild($styleUrl);

        $nameNode = $dom->createElement('name', htmlspecialchars($station->name));
        $placeNode->appendChild($nameNode);

        $description = $this->getPacketNodeDescription($station, $packets);
        if ($description !== null) {
            $node = $dom->createElement('description', ($description));
            $placeNode->appendChild($node);
        }

        $multiGeometryNode = $this->getMultiGeometryNode($dom, $station, $packets);
        $placeNode->appendChild($multiGeometryNode);

        return $placeNode;
    }

    private function getMultiGeometryNode($dom, $station, $packets) {
        $lastPacket = $packets[count($packets) - 1];

        $multiGeometryNode = $dom->createElement('MultiGeometry');

        $altitudeMode = 'clampToGround';
        if ($this->isFlyingObject($station, $packets)) {
            $altitudeMode = 'absolute';
        }

        $pointNode = $this->getPacketPointNode($dom, $lastPacket, $altitudeMode);
        $multiGeometryNode->appendChild($pointNode);

        if (count($packets) > 1) {
            $tailLineNode = $this->getTailLineNode($dom, $packets, $altitudeMode);
            $multiGeometryNode->appendChild($tailLineNode);
        }

        return $multiGeometryNode;
    }

    private function getPacketPointNode($dom, $packet, $altitudeMode)
    {
        $pointNode = $dom->createElement('Point');

        // Creates a coordinates element and gives it the value of the lng and lat columns from the results.
        if ($packet->altitude !== null) {
            $coorStr = round($packet->longitude, 5) . ','  . round($packet->latitude, 5) . ',' . round($packet->altitude, 2);
        } else {
            $coorStr = round($packet->longitude, 5) . ','  . round($packet->latitude, 5);
        }

        $altitudeModeNode = $dom->createElement('altitudeMode', $altitudeMode);
        $pointNode->appendChild($altitudeModeNode);

        $coorNode = $dom->createElement('coordinates', $coorStr);
        $pointNode->appendChild($coorNode);
        return $pointNode;
    }

    private function getTailLineNode($dom, $packets, $altitudeMode)
    {
        $lineStringNode = $dom->createElement('LineString');

        $lineCoorStr = '';
        foreach ($packets as $packet) {
            if ($packet->altitude !== null) {
                $lineCoorStr .= ' ' . round($packet->longitude, 5) . ','  . round($packet->latitude, 5) . ',' . round($packet->altitude, 2);
            } else {
                $lineCoorStr .= ' ' . round($packet->longitude, 5) . ','  . round($packet->latitude, 5);
            }
        }

        $altitudeModeNode = $dom->createElement('altitudeMode', $altitudeMode);
        $lineStringNode->appendChild($altitudeModeNode);

        $tessellateNode = $dom->createElement('tessellate', '1');
        $lineStringNode->appendChild($tessellateNode);

        $extrudeNode = $dom->createElement('extrude', '1');
        $lineStringNode->appendChild($extrudeNode);

        $lineCoorNode = $dom->createElement('coordinates', $lineCoorStr);
        $lineStringNode->appendChild($lineCoorNode);

        return $lineStringNode;
    }

    private function getPacketNodeDescription($station, $packets)
    {
        $description = array();
        $description[] = '<a href="' . $this->getWebsiteURL() . '?sid=' . $station->getId() . '" target="_blank">Track ' . $station->name . '</a>';

        if (!empty($packets)) {
            $firstPacket = $packets[0];
            $lastPacket = $packets[count($packets) - 1];

            $description[] = '';
            if (count($packets) == 1) {
                $description[] = '<span style="color: grey;">' . strftime('%F %T %Z',$lastPacket->timestamp) . '</span>';
            } else {
                $description[] = '<span style="color: grey;">' . strftime('%F %T %Z',$firstPacket->timestamp) . ' -<br>' . strftime('%F %T %Z',$lastPacket->timestamp) . '</span>';
            }

            if ($lastPacket->comment != null) {
                $description[] = '';
                $description[] = '<span style="font-style: italic; color: #754D08;">' . htmlspecialchars($lastPacket->comment) . '</span>';
            }

            if ($lastPacket->speed !== null) {
                $description[] = '';
                $description[] = 'Latest speed: <span style="color: blue;">' . $lastPacket->speed . 'kmh' . '</span>';

                if ($lastPacket->altitude !== null) {
                    $description[] = 'Latest altitude: <span style="color: blue;">' . $lastPacket->altitude . 'm ' . '</span>';
                }

                if ($lastPacket->course !== null) {
                    $description[] = 'Latest course: <span style="color: blue;">' . $lastPacket->course . '°' . '</span>';
                }
            }
        }

        return '<div style="margin-right: 45px;">' . implode('<br/>', $description) . '</div>';
    }

    private function isClientRequestingToOften()
    {
        $currentMinuteTs = (time() - (time() % 60));
        $limitedNumberOfRequestsPerMinute = 60;
        $logFile = 'tmp/export_kml_ip_' . $_SERVER['REMOTE_ADDR'] . '_' . $currentMinuteTs;

        // Create dir if missing
        if (!file_exists('tmp')) {
            mkdir('tmp');
        }

        // Delete old log-files
        $files = glob('tmp/*');
        foreach ($files as $file) {
            if (is_file($file) && !stristr($file, '_' . $currentMinuteTs)) {
                unlink($file);
            }
        }

        // Log request
        $log = fopen($logFile, "a");
        fwrite($log,'0');
        fclose($log);

        // Check limit
        if (filesize($logFile) > $limitedNumberOfRequestsPerMinute) {
            return true;
        }

        return false;
    }

    private function isFlyingObject($station, $packets)
    {
        if (count($packets) <= 1) {
            // A station with only one packet is probably stationary
            return false;
        }

        if ($station->sourceId == 4) {
            // All gliderradar stations with a tail is probably flying
            return true;
        }

        foreach ($packets as $packet) {
            if ($packet->altitude !== null && $packet->altitude > 1000) {
                // If altitude is above 1000m it is probably flying
                return true;
            }
        }

        return false;
    }

    private function getWebsiteURL()
    {
        return sprintf(
            "%s://%s",
            isset($_SERVER['HTTPS']) && $_SERVER['HTTPS'] != 'off' ? 'https' : 'http',
            $_SERVER['SERVER_NAME']
        );
    }
}
