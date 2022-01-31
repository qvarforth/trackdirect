<?php require "../../includes/bootstrap.php"; ?>

<?php $station = StationRepository::getInstance()->getObjectById($_GET['id'] ?? null); ?>
<?php if ($station->isExistingObject()) : ?>
    <?php $days = 10; ?>
    <?php $senderStats = PacketPathRepository::getInstance()->getSenderPacketPathSatistics($station->id, time() - (60*60*24*$days)); ?>
    <?php $receiverStats = PacketPathRepository::getInstance()->getReceiverPacketPathSatistics($station->id, time() - (60*60*24*$days)); ?>

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

                    $('.latest-heard').each(function() {
                        if ($(this).html().trim() != '' && !isNaN($(this).html().trim())) {
                            $(this).html(moment(new Date(1000 * $(this).html())).format('L LTSZ'));
                        }
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
                    <span>Statistics</span>
                    <a title="Trail Chart" href="/station/trail.php?id=<?php echo $station->id ?>&imperialUnits=<?php echo $_GET['imperialUnits'] ?? 0; ?>">Trail Chart</a>
                    <a title="Weather" href="/station/weather.php?id=<?php echo $station->id ?>&imperialUnits=<?php echo $_GET['imperialUnits'] ?? 0; ?>">Weather</a>
                    <a title="Telemetry" href="/station/telemetry.php?id=<?php echo $station->id ?>&imperialUnits=<?php echo $_GET['imperialUnits'] ?? 0; ?>">Telemetry</a>
                    <a title="Raw packets" href="/station/raw.php?id=<?php echo $station->id ?>&imperialUnits=<?php echo $_GET['imperialUnits'] ?? 0; ?>">Raw packets</a>
                </div>

                <div class="horizontal-line">&nbsp;</div>

                <p>
                    The communication statistics that we show here may differ from similar communication statistics on other websites, the reason is probably that this website is not collecting packets from the same APRS servers. Each APRS server performes duplicate filtering, and which packet that is considered to be a duplicate may differ depending on which APRS server you receive your data from.
                </p>

                <?php if (count($senderStats) > 0) : ?>
                    <p>Stations that heard <?php echo htmlspecialchars($station->name) ?> <b>directly</b> during the latest <?php echo $days; ?> days.</p>
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
                                        <a href="/station/overview.php?id=<?php echo $otherStation->id; ?>&imperialUnits=<?php echo $_GET['imperialUnits'] ?? 0; ?>"><?php echo htmlentities($otherStation->name) ?></a>
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
                    <p>Stations <b>directly</b> heard by <?php echo htmlspecialchars($station->name); ?> during the latest <?php echo $days; ?> days.</p>
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
                                        <a href="/station/overview.php?id=<?php echo $otherStation->id; ?>&imperialUnits=<?php echo $_GET['imperialUnits'] ?? 0; ?>"><?php echo htmlentities($otherStation->name) ?></a>

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
        </body>
    </html>
<?php endif; ?>