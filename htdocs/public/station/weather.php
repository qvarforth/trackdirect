<?php require "../../includes/bootstrap.php"; ?>

<?php $station = StationRepository::getInstance()->getObjectById($_GET['id']); ?>
<?php if ($station->isExistingObject()) : ?>
    <?php
        $maxDays = 10;
        $page = $_GET['page'] ?? 1;
        $rows = $_GET['rows'] ?? 25;
        $offset = ($page - 1) * $rows;
        $weatherPackets = PacketWeatherRepository::getInstance()->getLatestObjectListByStationIdAndLimit($station->id, $rows, $offset, $maxDays);
        $count = PacketWeatherRepository::getInstance()->getLatestNumberOfPacketsByStationIdAndLimit($station->id, $maxDays);
        $pages = ceil($count / $rows);
    ?>

    <!DOCTYPE html>
    <html lang="en">
        <head>
            <meta charset="utf-8" />
            <title><?php echo $station->name; ?> Weather</title>
            <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=0"/>
            <meta name="apple-mobile-web-app-capable" content="yes"/>
            <meta name="mobile-web-app-capable" content="yes">

            <script src="https://cdnjs.cloudflare.com/ajax/libs/jquery/1.12.4/jquery.min.js" integrity="sha512-jGsMH83oKe9asCpkOVkBnUrDDTp8wl+adkB2D+//JtlxO4SrLoJdhbOysIFQJloQFD+C4Fl1rMsQZF76JjV0eQ==" crossorigin="anonymous"></script>
            <script src="https://cdnjs.cloudflare.com/ajax/libs/moment.js/2.29.1/moment-with-locales.min.js" integrity="sha512-LGXaggshOkD/at6PFNcp2V2unf9LzFq6LE+sChH7ceMTDP0g2kn6Vxwgg7wkPP7AAtX+lmPqPdxB47A0Nz0cMQ==" crossorigin="anonymous"></script>

            <link rel="stylesheet" href="/css/main.css">

            <script>
                $(document).ready(function() {
                    var locale = window.navigator.userLanguage || window.navigator.language;
                    moment.locale(locale);

                    $('.weathertime').each(function() {
                        if ($(this).html().trim() != '' && !isNaN($(this).html().trim())) {
                            $(this).html(moment(new Date(1000 * $(this).html())).format('L LTSZ'));
                        }
                    });

                    $('#weather-rows').change(function () {
                        location.href = "/station/weather.php?id=<?php echo $station->id ?>&rows=" + $('#weather-rows').val() + "&page=1";
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

                        location.href = "/station/weather.php?id=<?php echo $station->id ?>&rows=" + $('#weather-rows').val() + "&page=" + page;
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
                    <span>Weather</span>
                    <a title="Telemetry" href="/station/telemetry.php?id=<?php echo $station->id ?>&imperialUnits=<?php echo $_GET['imperialUnits'] ?? 0; ?>">Telemetry</a>
                    <a title="Raw packets" href="/station/raw.php?id=<?php echo $station->id ?>&imperialUnits=<?php echo $_GET['imperialUnits'] ?? 0; ?>">Raw packets</a>
                </div>

                <div class="horizontal-line" style="margin-bottom: 15px;">&nbsp;</div>

                <?php if (count($weatherPackets) > 0) : ?>

                    <p>This is the latest recevied weather packets stored in our database for station/object <?php echo $station->name; ?>. If no packets are shown the sender has not sent any weather packets the latest <?php echo $maxDays; ?> days.</p>

                    <div class="form-container">
                        <select id="weather-rows" style="float:left; margin-right: 5px;" class="pagination-rows">
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

                    <div class="datagrid datagrid-weather" style="max-width:1000px;">
                        <table>
                            <thead>
                                <tr>
                                    <th>Time</th>
                                    <th>Temp.</th>
                                    <th>Humidity</th>
                                    <th>Pressure</th>
                                    <th>Rain*</th>
                                    <th>Wind**</th>
                                    <th>Luminosity</th>
                                    <th>Snow</th>
                                </tr>
                            </thead>
                            <tbody>
                            <?php foreach ($weatherPackets as $packetWeather) : ?>

                                <tr>
                                    <td class="weathertime">
                                        <?php echo ($packetWeather->wxRawTimestamp != null?$packetWeather->wxRawTimestamp:$packetWeather->timestamp); ?>
                                    </td>
                                    <td>
                                        <?php if ($packetWeather->temperature !== null) : ?>
                                            <?php if (isImperialUnitUser()) : ?>
                                                <?php echo round(convertCelciusToFahrenheit($packetWeather->temperature), 2); ?>&deg; F
                                            <?php else : ?>
                                                <?php echo round($packetWeather->temperature, 2); ?>&deg; C
                                            <?php endif; ?>
                                        <?php else : ?>
                                            -
                                        <?php endif; ?>
                                    </td>
                                    <td>
                                        <?php if ($packetWeather->humidity !== null) : ?>
                                            <?php echo $packetWeather->humidity; ?>%
                                        <?php else : ?>
                                            -
                                        <?php endif; ?>
                                    </td>
                                    <td>
                                        <?php if ($packetWeather->pressure !== null) : ?>
                                            <?php if (isImperialUnitUser()) : ?>
                                                <?php echo round(convertMbarToMmhg($packetWeather->pressure),1); ?> mmHg
                                            <?php else : ?>
                                                <?php echo round($packetWeather->pressure,1); ?> hPa
                                            <?php endif; ?>

                                        <?php else : ?>
                                            -
                                        <?php endif; ?>
                                    </td>

                                    <?php if ($weatherPackets[0]->rain_1h !== null) : ?>
                                        <td title="<?php echo $packetWeather->getRainSummary(false, true, true); ?>">
                                            <?php if ($packetWeather->rain_1h !== null) : ?>
                                                <?php if (isImperialUnitUser()) : ?>
                                                    <?php echo round(convertMmToInch($packetWeather->rain_1h), 2); ?> in
                                                <?php else : ?>
                                                    <?php echo round($packetWeather->rain_1h, 2); ?> mm
                                                <?php endif; ?>
                                            <?php else : ?>
                                                -
                                            <?php endif; ?>
                                        </td>
                                    <?php elseif ($weatherPackets[0]->rain_24h !== null) : ?>
                                        <td title="<?php echo $packetWeather->getRainSummary(true, false, true); ?>">
                                            <?php if ($packetWeather->rain_24h !== null) : ?>
                                                <?php if (isImperialUnitUser()) : ?>
                                                    <?php echo round(convertMmToInch($packetWeather->rain_24h), 2); ?> in
                                                <?php else : ?>
                                                    <?php echo round($packetWeather->rain_24h, 2); ?> mm
                                                <?php endif; ?>
                                            <?php else : ?>
                                                -
                                            <?php endif; ?>
                                        </td>
                                    <?php else : ?>
                                        <td title="<?php echo $packetWeather->getRainSummary(true, true, false); ?>">
                                            <?php if ($packetWeather->rain_since_midnight !== null) : ?>
                                                <?php if (isImperialUnitUser()) : ?>
                                                    <?php echo round(convertMmToInch($packetWeather->rain_since_midnight), 2); ?> in
                                                <?php else : ?>
                                                    <?php echo round($packetWeather->rain_since_midnight, 2); ?> mm
                                                <?php endif; ?>
                                            <?php else : ?>
                                                -
                                            <?php endif; ?>
                                        </td>
                                    <?php endif; ?>

                                    <td title="Wind gust: <?php echo ($packetWeather->wind_gust !== null?round($packetWeather->wind_gust,2):'-'); ?> m/s">

                                        <?php if (isImperialUnitUser()) : ?>
                                            <?php if ($packetWeather->wind_speed !== null && $packetWeather->wind_speed > 0) : ?>
                                                <?php echo round(convertMpsToMph($packetWeather->wind_speed), 2); ?> mph, <?php echo $packetWeather->wind_direction; ?>&deg;
                                            <?php elseif($packetWeather->wind_speed !== null) : ?>
                                                <?php echo round(convertMpsToMph($packetWeather->wind_speed), 2); ?> mph
                                            <?php else : ?>
                                                -
                                            <?php endif; ?>

                                        <?php else : ?>
                                            <?php if ($packetWeather->wind_speed !== null && $packetWeather->wind_speed > 0) : ?>
                                                <?php echo round($packetWeather->wind_speed, 2); ?> m/s, <?php echo $packetWeather->wind_direction; ?>&deg;
                                            <?php elseif($packetWeather->wind_speed !== null) : ?>
                                                <?php echo round($packetWeather->wind_speed, 2); ?> m/s
                                            <?php else : ?>
                                                -
                                            <?php endif; ?>
                                        <?php endif; ?>
                                    </td>

                                    <td>
                                        <?php if ($packetWeather->luminosity !== null) : ?>
                                            <?php echo round($packetWeather->luminosity,0); ?> W/m&sup2;
                                        <?php else : ?>
                                            -
                                        <?php endif; ?>
                                    </td>

                                    <td>
                                        <?php if ($packetWeather->snow !== null) : ?>
                                            <?php if (isImperialUnitUser()) : ?>
                                                <?php echo round(convertMmToInch($packetWeather->snow), 0); ?> in
                                            <?php else : ?>
                                                <?php echo round($packetWeather->snow, 0); ?> mm
                                            <?php endif; ?>
                                        <?php else : ?>
                                            -
                                        <?php endif; ?>
                                    </td>
                                </tr>

                            <?php endforeach; ?>
                            </tbody>
                        </table>
                    </div>
                    <p>
                        <?php if ($weatherPackets[0]->rain_1h !== null) : ?>
                            * Rain latest hour (hover to see other rain measurements)<br/>
                        <?php elseif ($weatherPackets[0]->rain_24h !== null) : ?>
                            * Rain latest 24 hours (hover to see other rain measurements)<br/>
                        <?php else : ?>
                            * Rain since midnight (hover to see other rain measurements)<br/>
                        <?php endif; ?>
                        ** Current wind speed in m/s (hover to see current wind gust speed)
                    </p>

                <?php endif; ?>

                <?php if (count($weatherPackets) == 0) : ?>
                    <p><i><b>No recent weather reports.</b></i></p>
                <?php endif; ?>

            </div>
        </body>
    </html>
<?php endif; ?>