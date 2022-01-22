<?php require "../../includes/bootstrap.php"; ?>

<?php $station = StationRepository::getInstance()->getObjectById($_GET['id']); ?>
<?php if ($station->isExistingObject()) : ?>

    <?php
        $page = $_GET['page'] ?? 1;
        $rows = $_GET['rows'] ?? 25;
        $offset = ($page - 1) * $rows;

        if (($_GET['category'] ?? 1) == 2) {
            $packets = PacketRepository::getInstance()->getObjectListWithRawBySenderStationId($station->id, $rows, $offset);
            $count = PacketRepository::getInstance()->getNumberOfPacketsWithRawBySenderStationId($station->id);
        } else {
            $packets = PacketRepository::getInstance()->getObjectListWithRawByStationId($station->id, $rows, $offset);
            $count = PacketRepository::getInstance()->getNumberOfPacketsWithRawByStationId($station->id);
        }

        $pages = ceil($count / $rows);
    ?>

    <!DOCTYPE html>
    <html lang="en">
        <head>
            <meta charset="utf-8" />
            <title><?php echo $station->name; ?> Raw Packets</title>
            <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=0"/>
            <meta name="apple-mobile-web-app-capable" content="yes"/>
            <meta name="mobile-web-app-capable" content="yes">

            <script src="https://cdnjs.cloudflare.com/ajax/libs/jquery/1.12.4/jquery.min.js" integrity="sha512-jGsMH83oKe9asCpkOVkBnUrDDTp8wl+adkB2D+//JtlxO4SrLoJdhbOysIFQJloQFD+C4Fl1rMsQZF76JjV0eQ==" crossorigin="anonymous"></script>
            <script src="https://cdnjs.cloudflare.com/ajax/libs/moment.js/2.29.1/moment-with-locales.min.js" integrity="sha512-LGXaggshOkD/at6PFNcp2V2unf9LzFq6LE+sChH7ceMTDP0g2kn6Vxwgg7wkPP7AAtX+lmPqPdxB47A0Nz0cMQ==" crossorigin="anonymous"></script>
            <script src="https://cdnjs.cloudflare.com/ajax/libs/autolinker/3.14.2/Autolinker.min.js" integrity="sha512-qyoXjTIJ69k6Ik7CxNVKFAsAibo8vW/s3WV3mBzvXz6Gq0yGup/UsdZBDqFwkRuevQaF2g7qhD3E4Fs+OwS4hw==" crossorigin="anonymous"></script>

            <link rel="stylesheet" href="/css/main.css">

            <script>
                $(document).ready(function() {
                    var locale = window.navigator.userLanguage || window.navigator.language;
                    moment.locale(locale);

                    $('.raw-packet-timestamp').each(function() {
                        if ($(this).html().trim() != '' && !isNaN($(this).html().trim())) {
                            $(this).html(moment(new Date(1000 * $(this).html())).format('L LTSZ'));
                        }
                    });

                    $('#raw-category').change(function () {
                        location.href = "/station/raw.php?id=<?php echo $station->id ?>&type=" + $('#raw-type').val() + "&category=" + $('#raw-category').val() + "&rows=" + $('#raw-rows').val() + "&page=1";
                    });

                    $('#raw-type').change(function () {
                        location.href = "/station/raw.php?id=<?php echo $station->id ?>&type=" + $('#raw-type').val() + "&category=" + $('#raw-category').val() + "&rows=" + $('#raw-rows').val() + "&page=1";
                    });

                    $('#raw-rows').change(function () {
                        location.href = "/station/raw.php?id=<?php echo $station->id ?>&type=" + $('#raw-type').val() + "&category=" + $('#raw-category').val() + "&rows=" + $('#raw-rows').val() + "&page=1";
                    });

                    $('.pagination a').click(function () {
                        let page = $(this).text();
                        if (page == '<<') {
                            page = 1;
                        } else if (page == '>>') {
                            page = <?php echo $pages; ?>;
                        }
                        if (isNaN(page)) {
                            page = 1;
                        }

                        location.href = "/station/raw.php?id=<?php echo $station->id ?>&type=" + $('#raw-type').val() + "&category=" + $('#raw-category').val() + "&rows=" + $('#raw-rows').val() + "&page=" + page;
                    });

                    if (window.parent && window.parent.trackdirect) {
                        <?php if ($station->latestConfirmedLatitude != null && $station->latestConfirmedLongitude != null) : ?>
                        window.parent.trackdirect.focusOnStation(<?php echo $station->id ?>, true);
                        <?php endif; ?>
                    }
                });
            </script>
        </head>
        <body>
            <div class="modal-inner-content">
                <div class="modal-inner-content-menu">
                    <a title="Overview" href="/station/overview.php?id=<?php echo $station->id ?>&imperialUnits=<?php echo $_GET['imperialUnits'] ?? 0; ?>">Overview</a>
                    <a title="Statistics" href="/station/statistics.php?id=<?php echo $station->id ?>&imperialUnits=<?php echo $_GET['imperialUnits'] ?? 0; ?>">Statistics</a>
                    <a title="Weather" href="/station/weather.php?id=<?php echo $station->id ?>&imperialUnits=<?php echo $_GET['imperialUnits'] ?? 0; ?>">Weather</a>
                    <a title="Telemetry" href="/station/telemetry.php?id=<?php echo $station->id ?>&imperialUnits=<?php echo $_GET['imperialUnits'] ?? 0; ?>">Telemetry</a>
                    <span>Raw packets</span>
                </div>

                <div class="horizontal-line" style="margin-bottom: 15px;">&nbsp;</div>

                <p>
                    This is the latest recevied packets stored in our database for station/object <?php echo $station->name; ?>. If no packets are shown the sender has not sent any packets the latest 24 hours.
                </p>

                <?php if ($station->sourceId == 5) : ?>
                    <p>
                        We do not save raw packets for aircrafts that do not exists in the <a target="_blank" href="http://wiki.glidernet.org/ddb">OGN Devices DataBase</a>. We will only display information that can be used to identify an aircraft if the aircraft device details exists in the OGN Devices DataBase, and if the setting "I don't want this device to be identified" is deactivated.
                    </p>
                <?php else : ?>
                    <p>
                        If you compare the raw packets with similar data from other websites it may differ (especially the path), the reason is that we are not collecting packets from the same APRS-IS servers. Each APRS-IS server performes duplicate filtering, and which packet that is considered to be a duplicate may differ depending on which APRS-IS server you receive your data from.
                    </p>
                <?php endif; ?>

                <div class="form-container">
                    <?php if ($station->stationTypeId == 1) : ?>
                        <select id="raw-category" style="float:left; margin-right: 5px;">
                            <option <?php echo (($_GET['category'] ?? 1) == 1 ? 'selected' : ''); ?> value="1">Packets regarding <?php echo $station->name; ?></option>
                            <option <?php echo (($_GET['category'] ?? 1) == 2 ? 'selected' : ''); ?> value="2">Packets sent by <?php echo $station->name; ?></option>
                        </select>
                    <?php endif; ?>

                    <select id="raw-type" style="float:left; margin-right: 5px;">
                        <option <?php echo (($_GET['type'] ?? 1) == 1 ? 'selected' : ''); ?> value="1">Raw Packets</option>
                        <option <?php echo (($_GET['type'] ?? 1) == 2 ? 'selected' : ''); ?> value="2">Decoded Data</option>
                    </select>

                    <select id="raw-rows" style="float:left; margin-right: 5px;" class="pagination-rows">
                        <option <?php echo ($rows == 25 ? 'selected' : ''); ?> value="25">25 rows</option>
                        <option <?php echo ($rows == 50 ? 'selected' : ''); ?> value="50">50 rows</option>
                        <option <?php echo ($rows == 100 ? 'selected' : ''); ?> value="100">100 rows</option>
                        <option <?php echo ($rows == 200 ? 'selected' : ''); ?> value="200">200 rows</option>
                        <option <?php echo ($rows == 300 ? 'selected' : ''); ?> value="300">300 rows</option>
                    </select>
                </div>

                <?php if ($pages > 1): ?>
                    <div class="pagination">
                      <a href="#"><<</a>
                      <?php for($i = max(1, $page - 3); $i <= min($pages, $page + 3); $i++) : ?>
                      <a href="#" <?php echo ($i == $page ? 'class="active"': '')?>><?php echo $i ?></a>
                      <?php endfor; ?>
                      <a href="#">>></a>
                    </div>
                <?php endif; ?>

                <div id="raw-content-output">
                    <?php foreach (array_slice($packets, 0, $rows) as $packet) : ?>
                        <?php if (($_GET['type'] ?? 1) == 1) : ?>
                            <p>
                                <span class="raw-packet-timestamp"><?php echo $packet->timestamp; ?></span>:

                                <?php if (in_array($packet->mapId, Array(3, 6))) : ?>
                                <span class="raw-packet-error">
                                <?php else : ?>
                                <span>
                                <?php endif; ?>

                                    <?php echo str_replace_first(htmlspecialchars($station->name . '>'), '<b>' . htmlspecialchars($station->name) . '</b>&gt;', htmlspecialchars($packet->raw)); ?>

                                    <?php if ($packet->mapId == 3) : ?>
                                    &nbsp;<b>[Duplicate]</b>
                                    <?php elseif ($packet->mapId == 6) : ?>
                                    &nbsp;<b>[Received in wrong order]</b>
                                    <?php endif; ?>

                                </span>
                            </p>
                        <?php elseif (($_GET['type'] ?? 1) == 2) : ?>
                            <div class="decoded">
                                <div class="datagrid">
                                    <table>
                                        <thead>
                                            <tr>
                                                <th colspan="2">
                                                    <?php if (in_array($packet->mapId, Array(3, 6))) : ?>
                                                    <span class="raw-packet-error">
                                                    <?php else : ?>
                                                    <span>
                                                    <?php endif; ?>
                                                        <span class="raw-packet-timestamp"><?php echo $packet->timestamp; ?></span>

                                                        <?php if ($packet->mapId == 3) : ?>
                                                        &nbsp;<b>[Duplicate]</b>
                                                        <?php elseif ($packet->mapId == 6) : ?>
                                                        &nbsp;<b>[Received in wrong order]</b>
                                                        <?php endif; ?>
                                                    </span>
                                                </th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            <tr>
                                                <td>Raw</td>
                                                <td>
                                                    <?php echo str_replace_first(htmlspecialchars($station->name . '>'), '<b>' . htmlspecialchars($station->name) . '</b>&gt;', htmlspecialchars($packet->raw)); ?>
                                                </td>
                                            </tr>

                                            <tr><td>Packet type</td><td><?php echo $packet->getPacketTypeName(); ?></td></tr>

                                            <?php if ($packet->getStationObject()->stationTypeId == 2) : ?>
                                                <tr><td>Object/Item name</td><td><?php echo htmlspecialchars($packet->getStationObject()->name); ?></td></tr>
                                            <?php else : ?>
                                                <tr><td>Callsign</td><td><?php echo htmlspecialchars($packet->getStationObject()->name); ?></td></tr>
                                            <?php endif; ?>

                                            <?php if ($packet->getStationObject()->name != $packet->getSenderObject()->name) : ?>
                                                <tr><td>Sender</td><td><?php echo htmlspecialchars($packet->getSenderObject()->name); ?></td></tr>
                                            <?php endif; ?>

                                            <tr><td>Path</td><td><?php echo htmlspecialchars($packet->rawPath); ?></td></tr>

                                            <?php if ($packet->reportedTimestamp != null) : ?>
                                                <tr><td>Reported time</td><td><?php echo $packet->reportedTimestamp; ?> - <span class="raw-packet-timestamp"><?php echo $packet->reportedTimestamp; ?></span></td></tr>
                                            <?php endif; ?>

                                            <?php if ($packet->latitude != null && $packet->longitude != null) : ?>
                                                <tr><td>Latitude</td><td><?php echo round($packet->latitude, 5); ?></td></tr>
                                                <tr><td>Longitude</td><td><?php echo round($packet->longitude, 5); ?></td></tr>
                                            <?php endif; ?>

                                            <?php if ($packet->symbol != null && $packet->symbolTable != null) : ?>
                                                <tr><td>Symbol</td><td><?php echo htmlspecialchars($packet->symbol); ?></td></tr>
                                                <tr><td>Symbol table</td><td><?php echo htmlspecialchars($packet->symbolTable); ?></td></tr>
                                            <?php endif; ?>

                                            <?php if ($packet->speed != null) : ?>
                                                <?php if (isImperialUnitUser()) : ?>
                                                    <tr><td>Speed</td><td><?php echo convertKilometerToMile($packet->speed); ?> mph</td></tr>
                                                <?php else : ?>
                                                    <tr><td>Speed</td><td><?php echo $packet->speed; ?> km/h</td></tr>
                                                <?php endif; ?>
                                            <?php endif; ?>

                                            <?php if ($packet->course != null) : ?>
                                                <tr><td>Course</td><td><?php echo $packet->course; ?>°</td></tr>
                                            <?php endif; ?>

                                            <?php if ($packet->altitude != null) : ?>
                                                <?php if (isImperialUnitUser()) : ?>
                                                    <tr><td>Altitude</td><td><?php echo convertMeterToFeet($packet->altitude); ?> ft</td></tr>
                                                <?php else : ?>
                                                    <tr><td>Altitude</td><td><?php echo $packet->altitude; ?> m</td></tr>
                                                <?php endif; ?>
                                            <?php endif; ?>

                                            <?php if ($packet->comment != null) : ?>
                                                <?php if ($packet->packetTypeId == 10) : ?>
                                                    <tr><td>Status</td><td><?php echo htmlspecialchars($packet->comment); ?></td></tr>
                                                <?php elseif ($packet->packetTypeId == 7) : ?>
                                                    <tr><td>Beacon</td><td><?php echo htmlspecialchars($packet->comment); ?></td></tr>
                                                <?php else : ?>
                                                    <tr><td>Comment</td><td><?php echo htmlspecialchars($packet->comment); ?></td></tr>
                                                <?php endif; ?>
                                            <?php endif; ?>

                                            <?php if ($packet->posambiguity == 1) : ?>
                                                <tr><td>Posambiguity</td><td>Yes</td></tr>
                                            <?php endif; ?>

                                            <?php if ($packet->phg != null) : ?>
                                                <?php if (isImperialUnitUser()) : ?>
                                                    <tr><td>PHG</td><td><?php echo $packet->phg; ?> (Calculated range: <?php echo round(convertKilometerToMile($packet->getPHGRange()/1000),2); ?> miles)</td></tr>
                                                <?php else : ?>
                                                    <tr><td>PHG</td><td><?php echo $packet->phg; ?> (Calculated range: <?php echo round($packet->getPHGRange()/1000,2); ?> km)</td></tr>
                                                <?php endif; ?>
                                            <?php endif; ?>

                                            <?php if ($packet->rng != null) : ?>
                                                <tr><td>RNG</td><td><?php echo $packet->rng; ?></td></tr>
                                            <?php endif; ?>

                                            <?php if ($station->latestWeatherPacketTimestamp !== null) : ?>
                                                <?php $weather = $packet->getPacketWeather(); ?>
                                                <?php if ($weather->isExistingObject()) : ?>
                                                    <tr>
                                                        <td>Weather</td>
                                                        <td>
                                                            <table>
                                                                <tbody>
                                                                    <?php if ($weather->wxRawTimestamp !== null) : ?>
                                                                        <tr>
                                                                            <td>Time:</td><td><span class="raw-packet-timestamp"><?php echo $weather->wxRawTimestamp; ?></span></td>
                                                                        </tr>
                                                                    <?php endif; ?>

                                                                    <?php if ($weather->temperature !== null) : ?>
                                                                        <tr>
                                                                            <td>Temperature:</td>
                                                                            <?php if (isImperialUnitUser()) : ?>
                                                                                <td><?php echo round(convertCelciusToFahrenheit($weather->temperature), 2); ?>&deg; F</td>
                                                                            <?php else : ?>
                                                                                <td><?php echo round($weather->temperature, 2); ?>&deg; C</td>
                                                                            <?php endif; ?>
                                                                        </tr>
                                                                    <?php endif; ?>

                                                                    <?php if ($weather->humidity !== null) : ?>
                                                                        <tr>
                                                                            <td>Humidity:</td>
                                                                            <td><?php echo $weather->humidity; ?>%</td>
                                                                        </tr>
                                                                    <?php endif; ?>

                                                                    <?php if ($weather->pressure !== null) : ?>
                                                                        <tr>
                                                                            <td>Pressure:</td>
                                                                            <?php if (isImperialUnitUser()) : ?>
                                                                                <td><?php echo round(convertMbarToMmhg($weather->pressure),1); ?> mmHg</td>
                                                                            <?php else : ?>
                                                                                <td><?php echo round($weather->pressure,1); ?> hPa</td>
                                                                            <?php endif; ?>
                                                                        </tr>
                                                                    <?php endif; ?>

                                                                    <?php if ($weather->rain_1h !== null) : ?>
                                                                        <tr>
                                                                            <td>Rain latest hour:</td>
                                                                            <?php if (isImperialUnitUser()) : ?>
                                                                                <td><?php echo round(convertMmToInch($weather->rain_1h),2); ?> in</td>
                                                                            <?php else : ?>
                                                                                <td><?php echo round($weather->rain_1h,2); ?> mm</td>
                                                                            <?php endif; ?>
                                                                        </tr>
                                                                    <?php endif; ?>

                                                                    <?php if ($weather->rain_24h !== null) : ?>
                                                                        <tr>
                                                                            <td>Rain latest 24h hours:</td>
                                                                            <?php if (isImperialUnitUser()) : ?>
                                                                                <td><?php echo round(convertMmToInch($weather->rain_24h),2); ?> in</td>
                                                                            <?php else : ?>
                                                                                <td><?php echo round($weather->rain_24h,2); ?> mm</td>
                                                                            <?php endif; ?>
                                                                        </tr>
                                                                    <?php endif; ?>

                                                                    <?php if ($weather->rain_since_midnight !== null) : ?>
                                                                        <tr>
                                                                            <td>Rain since midnight:</td>
                                                                            <?php if (isImperialUnitUser()) : ?>
                                                                                <td><?php echo round(convertMmToInch($weather->rain_since_midnight),2); ?> in</td>
                                                                            <?php else : ?>
                                                                                <td><?php echo round($weather->rain_since_midnight,2); ?> mm</td>
                                                                            <?php endif; ?>
                                                                        </tr>
                                                                    <?php endif; ?>

                                                                    <?php if (isImperialUnitUser()) : ?>
                                                                        <?php if ($weather->wind_speed !== null && $weather->wind_speed > 0) : ?>
                                                                            <tr>
                                                                                <td>Wind Speed:</td>
                                                                                <td><?php echo round(convertMpsToMph($weather->wind_speed), 2); ?> mph, <?php echo $weather->wind_direction; ?>&deg;</td>
                                                                            </tr>
                                                                        <?php elseif($weather->wind_speed !== null) : ?>
                                                                            <tr>
                                                                                <td>Wind Speed:</td>
                                                                                <td><?php echo round(convertMpsToMph($weather->wind_speed), 2); ?> mph</td>
                                                                            </tr>
                                                                        <?php endif; ?>

                                                                    <?php else : ?>
                                                                        <?php if ($weather->wind_speed !== null && $weather->wind_speed > 0) : ?>
                                                                            <tr>
                                                                                <td>Wind Speed:</td>
                                                                                <td><?php echo round($weather->wind_speed, 2); ?> m/s, <?php echo $weather->wind_direction; ?>&deg;</td>
                                                                            </tr>
                                                                        <?php elseif($weather->wind_speed !== null) : ?>
                                                                            <tr>
                                                                                <td>Wind Speed:</td>
                                                                                <td><?php echo round($weather->wind_speed, 2); ?> m/s</td>
                                                                            </tr>
                                                                        <?php endif; ?>
                                                                    <?php endif; ?>

                                                                    <?php if ($weather->luminosity !== null) : ?>
                                                                        <tr>
                                                                            <td>Luminosity:</td><td><?php echo round($weather->luminosity,0); ?> W/m&sup2;</td>
                                                                        </tr>
                                                                    <?php endif; ?>

                                                                    <?php if ($weather->snow !== null) : ?>
                                                                        <tr>
                                                                        <?php if (isImperialUnitUser()) : ?>
                                                                            <td>Snow:</td><td><?php echo round(convertMmToInch($weather->snow), 0); ?> in</td>
                                                                        <?php else : ?>
                                                                            <td>Snow:</td><td><?php echo round($weather->snow, 0); ?> mm</td>
                                                                        <?php endif; ?>
                                                                        </tr>
                                                                    <?php endif; ?>
                                                                </tbody>
                                                            </table>
                                                        </td>
                                                    </tr>

                                                <?php endif; ?>
                                            <?php endif; ?>

                                            <?php if ($station->latestTelemetryPacketTimestamp !== null) : ?>
                                                <?php $telemetry = $packet->getPacketTelemetry(); ?>
                                                <?php if ($telemetry->isExistingObject()) : ?>
                                                    <tr>
                                                        <td>Telemetry Analog Values</td>
                                                        <td>
                                                            <table>
                                                                <tbody>
                                                                    <?php for ($i = 1; $i<=5; $i++) : ?>
                                                                        <?php if ($telemetry->isValueSet($i)) : ?>
                                                                            <tr>
                                                                                <td><?php echo htmlspecialchars($telemetry->getValueParameterName($i)); ?>:</td>
                                                                                <td><?php echo round($telemetry->getValue($i), 2); ?> <?php echo htmlspecialchars($telemetry->getValueUnit($i)); ?></td>
                                                                            </tr>
                                                                        <?php endif; ?>
                                                                    <?php endfor; ?>
                                                                </tbody>
                                                            </table>
                                                        </td>
                                                    </tr>
                                                    <?php if ($telemetry->bits !== null) : ?>
                                                        <tr>
                                                            <td>Telemetry Bit Values</td>
                                                            <td>
                                                                <table>
                                                                    <tbody>
                                                                        <?php for ($i = 1; $i<=8; $i++) : ?>
                                                                            <tr>
                                                                                <td><?php echo htmlspecialchars($telemetry->getBitParameterName($i)); ?>:</td>
                                                                                <td><?php echo $telemetry->getBit($i); ?></td>
                                                                            </tr>
                                                                        <?php endfor; ?>
                                                                    </tbody>
                                                                </table>
                                                            </td>
                                                        </tr>
                                                    <?php endif; ?>
                                                <?php endif; ?>


                                                <?php if ($packet->packetTypeId == 7 && strstr($packet->raw, ':UNIT.')) : ?>
                                                    <?php $pos = strpos($packet->raw, ':UNIT.'); ?>
                                                    <tr>
                                                        <td>Telemetry UNIT</td>
                                                        <td>
                                                            <?php echo htmlspecialchars(substr($packet->raw, $pos + 6)); ?>
                                                        </td>
                                                    </tr>
                                                <?php endif; ?>

                                                <?php if ($packet->packetTypeId == 7 && strstr($packet->raw, ':BITS.')) : ?>
                                                    <?php $pos = strpos($packet->raw, ':BITS.'); ?>
                                                    <tr>
                                                        <td>Telemetry BITS</td>
                                                        <td>
                                                            <?php echo htmlspecialchars(substr($packet->raw, $pos + 6)); ?>
                                                        </td>
                                                    </tr>
                                                <?php endif; ?>

                                                <?php if ($packet->packetTypeId == 7 && strstr($packet->raw, ':EQNS.')) : ?>
                                                    <?php $pos = strpos($packet->raw, ':EQNS.'); ?>
                                                    <tr>
                                                        <td>Telemetry EQNS</td>
                                                        <td>
                                                            <?php echo htmlspecialchars(substr($packet->raw, $pos + 6)); ?>
                                                        </td>
                                                    </tr>
                                                <?php endif; ?>

                                                <?php if ($packet->packetTypeId == 7 && strstr($packet->raw, ':PARM.')) : ?>
                                                    <?php $pos = strpos($packet->raw, ':PARM.'); ?>
                                                    <tr>
                                                        <td>Telemetry PARM</td>
                                                        <td>
                                                            <?php echo htmlspecialchars(substr($packet->raw, $pos + 6)); ?>
                                                        </td>
                                                    </tr>
                                                <?php endif; ?>
                                            <?php endif; ?>

                                            <?php if ($packet->getPacketOgn()->isExistingObject()) : ?>
                                                <?php if ($packet->getPacketOgn()->ognSignalToNoiseRatio !== null) : ?>
                                                    <tr>
                                                        <td>Signal to Noise Ratio</td>
                                                        <td>
                                                            <?php echo $packet->getPacketOgn()->ognSignalToNoiseRatio; ?> dB
                                                        </td>
                                                    </tr>
                                                <?php endif;?>

                                                <?php if ($packet->getPacketOgn()->ognBitErrorsCorrected !== null) : ?>
                                                    <tr>
                                                        <td>Bits corrected</td>
                                                        <td>
                                                            <?php echo $packet->getPacketOgn()->ognBitErrorsCorrected; ?>
                                                        </td>
                                                    </tr>
                                                <?php endif;?>

                                                <?php if ($packet->getPacketOgn()->ognFrequencyOffset !== null) : ?>
                                                    <tr>
                                                        <td>Frequency Offset</td>
                                                        <td>
                                                            <?php echo $packet->getPacketOgn()->ognFrequencyOffset; ?> kHz
                                                        </td>
                                                    </tr>
                                                <?php endif;?>

                                                <?php if ($packet->getPacketOgn()->ognClimbRate !== null) : ?>
                                                    <tr>
                                                        <td>Climb Rate</td>
                                                        <td>
                                                            <?php echo $packet->getPacketOgn()->ognClimbRate; ?> fpm
                                                        </td>
                                                    </tr>
                                                <?php endif;?>

                                                <?php if ($packet->getPacketOgn()->ognTurnRate !== null) : ?>
                                                    <tr>
                                                        <td>Turn Rate</td>
                                                        <td>
                                                            <?php echo $packet->getPacketOgn()->ognTurnRate; ?> fpm
                                                        </td>
                                                    </tr>
                                                <?php endif;?>
                                            <?php endif;?>
                                        </tbody>
                                    </table>
                                </div>
                            </div>
                        <?php endif; ?>
                    <?php endforeach; ?>
                </div>

                <?php if (count($packets) == 0) : ?>
                <p>
                    <b><i>No raw packets found.</i></b>
                </p>
                <?php endif; ?>
            </div>
        </body>
    </html>
<?php endif; ?>