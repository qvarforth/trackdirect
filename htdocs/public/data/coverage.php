<?php

require dirname(__DIR__) . "../../includes/bootstrap.php";

$response = [];
$station = StationRepository::getInstance()->getObjectById($_GET['id'] ?? null);
if ($station->isExistingObject()) {
    $response['station_id'] = $station->id;
    $response['coverage'] = [];

    $numberOfHours = 10*24; // latest 10 days should be enough
    $limit = 5000; // Limit number of packets to reduce load on server (and browser)

    if (getWebsiteConfig('coverage_only_moving_senders')) {
        $packetPaths = PacketPathRepository::getInstance()->getLatestMovingDataListByReceivingStationId($_GET['id'] ?? null, $numberOfHours, $limit);
    } else {
        $packetPaths = PacketPathRepository::getInstance()->getLatestDataListByReceivingStationId($_GET['id'] ?? null, $numberOfHours, $limit);
    }


    foreach ($packetPaths as $path) {
        $row = [];
        $row['latitude'] = $path['sending_latitude'];
        $row['longitude'] = $path['sending_longitude'];
        $row['distance'] = $path['distance'];
        $response['coverage'][] = $row;
    }
}

header('Content-type: application/json');
echo json_encode($response);
