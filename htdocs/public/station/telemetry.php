<?php require "../../includes/bootstrap.php"; ?>

<?php $station = StationRepository::getInstance()->getObjectById($_GET['id']); ?>
<?php if ($station->isExistingObject()) : ?>
    <?php
        $maxDays = 10;
        $page = $_GET['page'] ?? 1;
        $rows = $_GET['rows'] ?? 25;
        $offset = ($page - 1) * $rows;
        $telemetryPackets = PacketTelemetryRepository::getInstance()->getLatestObjectListByStationId($station->id, $rows, $offset, $maxDays);
        $latestPacketTelemetry = (count($telemetryPackets) > 0 ? $telemetryPackets[0] : new PacketTelemetry(null));
        $count = PacketTelemetryRepository::getInstance()->getLatestNumberOfPacketsByStationId($station->id, $maxDays);
        $pages = ceil($count / $rows);
    ?>

    <!DOCTYPE html>
    <html lang="en">
        <head>
            <meta charset="utf-8" />
            <title><?php echo $station->name; ?> Telemetry</title>
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

                    $('.telemetrytime').each(function() {
                        if ($(this).html().trim() != '' && !isNaN($(this).html().trim())) {
                            $(this).html(moment(new Date(1000 * $(this).html())).format('L LTSZ'));
                        }
                    });

                    $('#telemetry-category').change(function () {
                        location.href = "/station/telemetry.php?id=<?php echo $station->id ?>&category=" + $('#telemetry-category').val() + "&rows=" + $('#telemetry-rows').val() + "&page=1";
                    });

                    $('#telemetry-rows').change(function () {
                        location.href = "/station/telemetry.php?id=<?php echo $station->id ?>&category=" + $('#telemetry-category').val() + "&rows=" + $('#telemetry-rows').val() + "&page=1";
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

                        location.href = "/station/telemetry.php?id=<?php echo $station->id ?>&rows=" + $('#telemetry-rows').val() + "&page=" + page;
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
                    <span>Telemetry</span>
                    <a title="Raw packets" href="/station/raw.php?id=<?php echo $station->id ?>&imperialUnits=<?php echo $_GET['imperialUnits'] ?? 0; ?>">Raw packets</a>
                </div>

                <div class="horizontal-line" style="margin-bottom: 15px;">&nbsp;</div>

                <?php if (count($telemetryPackets) > 0) : ?>

                    <p>This is the latest recevied telemetry packets stored in our database for station/object <?php echo $station->name; ?>. If no packets are shown the sender has not sent any telemetry packets the latest <?php echo $maxDays; ?> days.</p>
                    <p>Telemetry packets is used to share measurements like repeteater parameters, battery voltage, radiation readings (or any other measurements).</p>

                    <div class="form-container">
                        <select id="telemetry-category" style="float:left; margin-right: 5px;">
                            <option <?php echo (($_GET['category'] ?? 1) == 1 ? 'selected' : ''); ?> value="1">Telemetry Values</option>
                            <option <?php echo (($_GET['category'] ?? 1) == 2 ? 'selected' : ''); ?> value="2">Telemetry Bits</option>
                        </select>

                        <select id="telemetry-rows" style="float:left; margin-right: 5px;" class="pagination-rows">
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

                    <?php if (($_GET['category'] ?? 1) == 1) : ?>
                    <div class="datagrid datagrid-telemetry1" style="max-width:1000px;">
                        <table>
                            <thead>
                                <tr>
                                    <th>Time</th>
                                    <th><?php echo htmlspecialchars($latestPacketTelemetry->getValueParameterName(1)); ?>*</th>
                                    <th><?php echo htmlspecialchars($latestPacketTelemetry->getValueParameterName(2)); ?>*</th>
                                    <th><?php echo htmlspecialchars($latestPacketTelemetry->getValueParameterName(3)); ?>*</th>
                                    <th><?php echo htmlspecialchars($latestPacketTelemetry->getValueParameterName(4)); ?>*</th>
                                    <th><?php echo htmlspecialchars($latestPacketTelemetry->getValueParameterName(5)); ?>*</th>
                                </tr>
                            </thead>
                            <tbody>
                            <?php foreach ($telemetryPackets as $packetTelemetry) : ?>

                                <tr>
                                    <td class="telemetrytime">
                                        <?php echo ($packetTelemetry->wxRawTimestamp != null?$packetTelemetry->wxRawTimestamp:$packetTelemetry->timestamp); ?>
                                    </td>
                                    <td>
                                        <?php if ($packetTelemetry->val1 !== null) : ?>
                                            <?php echo round($packetTelemetry->getValue(1), 2); ?> <?php echo htmlspecialchars($packetTelemetry->getValueUnit(1)); ?>
                                        <?php else : ?>
                                            -
                                        <?php endif; ?>
                                    </td>
                                    <td>
                                        <?php if ($packetTelemetry->val1 !== null) : ?>
                                            <?php echo round($packetTelemetry->getValue(2), 2); ?> <?php echo htmlspecialchars($packetTelemetry->getValueUnit(2)); ?>
                                        <?php else : ?>
                                            -
                                        <?php endif; ?>
                                    </td>
                                    <td>
                                        <?php if ($packetTelemetry->val1 !== null) : ?>
                                            <?php echo round($packetTelemetry->getValue(3), 2); ?> <?php echo htmlspecialchars($packetTelemetry->getValueUnit(3)); ?>
                                        <?php else : ?>
                                            -
                                        <?php endif; ?>
                                    </td>
                                    <td>
                                        <?php if ($packetTelemetry->val1 !== null) : ?>
                                            <?php echo round($packetTelemetry->getValue(4), 2); ?> <?php echo htmlspecialchars($packetTelemetry->getValueUnit(4)); ?>
                                        <?php else : ?>
                                            -
                                        <?php endif; ?>
                                    </td>
                                    <td>
                                        <?php if ($packetTelemetry->val1 !== null) : ?>
                                            <?php echo round($packetTelemetry->getValue(5), 2); ?> <?php echo htmlspecialchars($packetTelemetry->getValueUnit(5)); ?>
                                        <?php else : ?>
                                            -
                                        <?php endif; ?>
                                    </td>
                                </tr>

                            <?php endforeach; ?>
                            </tbody>
                        </table>
                    </div>

                    <div class="telemetry-subtable">
                        <div>
                            <div>
                                *Used Equation Coefficients:
                            </div>
                            <div>
                                <?php echo htmlspecialchars($latestPacketTelemetry->getValueParameterName(1)); ?>: <?php echo implode(', ', $latestPacketTelemetry->getEqnsValue(1)); ?>
                            </div>
                            <div>
                                <?php echo htmlspecialchars($latestPacketTelemetry->getValueParameterName(2)); ?>: <?php echo implode(', ', $latestPacketTelemetry->getEqnsValue(2)); ?>
                            </div>
                            <div>
                                <?php echo htmlspecialchars($latestPacketTelemetry->getValueParameterName(3)); ?>: <?php echo implode(', ', $latestPacketTelemetry->getEqnsValue(3)); ?>
                            </div>
                            <div>
                                <?php echo htmlspecialchars($latestPacketTelemetry->getValueParameterName(4)); ?>: <?php echo implode(', ', $latestPacketTelemetry->getEqnsValue(4)); ?>
                            </div>
                            <div>
                                <?php echo htmlspecialchars($latestPacketTelemetry->getValueParameterName(5)); ?>: <?php echo implode(', ', $latestPacketTelemetry->getEqnsValue(5)); ?>
                            </div>
                        </div>
                    </div>
                <?php endif; ?>

                    <?php if (($_GET['category'] ?? 1) == 2) : ?>
                        <div class="datagrid datagrid-telemetry2" style="max-width:1000px;">
                            <table>
                                <thead>
                                    <tr>
                                        <th>Time</th>
                                        <th><?php echo htmlspecialchars($latestPacketTelemetry->getBitParameterName(1)); ?>*</th>
                                        <th><?php echo htmlspecialchars($latestPacketTelemetry->getBitParameterName(2)); ?>*</th>
                                        <th><?php echo htmlspecialchars($latestPacketTelemetry->getBitParameterName(3)); ?>*</th>
                                        <th><?php echo htmlspecialchars($latestPacketTelemetry->getBitParameterName(4)); ?>*</th>
                                        <th><?php echo htmlspecialchars($latestPacketTelemetry->getBitParameterName(5)); ?>*</th>
                                        <th><?php echo htmlspecialchars($latestPacketTelemetry->getBitParameterName(6)); ?>*</th>
                                        <th><?php echo htmlspecialchars($latestPacketTelemetry->getBitParameterName(7)); ?>*</th>
                                        <th><?php echo htmlspecialchars($latestPacketTelemetry->getBitParameterName(8)); ?>*</th>
                                    </tr>
                                </thead>
                                <tbody>
                                <?php foreach ($telemetryPackets as $i => $packetTelemetry) : ?>
                                    <?php if ($packetTelemetry->bits !== null && $i >= 2 ) : ?>
                                    <tr>
                                        <td class="telemetrytime">
                                            <?php echo $packetTelemetry->timestamp; ?>
                                        </td>
                                        <td>
                                            <div class="<?php echo ($packetTelemetry->getBit(1) == 1?'telemetry-biton':'telemetry-bitoff'); ?>">
                                                <?php echo htmlspecialchars($packetTelemetry->getBitLabel(1)); ?>
                                            </div>
                                        </td>
                                        <td>
                                            <div class="<?php echo ($packetTelemetry->getBit(2) == 1?'telemetry-biton':'telemetry-bitoff'); ?>">
                                                <?php echo htmlspecialchars($packetTelemetry->getBitLabel(2)); ?>
                                            </div>
                                        </td>
                                        <td>
                                            <div class="<?php echo ($packetTelemetry->getBit(3) == 1?'telemetry-biton':'telemetry-bitoff'); ?>">
                                                <?php echo htmlspecialchars($packetTelemetry->getBitLabel(3)); ?>
                                            </div>
                                        </td>
                                        <td>
                                            <div class="<?php echo ($packetTelemetry->getBit(4) == 1?'telemetry-biton':'telemetry-bitoff'); ?>">
                                                <?php echo htmlspecialchars($packetTelemetry->getBitLabel(4)); ?>
                                            </div>
                                        </td>
                                        <td>
                                            <div class="<?php echo ($packetTelemetry->getBit(5) == 1?'telemetry-biton':'telemetry-bitoff'); ?>">
                                                <?php echo htmlspecialchars($packetTelemetry->getBitLabel(5)); ?>
                                            </div>
                                        </td>
                                        <td>
                                            <div class="<?php echo ($packetTelemetry->getBit(6) == 1?'telemetry-biton':'telemetry-bitoff'); ?>">
                                                <?php echo htmlspecialchars($packetTelemetry->getBitLabel(6)); ?>
                                            </div>
                                        </td>
                                        <td>
                                            <div class="<?php echo ($packetTelemetry->getBit(7) == 1?'telemetry-biton':'telemetry-bitoff'); ?>">
                                                <?php echo htmlspecialchars($packetTelemetry->getBitLabel(7)); ?>
                                            </div>
                                        </td>
                                        <td>
                                            <div class="<?php echo ($packetTelemetry->getBit(8) == 1?'telemetry-biton':'telemetry-bitoff'); ?>">
                                                <?php echo htmlspecialchars($packetTelemetry->getBitLabel(8)); ?>
                                            </div>
                                        </td>
                                    </tr>
                                    <?php endif; ?>
                                <?php endforeach; ?>
                                </tbody>
                            </table>
                        </div>

                        <div class="telemetry-subtable">
                            <div>
                                <div>
                                    *Used Bit Sense:
                                </div>
                                <div>
                                    <?php echo $latestPacketTelemetry->getBitSense(1); ?>
                                    <?php echo $latestPacketTelemetry->getBitSense(2); ?>
                                    <?php echo $latestPacketTelemetry->getBitSense(3); ?>
                                    <?php echo $latestPacketTelemetry->getBitSense(4); ?>
                                    <?php echo $latestPacketTelemetry->getBitSense(5); ?>
                                    <?php echo $latestPacketTelemetry->getBitSense(6); ?>
                                    <?php echo $latestPacketTelemetry->getBitSense(7); ?>
                                    <?php echo $latestPacketTelemetry->getBitSense(8); ?>
                                </div>
                            </div>
                        </div>
                    <?php endif; ?>
                <?php endif; ?>


                <?php if (count($telemetryPackets) > 0) : ?>
                    <br/>
                    <ul>
                        <li>The parameter names for the analog channels will be Value1, Value2, Value3 (up to Value5) if station has not sent a PARAM-packet that specifies the parameter names for each analog channel.</li>
                        <li>Each analog value is a decimal number between 000 and 255 (according to APRS specifications). The receiver use the telemetry equation coefficientsto to restore the original sensor values. If no EQNS-packet with equation coefficients is sent we will show the values as is (this corresponds to the equation coefficients a=0, b=1 and c=0).<br/>The sent equation coefficients is used in the equation: a * value<sup>2</sup> + b * value + c.</li>
                        <li>The units for the analog values will not be shown if station has not sent a UNIT-packet specifying what unit's to use.</li>
                        <li>The parameter names for the digital bits will be Bit1, Bit2, Bit3 (up to Bit8) if station has not sent a PARAM-packet that specifies the parameter names for each digital bit.</li>
                        <li>All bit labels will be named "On" if station has not sent a UNIT-packet that specifies the label of each bit.</li>
                        <li>A bit is considered to be <b>On</b> when the bit is 1 if station has not sent a BITS-packet that specifies another "Bit sense" (a BITS-packet specify the state of the bits that match the BIT labels)</li>
                    </ul>
                <?php endif; ?>

                <?php if (count($telemetryPackets) == 0) : ?>
                    <p><i><b>No recent telemetry values.</b></i></p>
                <?php endif; ?>

            </div>
        </body>
    </html>
<?php endif; ?>