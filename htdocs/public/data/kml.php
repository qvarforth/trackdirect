<?php

require dirname(__DIR__) . "../../includes/bootstrap.php";

if (isset($_GET['id']) && isInt($_GET['id'])) {
    $station = StationRepository::getInstance()->getObjectById($_GET['id']);
} else {
    $station = new Station(null);
}

$color = null;
if (isset($_GET['color'])) {
    $color = $_GET['color'];
}

$startTimestamp = time() - (60*60*24); // Default to 24h
if (isset($_GET['startts'])) {
    $startTimestamp = $_GET['startts'];
}
if ($startTimestamp < (time() - (60*60*24*3))) {
    $startTimestamp = time() - (60*60*24*3); // Not older than 3 days allowed
}

$endTimestamp = time();
if (isset($_GET['endts']) && isInt($_GET['endts'])) {
    $endTimestamp = $_GET['endts'];
}

$startTimestampString = strftime('%Y%m%d%H%M', $startTimestamp);
$endTimestampString = strftime('%Y%m%d%H%M', $endTimestamp);

if ($station->isExistingObject()) {
    $stationIds = [];
    if ($station->stationTypeId == 2) {
        $currentStations = StationRepository::getInstance()->getObjectListByName($station->name, 2, $station->sourceId);
        foreach ($currentStations as $currentStation) {
            $stationIds[] = $currentStation->getId();
        }
    } else {
        $stationIds[] = $station->getId();
    }

    $lateststation = null;
    foreach ($stationIds as $stationId) {
        $s = StationRepository::getInstance()->getObjectById($stationId);
        if ($lateststation === null) {
            $lateststation = $s;
        } else if ($lateststation->latestConfirmedPacketTimestamp < $s->latestConfirmedPacketTimestamp) {
            $lateststation = $s;
        }
    }

    $packets = PacketRepository::getInstance()->getConfirmedObjectListByStationIdList($stationIds, $startTimestamp, $endTimestamp);
    $dom = Kml::getInstance()->getKmlDomDocument($lateststation, $packets, $startTimestamp, $endTimestamp, $color);
    $kmlOutput = $dom->saveXML();

    header('Content-type: application/vnd.google-earth.kml+xml');
    header('Content-Disposition: attachment; filename="' . htmlspecialchars($lateststation->name) . '-' . $startTimestampString . '-' . $endTimestampString . '.kml"');
    echo Kml::getInstance()->formatKmlContent($kmlOutput, " ", 4);
}
