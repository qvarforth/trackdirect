<?php require dirname(__DIR__) . "../../includes/bootstrap.php"; ?>

<?php $station = StationRepository::getInstance()->getObjectById($_GET['id'] ?? null); ?>
<?php if ($station->isExistingObject()) : ?>
    <title><?php echo $station->name; ?> Overview</title>
    <div class="modal-inner-content">
        <div class="modal-inner-content-menu">
            <span>Overview</span>
            <a class="tdlink" title="Statistics" href="/views/statistics.php?id=<?php echo $station->id ?>&imperialUnits=<?php echo $_GET['imperialUnits'] ?? 0; ?>">Statistics</a>
            <a class="tdlink" title="Trail Chart" href="/views/trail.php?id=<?php echo $station->id ?>&imperialUnits=<?php echo $_GET['imperialUnits'] ?? 0; ?>">Trail Chart</a>
            <a class="tdlink" title="Weather" href="/views/weather.php?id=<?php echo $station->id ?>&imperialUnits=<?php echo $_GET['imperialUnits'] ?? 0; ?>">Weather</a>
            <a class="tdlink" title="Telemetry" href="/views/telemetry.php?id=<?php echo $station->id ?>&imperialUnits=<?php echo $_GET['imperialUnits'] ?? 0; ?>">Telemetry</a>
            <a class="tdlink" title="Raw packets" href="/views/raw.php?id=<?php echo $station->id ?>&imperialUnits=<?php echo $_GET['imperialUnits'] ?? 0; ?>">Raw packets</a>
        </div>

        <div class="horizontal-line">&nbsp;</div>

        <div class="overview-content-summary">
            <div>
                <div class="overview-content-summary-hr">
                    <?php if ($station->sourceId == 5) : ?>
                        ID:
                    <?php else: ?>
                        Name:
                    <?php endif; ?>
                </div>
                <div class="overview-content-station" title="Name of the station/object">
                    <?php echo htmlentities($station->name); ?>
                </div>
            </div>

            <div>
                <div class="overview-content-summary-hr">
                    Station ID:
                </div>
                <div class="overview-content-station" title="Website station id">
                    <?php echo $station->id; ?>
                </div>
            </div>

            <?php if ($station->sourceId != null) : ?>
                <div>
                    <div class="overview-content-summary-hr">Source:</div>
                    <div class="overview-content-station" title="Source of this station">
                        <?php echo $station->getSourceDescription(); ?>
                    </div>
                </div>
            <?php endif; ?>

            <?php if ($station->getOgnDevice() !== null) : ?>
                <br/>
                <?php if ($station->getOgnDevice()->registration != null) : ?>
                    <div>
                        <div class="overview-content-summary-hr">Aircraft Registration:</div>
                        <div class="overview-content-station" title="Aircraft Registration">
                            <b><?php echo htmlspecialchars($station->getOgnDevice()->registration); ?></b>
                        </div>
                    </div>
                <?php endif; ?>

                <?php if ($station->getOgnDevice()->cn != null) : ?>
                    <div>
                        <div class="overview-content-summary-hr">Aircraft CN:</div>
                        <div class="overview-content-station" title="Aircraft CN">
                            <b><?php echo htmlspecialchars($station->getOgnDevice()->cn); ?></b>
                        </div>
                    </div>
                <?php endif; ?>
            <?php endif; ?>

            <?php if ($station->getOgnDdbAircraftTypeName() !== null) : ?>
                <div>
                    <div class="overview-content-summary-hr">Aircraft Type:</div>
                    <div class="overview-content-station" title="Type of aircraft">
                        <?php echo htmlspecialchars($station->getOgnDdbAircraftTypeName()); ?>
                    </div>
                </div>
                <?php if ($station->getOgnDevice()->aircraftModel != null) : ?>
                    <div>
                        <div class="overview-content-summary-hr">Aircraft Model:</div>
                        <div class="overview-content-station" title="Aircraft Model">
                            <?php echo htmlspecialchars($station->getOgnDevice()->aircraftModel); ?>
                        </div>
                    </div>
                <?php endif; ?>
            <?php elseif ($station->getOgnAircraftTypeName() != null) : ?>
                <div>
                    <div class="overview-content-summary-hr">Aircraft Type:</div>
                    <div class="overview-content-station" title="Type of aircraft">
                        <?php echo htmlspecialchars($station->getOgnAircraftTypeName()); ?>
                    </div>
                </div>
            <?php else : ?>
                <div>
                    <div class="overview-content-summary-hr">Symbol:</div>
                    <div class="overview-content-station" title="Symbol type">
                        <img src="<?php echo $station->getIconFilePath(24, 24); ?>" alt="Latest symbol" />
                        <span>&nbsp;<?php echo htmlentities($station->getLatestSymbolDescription()); ?></span>
                    </div>
                </div>
            <?php endif; ?>

            <!-- Latest Packet -->
            <?php if ($station->latestPacketId !== null) : ?>
                <?php $latestPacket = PacketRepository::getInstance()->getObjectById($station->latestPacketId, $station->latestPacketTimestamp); ?>
                <div class="overview-content-divider"></div>

                <div>
                    <div class="overview-content-summary-hr">Latest Packet:</div>
                    <div class="overview-content-summary-cell-type overview-content-summary-indent"><?php echo $latestPacket->getPacketTypeName(); ?> Packet</div>
                </div>

                <?php $latestPacketSender = SenderRepository::getInstance()->getObjectById($latestPacket->senderId); ?>
                <?php if ($latestPacketSender->name != $station->name) : ?>
                <div>
                    <div class="overview-content-summary-hr-indent">Sender:</div>
                    <div class="overview-content-summary-indent" title="Sender of current packet">
                        <?php $latestPacketSenderStation = StationRepository::getInstance()->getObjectByNameAndSenderId($latestPacketSender->name, $latestPacketSender->id); ?>
                        <?php if ($latestPacketSenderStation->isExistingObject()) : ?>
                            <a class="tdlink" title="Sender of the object" href="/views/overview.php?id=<?php echo $latestPacketSenderStation->id; ?>&imperialUnits=<?php echo $_GET['imperialUnits'] ?? 0; ?>">
                                <?php echo htmlentities($latestPacketSenderStation->name); ?>
                            </a>
                        <?php else : ?>
                            <?php echo $latestPacketSender->name; ?>
                        <?php endif; ?>
                    </div>
                </div>
                <?php endif; ?>

                <div>
                    <div class="overview-content-summary-hr-indent">Receive Time:</div>
                    <div title="Timestamp of the latest packet" id="latest-timestamp" class="overview-content-summary-cell-time overview-content-summary-indent">
                        <?php echo $station->latestPacketTimestamp; ?>
                    </div>
                </div>


                <div>
                    <div class="overview-content-summary-hr-indent">Age:</div>
                    <div title="Age of the latest packet" id="latest-timestamp-age" class="overview-content-summary-cell-time overview-content-summary-indent">
                        <?php echo $station->latestPacketTimestamp; ?>
                    </div>
                </div>


                <div>
                    <div class="overview-content-summary-hr-indent">Path:</div>
                    <div class="overview-content-summary-cell-path overview-content-summary-indent" title="Latest path"><?php echo $latestPacket->rawPath; ?></div>
                </div>

                <?php if ($latestPacket->comment != '') : ?>
                    <div>
                        <div class="overview-content-summary-hr-indent">Comment:</div>
                        <div title="Comment found in thelatest packet" id="latest-packet-comment" class="overview-content-summary-indent">
                            <?php echo htmlentities($latestPacket->comment); ?>
                        </div>
                    </div>
                <?php endif;?>

                <?php if ($latestPacket->getPacketOgn()->isExistingObject()) : ?>
                    <div style="line-height: 8px">&nbsp;</div>
                    <?php if ($latestPacket->getPacketOgn()->ognSignalToNoiseRatio !== null) : ?>
                        <div>
                            <div class="overview-content-summary-hr-indent">Signal to Noise Ratio:</div>
                            <div class="overview-content-summary-indent" title="Signal to Noise Ratio measured upon reception"><?php echo $latestPacket->getPacketOgn()->ognSignalToNoiseRatio; ?> dB</div>
                        </div>
                    <?php endif;?>

                    <?php if ($latestPacket->getPacketOgn()->ognBitErrorsCorrected !== null) : ?>
                        <div>
                            <div class="overview-content-summary-hr-indent">Bits corrected:</div>
                            <div class="overview-content-summary-indent" title="The number of bit errors corrected in the packet upon reception"><?php echo $latestPacket->getPacketOgn()->ognBitErrorsCorrected; ?></div>
                        </div>
                    <?php endif;?>

                    <?php if ($latestPacket->getPacketOgn()->ognFrequencyOffset !== null) : ?>
                        <div>
                            <div class="overview-content-summary-hr-indent">Frequency Offset:</div>
                            <div class="overview-content-summary-indent" title="The frequency offset measured upon reception"><?php echo $latestPacket->getPacketOgn()->ognFrequencyOffset; ?> kHz</div>
                        </div>
                    <?php endif;?>
                <?php endif;?>

            <?php endif;?>


            <!-- Latest Weather -->
            <?php if ($station->latestWeatherPacketTimestamp !== null) : ?>
                <div class="overview-content-divider"></div>

                <div>
                    <div class="overview-content-summary-hr">Latest Weather:</div>
                    <div id="weather-timestamp" class="overview-content-summary-cell-weather-time" title="Latest received weather">
                        <?php echo $station->latestWeatherPacketTimestamp; ?>
                    </div>
                </div>

                <?php if ($station->latestWeatherPacketComment != '') : ?>
                    <div>
                        <div class="overview-content-summary-hr-indent">Comment/Software:</div>
                        <div class="overview-content-summary-cell-time overview-content-summary-indent" title="Weather packet comment/software">
                            <?php echo htmlentities($station->latestWeatherPacketComment); ?><br/>
                        </div>
                    </div>
                <?php endif;?>
            <?php endif;?>

            <!-- Latest Telemetry -->
            <?php if ($station->latestTelemetryPacketTimestamp !== null) : ?>
                <div class="overview-content-divider"></div>

                <div>
                    <div class="overview-content-summary-hr">Latest Telemetry:</div>
                    <div id="telemetry-timestamp" class="overview-content-summary-cell-telemetry-time" title="Latest received telemetry">
                        <?php echo $station->latestTelemetryPacketTimestamp; ?>
                    </div>
                </div>
            <?php endif;?>

            <!-- Latest Position -->
            <?php if ($station->latestConfirmedPacketId !== null) : ?>

                <div class="overview-content-divider"></div>

                <div>
                    <div class="overview-content-summary-hr">Latest Position:</div>
                    <div id="overview-content-latest-position" class="overview-content-summary-cell-position" title="Latest position (that is approved by our filters)">
                        <?php echo round($station->latestConfirmedLatitude, 5); ?>, <?php echo round($station->latestConfirmedLongitude, 5); ?>
                    </div>
                </div>
                <div>
                    <div class="overview-content-summary-hr-indent">Gridsquare:</div>
                    <div id="overview-content-latest-gridsquare" class="overview-content-summary-cell-position" title="Maidenhead gridsquare (calculated from position)">
                    </div>
                </div>

                <div>
                    <div class="overview-content-summary-hr-indent">Receive Time:</div>
                    <div id="position-timestamp" class="overview-content-summary-cell-time overview-content-summary-indent" title="Latest position receive time">
                        <?php if ($station->latestPacketId == $station->latestConfirmedPacketId && $station->latestPacketTimestamp == $station->latestConfirmedPacketTimestamp) : ?>
                            (Received in latest packet)
                        <?php else : ?>
                            <?php echo $station->latestConfirmedPacketTimestamp; ?>
                        <?php endif; ?>
                    </div>
                </div>
                <div>
                    <div class="overview-content-summary-hr">&nbsp;</div>
                    <div class="overview-content-summary-cell-position">
                        <a href="?sid=<?php echo $station->id; ?>" onclick="
                            if (window.parent && window.parent.trackdirect) {
                                $('.modal', parent.document).hide();
                                window.parent.trackdirect.filterOnStationId([]);
                                window.parent.trackdirect.filterOnStationId([<?php echo $station->id; ?>]);
                                return false;
                            }">Show on map</a>
                    </div>
                </div>


                <?php $latestConfirmedPacket = PacketRepository::getInstance()->getObjectById($station->latestConfirmedPacketId, $station->latestConfirmedPacketTimestamp); ?>
                <?php if ($latestConfirmedPacket->isExistingObject() && $latestConfirmedPacket->posambiguity > 0) : ?>
                <div>
                    <div class="overview-content-summary-hr-indent">Posambiguity:</div>
                    <div class="overview-content-summary-cell-posambiguity overview-content-summary-indent" title="If posambiguity is active the gps position is inaccurate">Yes</div>
                </div>
                <?php endif;?>

                <?php if ($latestConfirmedPacket->isExistingObject()) : ?>
                    <?php if ($latestConfirmedPacket->speed != '' || $latestConfirmedPacket->course != '' || $latestConfirmedPacket->altitude != '') : ?>
                        <?php if (round($latestConfirmedPacket->speed) != 0 || round($latestConfirmedPacket->course) != 0 || round($latestConfirmedPacket->altitude) != 0) : ?>

                            <?php if ($latestConfirmedPacket->speed != '') : ?>
                            <div>
                                <div class="overview-content-summary-hr-indent">Speed:</div>
                                <div title="Latest speed" class="overview-content-summary-indent">
                                    <?php if (isImperialUnitUser()) : ?>
                                        <?php echo round(convertKilometerToMile($latestConfirmedPacket->speed), 2); ?> mph
                                    <?php else : ?>
                                        <?php echo round($latestConfirmedPacket->speed, 2); ?> km/h
                                    <?php endif; ?>
                                </div>
                            </div>
                            <?php endif;?>

                            <?php if ($latestConfirmedPacket->course != '') : ?>
                            <div>
                                <div class="overview-content-summary-hr-indent">Course:</div>
                                <div title="Latest course" class="overview-content-summary-indent"><?php echo $latestConfirmedPacket->course; ?>&deg;</div>
                            </div>
                            <?php endif;?>

                            <?php if ($latestConfirmedPacket->altitude != '') : ?>
                            <div>
                                <div class="overview-content-summary-hr-indent">Altitude:</div>
                                <div title="Latest altitude" class="overview-content-summary-indent">
                                    <?php if (isImperialUnitUser()) : ?>
                                        <?php echo round(convertMeterToFeet($latestConfirmedPacket->altitude), 2); ?> ft
                                    <?php else : ?>
                                        <?php echo round($latestConfirmedPacket->altitude, 2); ?> m
                                    <?php endif; ?>
                                </div>
                            </div>
                            <?php endif;?>

                        <?php endif;?>
                    <?php endif;?>

                    <?php if ($latestConfirmedPacket->getPacketOgn()->isExistingObject()) : ?>
                        <?php if ($latestConfirmedPacket->getPacketOgn()->ognClimbRate !== null) : ?>
                            <div>
                                <div class="overview-content-summary-hr-indent">Climb Rate:</div>
                                <div class="overview-content-summary-indent" title="The climb rate in feet-per-minute"><?php echo $latestConfirmedPacket->getPacketOgn()->ognClimbRate; ?> fpm</div>
                            </div>
                        <?php endif;?>

                        <?php if ($latestConfirmedPacket->getPacketOgn()->ognTurnRate !== null) : ?>
                            <div>
                                <?php $turnRateNote = true; ?>
                                <div class="overview-content-summary-hr-indent">Turn Rate:</div>
                                <div class="overview-content-summary-indent" title="Current turn rate."><?php echo $latestConfirmedPacket->getPacketOgn()->ognTurnRate; ?> rot</div>
                            </div>
                        <?php endif;?>
                    <?php endif;?>
                <?php endif;?>

                <!-- Latest PHG and RNG -->
                <?php if ($latestConfirmedPacket && $latestConfirmedPacket->isExistingObject()) : ?>
                    <?php if ($latestConfirmedPacket->phg != null || $latestConfirmedPacket->latestPhgTimestamp != null) : ?>
                        <div class="overview-content-divider"></div>
                        <div>
                            <div class="overview-content-summary-hr">Latest PHG:</div>
                            <div class="overview-content-summary-cell-phg" title="Power-Height-Gain (and directivity)">
                                <?php echo $latestConfirmedPacket->getPHGDescription(true); ?><br/>
                                (Calculated range:
                                    <?php if (isImperialUnitUser()) : ?>
                                        <?php echo round(convertKilometerToMile($latestConfirmedPacket->getPHGRange(true)/1000),2); ?> miles)
                                    <?php else : ?>
                                        <?php echo round($latestConfirmedPacket->getPHGRange(true)/1000,2); ?> km)
                                    <?php endif; ?>
                            </div>
                        </div>
                    <?php endif;?>

                    <?php if ($latestConfirmedPacket->rng != null || $latestConfirmedPacket->latestRngTimestamp != null) : ?>
                        <div class="overview-content-divider"></div>
                        <div>
                            <div class="overview-content-summary-hr">Latest RNG:</div>
                            <div class="overview-content-summary-cell-phg" title="The pre-calculated radio range">
                                <?php if (isImperialUnitUser()) : ?>
                                    <?php echo round(convertKilometerToMile($latestConfirmedPacket->getRng(true)), 2); ?> miles
                                <?php else : ?>
                                    <?php echo round($latestConfirmedPacket->getRng(true), 2); ?> km
                                <?php endif; ?>
                            </div>
                        </div>
                    <?php endif;?>
                <?php endif;?>
            <?php endif;?>

            <!-- Latest Symbols -->
            <?php $stationLatestSymbols = $station->getLatestIconFilePaths(22, 22); ?>
            <?php if ($stationLatestSymbols !== null && count($stationLatestSymbols) > 1) : ?>
                <div class="overview-content-divider"></div>
                <div>
                    <div class="overview-content-summary-hr">Latest used symbols:</div>
                    <div title="Latest symbols that this station has used">
                        <?php foreach ($stationLatestSymbols as $symbolPath) : ?>
                            <img src="<?php echo $symbolPath; ?>" alt="Symbol"/>&nbsp;
                        <?php endforeach; ?>
                    </div>
                </div>
            <?php endif; ?>


            <!-- Packet Frequency -->
            <?php $packetFrequencyNumberOfPackets = null; ?>
            <?php $stationPacketFrequency = $station->getPacketFrequency(null, $packetFrequencyNumberOfPackets); ?>
            <?php if ($stationPacketFrequency != null) : ?>
                <div class="overview-content-divider"></div>
                <div>
                    <div class="overview-content-summary-hr">Packet frequency:</div>
                    <div class="overview-content-packet-frequency" title="Calculated packet frequency"><span><?php echo $stationPacketFrequency; ?>s</span> <span>(Latest <?php echo $packetFrequencyNumberOfPackets; ?> packets)</span></div>
                </div>
            <?php endif; ?>


            <div class="overview-content-divider"></div>
        </div>

        <div class="overview-content-symbol" id ="overview-content-symbol-<?php echo $station->id; ?>">
            <img src="<?php echo $station->getIconFilePath(150, 150); ?>" alt="Latest symbol" title="<?php echo $station->getLatestSymbolDescription(); ?>"/>
            <?php if ($station->latestPacketId !== null) : ?>
                <br/>
                <div style="text-align: center; padding-top: 30px;">
                    <?php if ($station->getOgnDevice() !== null && $station->getOgnDevice()->registration != null) : ?>
                        <div>
                            Search for <a href="https://www.jetphotos.com/registration/<?php echo $station->getOgnDevice()->registration; ?>" target="_blank"><?php echo htmlspecialchars($station->getOgnDevice()->registration); ?></a> photos!
                        </div>
                    <?php endif; ?>

                    <?php if ($station->sourceId == 1) : ?>
                        <?php if ($station->getLiklyHamRadioCallsign() !== null) : ?>
                            <div>Search for <a href="https://www.qrz.com/db/<?php echo $station->getLiklyHamRadioCallsign(); ?>" target="_blank"><?php echo htmlspecialchars($station->getLiklyHamRadioCallsign()); ?></a> at QRZ</div>
                        <?php endif; ?>
                    <?php endif; ?>

                    <div>Export <a href="/data/kml.php?id=<?php echo $station->id; ?>"><?php echo htmlspecialchars($station->name); ?></a> data to KML</div>
                </div>
                <div style="clear: both;"></div>
            <?php endif; ?>
        </div>

        <div class="horizontal-line">&nbsp;</div>

        <div class="overview-content-summary">

            <!-- Related stations -->
            <?php $relatedStations = StationRepository::getInstance()->getRelatedObjectListByStationId($station->id, 15); ?>
            <?php if (count($relatedStations) > 1) : ?>
                <div>
                    <?php $relatedStattionNote = true; ?>
                    <div class="overview-content-summary-hr">Related stations/objects:</div>
                    <div class="overview-content-station-list" title="Stations with same call except SSID or objects with related sender">
                        <?php foreach ($relatedStations as $relatedStation) : ?>
                            <?php if ($relatedStation->id != $station->id) : ?>
                                <img src="<?php echo $relatedStation->getIconFilePath(22, 22); ?>" alt="Symbol"/>&nbsp;
                                <span><a class="tdlink" href="/views/overview.php?id=<?php echo $relatedStation->id; ?>&imperialUnits=<?php echo $_GET['imperialUnits'] ?? 0; ?>"><?php echo htmlentities($relatedStation->name) ?></a></span>
                                <br/>
                            <?php endif; ?>
                        <?php endforeach; ?>
                    </div>
                </div>
                <div class="overview-content-divider"></div>
            <?php endif; ?>


            <!-- Close by stations -->
            <?php $closeByStations = StationRepository::getInstance()->getCloseByObjectListByStationId($station->id, 15); ?>
            <?php if (count($closeByStations) > 1) : ?>
                <div>
                    <div class="overview-content-summary-hr">Nearby stations/objects:</div>
                    <div class="overview-content-station-list" title="The closest stations/objects at the current position">
                        <?php foreach ($closeByStations as $closeByStation) : ?>
                            <?php if ($closeByStation->id != $station->id) : ?>

                                <img src="<?php echo $closeByStation->getIconFilePath(22, 22); ?>" alt="Symbol"/>&nbsp;
                                <span>
                                    <a class="tdlink" href="/views/overview.php?id=<?php echo $closeByStation->id; ?>&imperialUnits=<?php echo $_GET['imperialUnits'] ?? 0; ?>"><?php echo htmlentities($closeByStation->name) ?></a>
                                    <span>
                                        <?php if (isImperialUnitUser()) : ?>
                                            <?php if (convertMeterToYard($closeByStation->getDistance($station->latestConfirmedLatitude, $station->latestConfirmedLongitude)) < 1000) : ?>
                                                <?php echo round(convertMeterToYard($closeByStation->getDistance($station->latestConfirmedLatitude, $station->latestConfirmedLongitude)), 0); ?> yd
                                            <?php else : ?>
                                                <?php echo round(convertKilometerToMile($closeByStation->getDistance($station->latestConfirmedLatitude, $station->latestConfirmedLongitude) / 1000), 2); ?> miles
                                            <?php endif; ?>
                                        <?php else : ?>
                                            <?php if ($closeByStation->getDistance($station->latestConfirmedLatitude, $station->latestConfirmedLongitude) < 1000) : ?>
                                                <?php echo round($closeByStation->getDistance($station->latestConfirmedLatitude, $station->latestConfirmedLongitude), 0); ?> m
                                            <?php else : ?>
                                                <?php echo round($closeByStation->getDistance($station->latestConfirmedLatitude, $station->latestConfirmedLongitude) / 1000, 2); ?> km
                                            <?php endif; ?>
                                        <?php endif; ?>
                                    </span>

                                </span>
                            <br/>
                            <?php endif; ?>
                        <?php endforeach; ?>
                    </div>
                </div>
                <div class="overview-content-divider"></div>
            <?php endif; ?>
        </div>

        <?php if (count($relatedStations) > 1 || count($closeByStations) > 1) : ?>
            <div class="horizontal-line">&nbsp;</div>
        <?php endif; ?>

        <div class="overview-content-explanations">
            <ul>
                <li>The specified "Station ID" is the ID that this station has on this website, this ID is useful when creating a link to this website. Read more in the About/FAQ.</li>

                <?php if ($station->sourceId == 5) : ?>
                    <li>Packets is received from the <a target="_blank" href="http://wiki.glidernet.org/">Open Glider Network</a>. The goal of the Open Glider Network project is to create a unified platform for tracking aircraft equipped with FLARM and OGN trackers.</li>

                    <li>Aircraft device details such as Registration, CN and Aircraft Model is collected from the <a target="_blank" href="http://wiki.glidernet.org/ddb">OGN Devices DataBase</a>. We will only display information that can be used to identify an aircraft if the aircraft device details exists in the OGN Devices DataBase, and if the setting "I don't want this device to be identified" is deactivated.</li>

                    <li>Detailed aircraft information is received from the <a target="_blank" rel="nofollow" href="http://wiki.glidernet.org/ddb">OGN Devices DataBase</a>. If the aircraft is not registered in the <a target="_blank" rel="nofollow" href="http://wiki.glidernet.org/ddb">OGN Devices DataBase</a> or if the aircraft does not want to be identified, the aircraft type indicated in the FLARM/OGN packet is displayed (but only if the website is configured to show aircrafts not registered in the database, that setting is not enabled by default). We also adapt which symbol that is used based on the selected aircraft type.</li>

                    <li>According to <a target="_blank" href="http://wiki.glidernet.org/">OGN</a>, 4-5dB is about the limit of meaningful reception (but currently we still save packets with low SNR).</li>

                    <li>According to <a target="_blank" href="http://wiki.glidernet.org/">OGN</a>, it is recommended that you ignore packets that have a high CRC error rate (>5) as their information may be corrupt (but currently we still save packets with high CRC error rate).</li>

                    <li>1rot is the standard aircraft rotation rate of 1 half-turn per minute (equal to 1.5&deg; per second).</li>
                <?php endif; ?>

                <?php if ($station->sourceId == 1) : ?>
                    <li>To get a better understanding of the APRS path I recommend reading <a target="_blank" rel="nofollow" href="http://wa8lmf.net/DigiPaths/">the explanation written by wa8lmf</a>.</li>

                    <li>If this packet has the "Posambiguity"-mark it means that the sent position is ambiguous (a configured number of digits has been truncated from the end of the position).</li>

                    <li>PHG stands for Power-Height-Gain (and directivity). The height is not the height above sea-level, it is the height above average terrain (HAAT = Height Above Average Terrain). PHG is used to calculate the relative RF range of a station. If this station has reported several positions or symbols the PHG data will only be used for the position and symbol used in the PHG-packet.</li>

                    <li>RNG is the "pre-calculated omni-directional radio range" of the station (reported by the station itself). If this station has reported several positions or symbols the RNG data will only be used for the position and symbol used in the RNG-packet. It seems like many D-STAR station use the RNG value to specifify D-STAR range.</li>

                    <li>One object may be sent by several different senders. On the map they may share the same path, but they all have their own "Station information" modal.</li>

                    <li>If station has more than 15 related stations we will only show the 10 closest related stations.</li>
                <?php endif; ?>

                <?php if ($station->sourceId == 2) : ?>
                    <li>Station data is received from the CWOP network (Citizen Weather Observer Program). Visit <a href="http://www.wxqa.com/cwop_info.htm" target="_blank">CWOP Information</a> if you want know more!</li>


                <?php endif; ?>

            </ul>
        </div>
    </div>

    <script>
        $(document).ready(function() {
            var locale = window.navigator.userLanguage || window.navigator.language;
            moment.locale(locale);

            $('#overview-content-comment, #overview-content-beacon, #overview-content-status').each(function() {
                if ($(this).html().trim() != '') {
                    $(this).html(Autolinker.link($(this).html()));
                }
            });

            $('#latest-timestamp, #comment-timestamp, #status-timestamp, #beacon-timestamp, #position-timestamp, #weather-timestamp, #telemetry-timestamp').each(function() {
                if ($(this).html().trim() != '' && !isNaN($(this).html().trim())) {
                    $(this).html(moment(new Date(1000 * $(this).html())).format('L LTSZ'));
                }
            });

            if ($('#latest-timestamp-age').length && $('#latest-timestamp-age').html().trim() != '' && !isNaN($('#latest-timestamp-age').html().trim())) {
                $('#latest-timestamp-age').html(moment(new Date(1000 * $('#latest-timestamp-age').html())).locale('en').fromNow());
            }

            $('#overview-content-latest-gridsquare').html(trackdirect.models.Map.prototype._getMaidenheadLocatorFromGpsDecimal(<?php echo $station->latestConfirmedLatitude ?>, <?php echo $station->latestConfirmedLongitude ?>));

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
