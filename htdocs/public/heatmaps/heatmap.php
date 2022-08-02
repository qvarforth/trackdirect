<?php
header('Access-Control-Allow-Origin: *');
header('Cache-Control: max-age=3600, public');
header('Expires: '. gmdate('D, d M Y H:i:s \G\M\T', time() + 3600));
header('Content-type: image/png');

$zoom = $_GET['zoom'] ?? 0;
$x = $_GET['x'] ?? 0;
$y = $_GET['y'] ?? 0;
$filename = 'heatmap.'.$zoom.'.'.$x.'.'.$y.'.png';

if (file_exists($filename) && time()-filemtime($filename) < 3600) {
    // File exists and is not older than 1 hour
    readfile($filename);
    exit;
}

require dirname(__DIR__) . "../../includes/bootstrap.php";
require_once('gd-heatmap/gd_heatmap.php');

$dotRadius = 16;
$tilePixelSize = 256;

$totalMinLat = -85.05115;
$totalMaxLat = 85.05115;
$totalMinLng = -180;
$totalMaxLng = 180;

$totalMinLatPixel = getLatPixelCoordinate($totalMinLat, $zoom, $tilePixelSize);
$totalMaxLatPixel = getLatPixelCoordinate($totalMaxLat, $zoom, $tilePixelSize);
$totalMinLngPixel = getLngPixelCoordinate($totalMinLng, $zoom, $tilePixelSize);
$totalMaxLngPixel = getLngPixelCoordinate($totalMaxLng, $zoom, $tilePixelSize);

$latPartPixelLength = ($totalMinLatPixel / pow(2, $zoom));
$lngPartPixelLength = ($totalMaxLngPixel / pow(2, $zoom));

$minLatPixel = ($x * $latPartPixelLength) + $latPartPixelLength;
$maxLatPixel = ($x * $latPartPixelLength);
$minLngPixel = $totalMinLngPixel + $y * $lngPartPixelLength;
$maxLngPixel = $totalMinLngPixel + (($y * $lngPartPixelLength) + $lngPartPixelLength);

$minLat = getLatFromLatPixelCoordinate($minLatPixel, $zoom, $tilePixelSize);
$maxLat = getLatFromLatPixelCoordinate($maxLatPixel, $zoom, $tilePixelSize);
$minLng = getLngFromLngPixelCoordinate($minLngPixel, $zoom, $tilePixelSize);
$maxLng = getLngFromLngPixelCoordinate($maxLngPixel, $zoom, $tilePixelSize);

$latMarginal = ($maxLat - $minLat) * 0.1;
$lngMarginal = ($maxLng - $minLng) * 0.1;

$sql = "select latest_confirmed_latitude latitude, latest_confirmed_longitude longitude
    from station
    where latest_confirmed_packet_timestamp > ?
        and latest_confirmed_latitude between ? and ?
        and latest_confirmed_longitude between ? and ?";
$parameters = [time() - (3*60*60), $minLat - $latMarginal, $maxLat + $latMarginal, $minLng - $lngMarginal, $maxLng + $lngMarginal];

$pdo = PDOConnection::getInstance();
$stmt = $pdo->prepareAndExec($sql, $parameters);
$rows = $stmt->fetchAll(PDO::FETCH_ASSOC);

$data = [];
foreach($rows as $row) {
    $x = getLngPixelCoordinate($row["longitude"], $zoom, $tilePixelSize) - $minLngPixel - ($dotRadius / 2);
    $y = getLatPixelCoordinate($row["latitude"], $zoom, $tilePixelSize) - $maxLatPixel - ($dotRadius / 2);
    $data[] = [$x, $y, 2];
}

$config = array(
  'debug' => FALSE,
  'width' => 256,
  'height' => 256,
  'noc' =>16,
  'r' => $dotRadius,
  'dither' => FALSE,
  'format' => 'png',
  'fill_with_smallest' => FALSE,
);

$heatmap = new gd_heatmap($data, $config);

if (is_writable(dirname($filename))) {
    $heatmap->output($filename);
    readfile($filename);
} else {
    $heatmap->output();
}
