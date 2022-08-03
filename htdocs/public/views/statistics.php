<?php require dirname(__DIR__) . "../../includes/bootstrap.php"; ?>

<?php $station = StationRepository::getInstance()->getObjectById($_GET['id'] ?? null); ?>
<?php if ($station->isExistingObject()) : ?>
    <?php
        $days = 10;
        if (!isAllowedToShowOlderData()) {
            $days = 1;
        }
    ?>
    <?php $senderStats = PacketPathRepository::getInstance()->getSenderPacketPathSatistics($station->id, time() - (60*60*24*$days)); ?>
    <?php $receiverStats = PacketPathRepository::getInstance()->getReceiverPacketPathSatistics($station->id, time() - (60*60*24*$days)); ?>

    <title><?php echo $station->name; ?> Stats</title>
    <div class="modal-inner-content">
        <div class="modal-inner-content-menu">
            <a class="tdlink" title="Overview" href="/views/overview.php?id=<?php echo $station->id ?>&imperialUnits=<?php echo $_GET['imperialUnits'] ?? 0; ?>">Overview</a>
            <span>Statistics</span>
            <a class="tdlink" title="Trail Chart" href="/views/trail.php?id=<?php echo $station->id ?>&imperialUnits=<?php echo $_GET['imperialUnits'] ?? 0; ?>">Trail Chart</a>
            <a class="tdlink" title="Weather" href="/views/weather.php?id=<?php echo $station->id ?>&imperialUnits=<?php echo $_GET['imperialUnits'] ?? 0; ?>">Weather</a>
            <a class="tdlink" title="Telemetry" href="/views/telemetry.php?id=<?php echo $station->id ?>&imperialUnits=<?php echo $_GET['imperialUnits'] ?? 0; ?>">Telemetry</a>
            <a class="tdlink" title="Raw packets" href="/views/raw.php?id=<?php echo $station->id ?>&imperialUnits=<?php echo $_GET['imperialUnits'] ?? 0; ?>">Raw packets</a>
        </div>

        <div class="horizontal-line">&nbsp;</div>

        <p>
            The communication statistics that we show here may differ from similar communication statistics on other websites, the reason is probably that this website is not collecting packets from the same APRS servers. Each APRS server performes duplicate filtering, and which packet that is considered to be a duplicate may differ depending on which APRS server you receive your data from.
        </p>

        <?php if (count($senderStats) > 0) : ?>
            <p>Stations that heard <?php echo htmlspecialchars($station->name) ?> <b>directly</b> during the latest <?php echo $days; ?> day(s).</p>
            <div class="datagrid datagrid-statistics" style="max-width:700px;">
                <table>
                    <thead>
                        <tr>
                            <th>Station</th>
                            <th>Number of packets</th>
                            <th>Latest heard</th>
                            <th>Longest distance</th>
                        </tr>
                    </thead>
                    <tbody>
                    <?php foreach ($senderStats as $stats) : ?>
                        <?php $otherStation = StationRepository::getInstance()->getObjectById($stats["station_id"]) ?>
                        <tr>
                            <td>
                                <img alt="Symbol" src="<?php echo $otherStation->getIconFilePath(22, 22); ?>" style="vertical-align: middle;"/>&nbsp;
                                <a class="tdlink" href="/views/overview.php?id=<?php echo $otherStation->id; ?>&imperialUnits=<?php echo $_GET['imperialUnits'] ?? 0; ?>"><?php echo htmlentities($otherStation->name) ?></a>
                            </td>
                            <td>
                                <?php echo $stats["number_of_packets"]; ?>
                            </td>
                            <td class="latest-heard">
                                <?php echo $stats["latest_timestamp"];?>
                            </td>

                            <td class="longest-distance">
                                <?php if ($stats["longest_distance"] !== null) : ?>
                                    <?php if (isImperialUnitUser()) : ?>
                                        <?php echo round(convertKilometerToMile($stats["longest_distance"] / 1000), 2); ?> miles
                                    <?php else : ?>
                                        <?php echo round($stats["longest_distance"] / 1000, 2); ?> km
                                    <?php endif; ?>
                                <?php else : ?>
                                    &nbsp;
                                <?php endif; ?>
                            </td>
                        </tr>
                    <?php endforeach; ?>
                    </tbody>
                </table>
            </div>
            <br/>
        <?php endif; ?>


        <?php if (count($receiverStats) > 0) : ?>
            <p>Stations <b>directly</b> heard by <?php echo htmlspecialchars($station->name); ?> during the latest <?php echo $days; ?> day(s).</p>
            <div class="datagrid datagrid-statistics" style="max-width:700px;">
                <table>
                    <thead>
                        <tr>
                            <th>Station</th>
                            <th>Number of packets</th>
                            <th>Latest heard</th>
                            <th>Longest distance</th>
                        </tr>
                    </thead>
                    <tbody>
                    <?php foreach ($receiverStats as $stats) : ?>
                        <?php $otherStation = StationRepository::getInstance()->getObjectById($stats["station_id"]) ?>
                        <tr>
                            <td>
                                <img alt="Symbol" src="<?php echo $otherStation->getIconFilePath(22, 22); ?>" style="vertical-align: middle;"/>&nbsp;
                                <a class="tdlink" href="/views/overview.php?id=<?php echo $otherStation->id; ?>&imperialUnits=<?php echo $_GET['imperialUnits'] ?? 0; ?>"><?php echo htmlentities($otherStation->name) ?></a>

                            </td>
                            <td>
                                <?php echo $stats["number_of_packets"]; ?>
                            </td>
                            <td class="latest-heard">
                                <?php echo $stats["latest_timestamp"];?>
                            </td>
                            <td class="longest-distance">
                                <?php if ($stats["longest_distance"] !== null) : ?>
                                    <?php if (isImperialUnitUser()) : ?>
                                        <?php echo round(convertKilometerToMile($stats["longest_distance"] / 1000), 2); ?> miles
                                    <?php else : ?>
                                        <?php echo round($stats["longest_distance"] / 1000, 2); ?> km
                                    <?php endif; ?>
                                <?php else : ?>
                                    &nbsp;
                                <?php endif; ?>
                            </td>
                        </tr>
                    <?php endforeach; ?>
                    </tbody>
                </table>
            </div>
            <br/>
        <?php endif; ?>


        <?php if (count($senderStats) == 0 && count($receiverStats) == 0): ?>
            <p><i><b>No radio communication statistics during the latest <?php echo $days; ?> days.</b></i></p>
        <?php endif; ?>
    </div>
    <script>
        $(document).ready(function() {
            var locale = window.navigator.userLanguage || window.navigator.language;
            moment.locale(locale);

            $('.latest-heard').each(function() {
                if ($(this).html().trim() != '' && !isNaN($(this).html().trim())) {
                    $(this).html(moment(new Date(1000 * $(this).html())).format('L LTSZ'));
                }
	    });

            if (window.trackdirect) {
                <?php if ($station->latestConfirmedLatitude != null && $station->latestConfirmedLongitude != null) : ?>
                    window.trackdirect.addListener("map-created", function() {
                        if (!window.trackdirect.focusOnStation(<?php echo $station->id ?>, true)) {
                            window.trackdirect.setCenter(<?php echo $station->latestConfirmedLatitude ?>, <?php echo $station->latestConfirmedLongitude ?>);
                        }
                    });
                <?php endif; ?>
            }
        });
    </script>
<?php endif; ?>
