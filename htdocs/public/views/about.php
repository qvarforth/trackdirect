<?php require dirname(__DIR__) . "../../includes/bootstrap.php"; ?>

<title>About / FAQ</title>
<div class="modal-inner-content modal-inner-content-about" style="padding-bottom: 30px;">
    <p>
	    Welcome to this APRS tracking website! Our goal is to bring you a fast and easy-to-use map with APRS data from <a href="http://www.aprs-is.net" target="_blank">APRS-IS</a>, <a href="http://www.wxqa.com" target="_blank">CWOP-IS</a>, <a href="https://www.glidernet.org" target="_blank">OGN</a> or some other APRS data source (depending on how this specific website is configured).
    </p>

    <p>
        This website is based on the APRS Track Direct tools. Read more about APRS Track Direct <a href="https://www.aprsdirect.com" target="_blank">here</a> or go directly to <a href="https://github.com/qvarforth/trackdirect" target="_blank">GitHub</a>. In addition to a map with fast APRS data updates, APRS Track direct also provides related functions such as <a href="/views/latest.php" class="tdlink" title="List latest heard stations">Latest heard</a> and <a href="/views/search.php" class="tdlink" title="Search for stations">Station search</a> etc.
    </p>

    <h2>What is APRS?</h2>
    <p>
        APRS (Automatic Packet Reporting System) is a digital communications system that uses packet radio to send real time tactical information (on amateur radio frequencies).
        The APRS network is used by ham radio operators all over the world.
        Information shared over the APRS network is for example coordinates, altitude, speed, heading, text messages, alerts, announcements, bulletins and weather data.
        APRS has been developed by Bob Bruninga, callsign WB4APR.
	More information about APRS can be found at <a target="_blank" rel="nofollow" href="http://www.aprs.org/">www.aprs.org</a> or at <a target="_blank" rel="nofollow" href="https://en.wikipedia.org/wiki/Automatic_Packet_Reporting_System">wikipedia</a>.
    </p>
    <p>
        But as you probably already understood, the APRS specification is not only used by ham radio operators, but also for several other areas of use, such as e.g. for CWOP and OGN data.
    </p>

    <h2>FAQ</h2>

    <h3>1. My latest packet seems to be using different path's depending on what website I look at (APRS-IS related). Why?</h3>
    <p>
        The websites you compare are not collecting packets from the same APRS-IS servers. Each APRS-IS server performes duplicate filtering, and which packet that is considered to be a duplicate may differ depending on which APRS-IS server you ask.
    </p>

    <h3>2. Where does the displayed data come from?</h3>
    <p>
        The data source for each station is specified, which may include
        <a href="http://www.aprs-is.net" target="_blank">APRS-IS</a>,
        <a href="http://www.wxqa.com" target="_blank">CWOP-IS</a>, or
        <a href="https://www.glidernet.org" target="_blank">OGN</a>.
    </p>

    <h3>3. How do I prevent my data from being displayed on websites such as this?</h3>
    <h4>A. Answer for APRS-IS/CWOP-IS and more</h4>
    <p>
        If you do not want your APRS data to be publiched on APRS-websites you can append <b>NOGATE</b> to the end of your path (or use <b>RFONLY</b>). If your digipeater path is <b>WIDE1-1,WIDE2-1</b>, you just change it to <b>WIDE1-1,WIDE2-1,NOGATE</b>.
    </p>

    <h4>B. Answer for OGN (Open Glider Network)</h4>
    <p>
        Not all information that is sent to the Open Glider Network is published.
    </p>
    <p>
        Aircrafts that meet any of the following condition is not shown at all.<br/>
        &rarr; Has the "no-tracking" flag in FLARM device configuration set.<br/>
        &rarr; Has activated the setting "I don't want this device to be tracked" in the the <a target="_blank" href="http://wiki.glidernet.org/ddb">OGN Devices DataBase</a>.
    </p>
    <p>
        This website will only display information that can be used to identify an aircraft if the aircraft device details exists in the <a target="_blank" href="http://wiki.glidernet.org/ddb">OGN Devices DataBase</a>, and if the setting "I don't want this device to be identified" is deactivated. If the website is configured to also render aircrafts that does not exists in the OGN database, the aircraft is given a temporary name that is only used for a maximum of 24h (to make sure it can not be identified).
    </p>
    <p>
        Read more about how to "Opt In" or "Opt Out" <a target="_blank" href="http://wiki.glidernet.org/opt-in-opt-out">here</a>.
    </p>

    <h3>4. How is the coverage map created?</h3>
    <p>
        Note that the coverage map is only available for receiving stations, it tries to show from which area the station is able to receive packets.
    </p>
    <p>
        The coverage map consists of two parts:
        <ul>
            <li><span>The heatmap that shows all recorded coordinates.</span></li>
            <li><span>The interpolated max range plot polygon that shows the coverage.</span></li>
        </ul>
    </p>
    <p>
        The max range plot is created by:
        <ol>
            <li><span>We exclude positions that have a distance that is further away than the 95th percentile.</span></li>
            <li><span>We use a convex hull algorithm to get a polygon of the covered area.</span></li>
            <li><span>We add some padding to the area received in the previous step. This step is just used to make the polygon look a bit nicer.</span></li>
        </ol>
    </p>

    <h3>5. How does the marker logic work?</h3>
    <ul>
        <li>Speed limit and other filters identify faulty positions.</li>
        <li>Unconfirmed packets are updated upon confirmation of direction.</li>
        <li>Moving stations with a sudden location change are connected by a dashed line.</li>
        <li>Animated direction polylines fade after 15 minutes.</li>
        <li>Hovering over markers shows dotted transmit paths.</li>
    </ul>

    <h3>6. Can I link to this website?</h3>
    <p>
        Yes absolutely!
    </p>
    <ul>
        <li>
            To link to a station tracking map view, use one of the following alternatives:
            <br/><span style="color:darkblue;">https://www.thiswebsite.com?sname=<b>STATION-NAME</b></span>
            <br/><span style="color:darkblue;">https://www.thiswebsite.com?sid=<b>STATION-ID</b></span>
        </li>
        <br/>
        <li>
            To link to a tracking map view for multiple stations, use one of the following alternatives:
            <br/><span style="color:darkblue;">https://www.thiswebsite.com?snamelist=<b>STATION-NAME-1,STATION-NAME-2,STATION-NAME-3</b></span>
            <br/><span style="color:darkblue;">https://www.thiswebsite.com?sidlist=<b>STATION-ID-1,STATION-ID-2,STATION-ID-3</b></span>
        </li>
        <br/>
        <li>
            To link to a map view, centered on a position, use the following:
            <br/><span style="color:darkblue;">https://www.thiswebsite.com?center=<b>LATITUDE</b>,<b>LONGITUDE</b>&zoom=<b>ZOOM-LEVEL</b></span>
        </li>

    </ul>
</div>
