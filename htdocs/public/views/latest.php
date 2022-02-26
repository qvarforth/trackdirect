<?php require dirname(__DIR__) . "../../includes/bootstrap.php"; ?>

<?php
    $stations = [];
    $seconds = 60*60*24;
    $page = $_GET['page'] ?? 1;
    $rows = 50;
    $offset = ($page - 1) * $rows;

    $stations = StationRepository::getInstance()->getObjectList($seconds, $rows, $offset);
    $count = StationRepository::getInstance()->getNumberOfStations($seconds);

    $pages = ceil($count / $rows);
?>

<title>Latest heard stations</title>
<div class="modal-inner-content" style="padding-bottom: 30px;">
    <?php if (count($stations) > 0) : ?>
        <p>
            <?php echo $count; ?> station(s) have been heard in the last 24 hours.
        </p>

        <?php if ($pages > 1): ?>
            <div class="pagination">
              <a class="tdlink" href="/views/latest.php?q=<?php echo ($_GET['q'] ?? "") ?>&seconds=<?php echo $seconds ?>&page=1"><<</a>
              <?php for($i = max(1, $page - 3); $i <= min($pages, $page + 3); $i++) : ?>
              <a href="/views/latest.php?q=<?php echo ($_GET['q'] ?? "") ?>&seconds=<?php echo $seconds ?>&page=<?php echo $i; ?>" <?php echo ($i == $page ? 'class="tdlink active"': 'class="tdlink"')?>><?php echo $i ?></a>
              <?php endfor; ?>
              <a class="tdlink" href="/views/latest.php?q=<?php echo ($_GET['q'] ?? "") ?>&seconds=<?php echo $seconds ?>&page=<?php echo $pages; ?>">>></a>
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
                            <a class="tdlink" href="/views/overview.php?id=<?php echo $foundStation->id; ?>&imperialUnits=<?php echo $_GET['imperialUnits'] ?? 0; ?>"><?php echo htmlentities($foundStation->name) ?></a>
                        </td>
                        <td class="station-latest-heard-timestamp" style="white-space: nowrap;">
                            <?php echo $foundStation->latestConfirmedPacketTimestamp; ?>
                        </td>
                        <td>
                            <?php if ($foundStation->sourceId == 5 && $foundStation->getOgnDevice() !== null) : ?>
                                <div style="width: 100px; display: inline-block;">Registration:</div><?php echo htmlspecialchars($foundStation->getOgnDevice()->registration); ?> <?php echo $foundStation->getOgnDevice()->cn ? '[' .htmlspecialchars($foundStation->getOgnDevice()->cn) . ']' : ''; ?><br/>
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

    <?php if (count($stations) == 0) : ?>
        <p>
            <b><i>No station have been heard in the last 24 hours.</i></b>
        </p>
    <?php endif; ?>
</div>
<script>
    $(document).ready(function() {
        var locale = window.navigator.userLanguage || window.navigator.language;
        moment.locale(locale);

        $('.station-latest-heard-timestamp').each(function() {
            if ($(this).html().trim() != '' && !isNaN($(this).html().trim())) {
                $(this).html(moment(new Date(1000 * $(this).html())).format('L LTSZ'));
            }
        });
    });
</script>
