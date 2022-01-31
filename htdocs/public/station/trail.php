<?php require "../../includes/bootstrap.php"; ?>

<?php $station = StationRepository::getInstance()->getObjectById($_GET['id'] ?? null); ?>
<?php if ($station->isExistingObject()) : ?>
    <!DOCTYPE html>
    <html lang="en">
        <head>
            <meta charset="utf-8" />
            <title><?php echo $station->name; ?> Trail Chart</title>
            <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=0"/>
            <meta name="apple-mobile-web-app-capable" content="yes"/>
            <meta name="mobile-web-app-capable" content="yes">

            <script src="https://cdnjs.cloudflare.com/ajax/libs/jquery/1.12.4/jquery.min.js" integrity="sha512-jGsMH83oKe9asCpkOVkBnUrDDTp8wl+adkB2D+//JtlxO4SrLoJdhbOysIFQJloQFD+C4Fl1rMsQZF76JjV0eQ==" crossorigin="anonymous"></script>
            <script src="https://cdnjs.cloudflare.com/ajax/libs/moment.js/2.29.1/moment-with-locales.min.js" integrity="sha512-LGXaggshOkD/at6PFNcp2V2unf9LzFq6LE+sChH7ceMTDP0g2kn6Vxwgg7wkPP7AAtX+lmPqPdxB47A0Nz0cMQ==" crossorigin="anonymous"></script>
            <script type="text/javascript" src="//www.gstatic.com/charts/loader.js"></script>

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

                    if (window.parent && window.parent.trackdirect) {
                        <?php if ($station->latestConfirmedLatitude != null && $station->latestConfirmedLongitude != null) : ?>
                        window.parent.trackdirect.focusOnStation(<?php echo $station->id ?>, true);
                        <?php endif; ?>
                    }

                    function loadTrailChart(stationId, hours, type, imperialUnits) {
                        $('#trail-curve-chart').html('Loading!');

                        $.ajax({
                            type: 'GET',
                            url: '/data/trail.php?id=' + stationId + '&hours=' + hours + '&type=' + type + '&imperialUnits=' + imperialUnits,
                            dataType: 'json'
                        }).done(function( result ) {
                            var onlyZeroValues = true;
                            for(i=1; i < result.length; i++) {
                                if (result[i][0] === parseInt(result[i][0], 10)) {
                                    result[i][0] = new Date(result[i][0] * 1000);
                                }

                                if (result[i][1] != 0 && result[i][1] != null) {
                                    onlyZeroValues = false;
                                }
                            }

                            var endTimestamp = new Date();
                            var startTimestamp = new Date(endTimestamp.getTime() - 1000*60*60*hours);

                            if (result != null && result.length > 1) {
                                google.charts.setOnLoadCallback(
                                    function () {
                                        var data = google.visualization.arrayToDataTable(result);

                                        var pointSize = 0; // default
                                        var dataOpacity = 1;
                                        var trigger = 'selection';
                                        var series = {
                                            0: { lineWidth: 2},
                                            1: { lineWidth: 1, color: 'darkgreen'},
                                        };
                                        var legend = {position: 'none'};
                                        var title = result[0][1];
                                        var curveType = 'none'; // can be 'function' or 'none'
                                        var vAxis = {};
                                        var hAxis = {
                                            minValue: startTimestamp,
                                            maxValue: endTimestamp
                                        };
                                        var explorer = {
                                            axis: 'horizontal',
                                            keepInBounds:true,
                                            maxZoomIn: 50,
                                            maxZoomOut: 1,
                                            actions: ['dragToPan', 'rightClickToReset']
                                        };
                                        explorer = null;

                                        if (result[0].length > 2) {
                                            // We need to show legend if we plot more than one thing
                                            legend = {position: 'top'};
                                            title = null;
                                        }

                                        if (onlyZeroValues) {
                                            // dot chart with big dots
                                            var series = {
                                                0: { lineWidth: 0, pointsVisible: true, pointSize: 4 },
                                            }
                                        } else if (hours < 24) {
                                            // line chart
                                            var series = {
                                                0: { lineWidth: 2, pointsVisible: false},
                                            }
                                        } else {
                                            // dot chart
                                            var series = {
                                                0: { lineWidth: 0, pointsVisible: true, pointSize: 1 },
                                            }
                                        }

                                        if (type == 'speed') {
                                            // I'm pretty sure we won't have negative speed
                                            var vAxis = {
                                                viewWindow : {
                                                    min: 0
                                                }
                                            };
                                        }

                                        var chartArea = {'width': '90%', 'height': '80%', 'left': '8%'};
                                        var options = {
                                            title: title,
                                            curveType: curveType,
                                            tooltip : {
                                              trigger: trigger
                                            },
                                            pointsVisible : false,
                                            pointSize: pointSize,
                                            dataOpacity: dataOpacity,
                                            series: series,
                                            chartArea: chartArea,
                                            legend: legend,
                                            hAxis: hAxis,
                                            vAxis: vAxis,
                                            interpolateNulls: false,
                                            crosshair: {
                                                trigger: 'focus',
                                                opacity: 0.5
                                            },
                                            explorer: explorer
                                        };

                                        var chart = new google.visualization.LineChart(document.getElementById('trail-curve-chart'));

                                        chart.draw(data, options);
                                    });

                            } else {
                                $('#trail-curve-chart').html('<br/><p><i><b>No trail data to create chart from.</b></i></p>');
                            }
                        });
                    }

                    google.charts.load('current', {'packages':['corechart', 'timeline']});

                    $('#trail-hours').change(function() {
                        loadTrailChart(<?php echo $station->id; ?>, $('#trail-hours').val(), $('#trail-type').val(), <?php echo $_GET['imperialUnits'] ?? 0; ?>);
                    });

                    $('#trail-type').change(function() {
                        loadTrailChart(<?php echo $station->id; ?>, $('#trail-hours').val(), $('#trail-type').val(), <?php echo $_GET['imperialUnits'] ?? 0; ?>);
                    });

                    loadTrailChart(<?php echo $station->id; ?>, $('#trail-hours').val(), $('#trail-type').val(), <?php echo $_GET['imperialUnits'] ?? 0; ?>);

                });
            </script>
        </head>
        <body>
            <div class="modal-inner-content">
                <div class="modal-inner-content-menu">
                    <a title="Overview" href="/station/overview.php?id=<?php echo $station->id ?>&imperialUnits=<?php echo $_GET['imperialUnits'] ?? 0; ?>">Overview</a>
                    <a title="Statistics" href="/station/statistics.php?id=<?php echo $station->id ?>&imperialUnits=<?php echo $_GET['imperialUnits'] ?? 0; ?>">Statistics</a>
                    <span>Trail Chart</span>
                    <a title="Weather" href="/station/weather.php?id=<?php echo $station->id ?>&imperialUnits=<?php echo $_GET['imperialUnits'] ?? 0; ?>">Weather</a>
                    <a title="Telemetry" href="/station/telemetry.php?id=<?php echo $station->id ?>&imperialUnits=<?php echo $_GET['imperialUnits'] ?? 0; ?>">Telemetry</a>
                    <a title="Raw packets" href="/station/raw.php?id=<?php echo $station->id ?>&imperialUnits=<?php echo $_GET['imperialUnits'] ?? 0; ?>">Raw packets</a>
                </div>

                <div class="horizontal-line">&nbsp;</div>

                <p>
                    Show chart for
                </p>


                <div class="form-container">
                    <select id="trail-type" style="float:left; margin-right: 5px;">
                        <option <?php echo (($_GET['type'] ?? 'speed') == 'speed' ? 'selected' : ''); ?> value="speed">Speed</option>
                        <option <?php echo (($_GET['type'] ?? 'speed') == 'altitude' ? 'selected' : ''); ?> value="altitude">Altitude</option>
                    </select>

                    <select id="trail-hours" style="float:left; margin-right: 5px;">
                        <option <?php echo (($_GET['hours'] ?? 1) == 1 ? 'selected' : ''); ?> value="1">Latest hour</option>
                        <option <?php echo (($_GET['hours'] ?? 1) == 3 ? 'selected' : ''); ?> value="3">Latest 3 hours</option>
                        <option <?php echo (($_GET['hours'] ?? 1) == 24 ? 'selected' : ''); ?> value="24">Latest 24 hours</option>
                    </select>
                </div>

                <div style="clear: both;"></div>

                <div id="trail-curve-chart" style="width:850px; height: 350px;"></div>

                <p>
                    * chart x-axis is based on your timezone (not the timezone of the station).
                </p>
            </div>
        </body>
    </html>
<?php endif; ?>