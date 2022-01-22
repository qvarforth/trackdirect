<?php require "../includes/bootstrap.php"; ?>

<?php
    $stations = [];
    $seconds = $_GET['seconds'] ?? 0;
    $page = $_GET['page'] ?? 1;
    $rows = $_GET['rows'] ?? 50;
    $offset = ($page - 1) * $rows;
    $count = 0;
    if (isset($_GET['q'])) {
        $stations = StationRepository::getInstance()->getObjectListByQueryString($_GET['q'], $seconds, $rows, $offset);
        $count = StationRepository::getInstance()->getNumberOfStationsByQueryString($_GET['q'], $seconds);
    }
    $pages = ceil($count / $rows);
?>

<!DOCTYPE html>
<html lang="en">
    <head>
        <meta charset="utf-8" />
        <title>Station search</title>
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

                $('.station-latest-heard-timestamp').each(function() {
                    if ($(this).html().trim() != '' && !isNaN($(this).html().trim())) {
                        $(this).html(moment(new Date(1000 * $(this).html())).format('L LTSZ'));
                    }
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

                    location.href = "/search.php?q=<?php echo ($_GET['q'] ?? "") ?>&seconds=<?php echo $seconds ?>&page=" + page;
                });
            });
        </script>
    </head>
    <body>
        <div class="modal-inner-content" style="padding-bottom: 30px;">
            <p>
                Search by entering the beginning of the station name/id (or just click search to list all).
            </p>

            <form id="station-search-form" method="get" action="">
                <div style="margin-bottom: 5px;">
                    <select name ="seconds" style="width: 280px;">
                        <option <?php echo ($seconds == 0 ? 'selected' : ''); ?> value="0">Include all known stations in search</option>
                        <option <?php echo ($seconds == 60 ? 'selected' : ''); ?> value="60">Only stations active latest hour</option>
                        <option <?php echo ($seconds == 120 ? 'selected' : ''); ?> value="120">Only stations active latest 2 hours</option>
                        <option <?php echo ($seconds == 360 ? 'selected' : ''); ?> value="360">Only stations active latest 6 hours</option>
                        <option <?php echo ($seconds == 720 ? 'selected' : ''); ?> value="720">Only stations active latest 12 hours</option>
                        <option <?php echo ($seconds == 3600 ? 'selected' : ''); ?> value="3600">Only stations active latest 24 hours</option>
                    </select>
                </div>
                <div>
                    <input type="text" style="width: 280px; margin-bottom: 5px;" name="q" placeholder="Search here!" title="Search for a station/vehicle here!" value="<?php echo ($_POST['q'] ?? '') ?>">
                    <input type="submit" value="Search">
                </div>
            </form>

            <div style="clear: both;"></div>

            <?php if (count($stations) > 0) : ?>
                <p>
                    <?php echo $count; ?> result(s):
                </p>

                <?php if ($pages > 1): ?>
                    <div class="pagination">
                      <a href="#"><<</a>
                      <?php for($i = max(1, $page - 3); $i <= min($pages, $page + 3); $i++) : ?>
                      <a href="#" <?php echo ($i == $page ? 'class="active"': '')?>><?php echo $i ?></a>
                      <?php endfor; ?>
                      <a href="#">>></a>
                    </div>
                <?php endif; ?>

                <div class="datagrid datagrid-search" style="max-width:1000px;">
                    <table>
                        <thead>
                            <tr>
                                <th>&nbsp;</th>
                                <th>Name/Id</th>
                                <th>Latest heard</th>
                                <th>Comment/Other</th>
                                <th>Map</th>

                            </tr>
                        </thead>
                        <tbody>
                        <?php foreach ($stations as $foundStation) : ?>
                            <tr>
                                <td>
                                    <img src="<?php echo $foundStation->getIconFilePath(22, 22); ?>" alt="Symbol"/>
                                </td>
                                <td>
                                    <a href="/station/overview.php?id=<?php echo $foundStation->id; ?>&imperialUnits=<?php echo $_GET['imperialUnits'] ?? 0; ?>"><?php echo htmlentities($foundStation->name) ?></a>
                                </td>
                                <td class="station-latest-heard-timestamp" style="white-space: nowrap;">
                                    <?php echo $foundStation->latestConfirmedPacketTimestamp; ?>
                                </td>
                                <td>
                                    <?php if ($foundStation->sourceId == 5 && $foundStation->getOgnDevice() !== null) : ?>
                                        <div style="width: 100px; display: inline-block;">Registration:</div><?php echo htmlspecialchars($foundStation->getOgnDevice()->registration); ?><br/>
                                        <div style="width: 100px; display: inline-block;">Aircraft Model:</div><?php echo htmlspecialchars($foundStation->getOgnDevice()->aircraftModel); ?>
                                    <?php else : ?>
                                        <?php $latestPacket = PacketRepository::getInstance()->getObjectById($foundStation->latestPacketId, $foundStation->latestPacketTimestamp); ?>
                                        <?php echo htmlspecialchars($latestPacket->comment); ?>
                                    <?php endif; ?>
                                </td>
                                <td>
                                    <?php if ($foundStation->latestConfirmedPacketTimestamp > (time() - 60*60*24)) : ?>
                                        <a href="?sid=<?php echo $foundStation->id; ?>" onclick="
                                            if (window.parent && window.parent.trackdirect) {
                                                $('.modal', parent.document).hide();
                                                window.parent.trackdirect.filterOnStationId([]);
                                                window.parent.trackdirect.filterOnStationId([<?php echo $foundStation->id; ?>]);
                                                return false;
                                            }">Map</a>
                                    <?php else : ?>
                                        &nbsp;
                                    <?php endif; ?>
                                </td>
                            </tr>
                        <?php endforeach; ?>
                        </tbody>
                    </table>
                </div>
            <?php endif; ?>

            <?php if (isset($_GET['q']) && count($stations) == 0) : ?>
                <p>
                    <b><i>No stations packets found.</i></b>
                </p>
            <?php endif; ?>
        </div>
    </body>
</html>
