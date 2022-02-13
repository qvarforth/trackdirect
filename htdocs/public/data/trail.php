<?php

require dirname(__DIR__) . "../../includes/bootstrap.php";

$response = [];
$station = StationRepository::getInstance()->getObjectById($_GET['id'] ?? null);
if ($station->isExistingObject()) {
    $numberOfHours = $_GET['hours'] ?? 1;

    $columns = ['timestamp'];
    $type = 'speed';
    if ($_GET['type'] == 'speed') {
        $type = 'speed';
        if ($_GET['imperialUnits'] ?? '0' == '1') {
            $response[] = array('Time', 'Speed (mph)');
        } else {
            $response[] = array('Time', 'Speed (kmh)');
        }
    } else {
        $type = 'altitude';
        if ($_GET['imperialUnits'] ?? '0' == '1') {
            $response[] = array('Time', 'Altitude (ft)');
        } else {
            $response[] = array('Time', 'Altitude (m)');
        }
    }
    $columns[] = $type;

    $packets = PacketRepository::getInstance()->getLatestDataListByStationId($_GET['id'] ?? null, $numberOfHours, $columns);
    foreach($packets as $packet) {
        $value = floatval($packet[$type]);
        if ($_GET['imperialUnits'] ?? '0' == '1') {
            if ($type == 'speed') {
                $value = convertKilometerToMile($value);
            } else if ($type == 'altitude') {
                $value = convertMeterToFeet($value);
            }
        }

        if ($type == 'speed' && count($response) > 1) {
            if (isset($response[count($response) - 1])) {
                $prevTimestamp = $response[count($response) - 1][0];
                if ($prevTimestamp < ($packet['timestamp'] - 60*60)) {
                    // Previous value is old, make sure we have a break in graph
                    $response[] = array($prevTimestamp + 1, null);
                }
            }
        }

        $response[] = [$packet['timestamp'], $value];
    }
}

header('Content-type: application/json');
echo json_encode($response);
