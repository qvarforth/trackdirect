<?php require dirname(__DIR__) . "../../includes/bootstrap.php"; ?>

<title>About / FAQ</title>
<div class="modal-inner-content modal-inner-content-about" style="padding-bottom: 30px;">
    <div class="modal-inner-content-menu">
        <a href="/views/about.php" class="tdlink" title="More about this website!">About</a>
        <span>FAQ</span>
    </div>
    <div class="horizontal-line">&nbsp;</div>

    <h2>1. I have a question. Who may I contact?</h2>
    <p>
        Maintainer of this website is <a href="mailto:<?php echo getWebsiteConfig('owner_email'); ?>"><?php echo getWebsiteConfig('owner_name'); ?></a>.
    </p>

    <h2>2. What is APRS?</h2>
    <p>
        APRS (Automatic Packet Reporting System) is a digital communications system that uses packet radio to send real time tactical information. The APRS network is used by ham radio operators all over the world.
    </p>
    <p>
        Information shared over the APRS network is for example coordinates, altitude, speed, heading, text messages, alerts, announcements, bulletins and weather data.
    </p>

    <h2>3. What is APRS Track Direct</h2>
    <p>
        This website is based on the APRS Track Direct tools. Read more on <a href="https://github.com/qvarforth/trackdirect" target="_blank">GitHub</a>. But please note that the maintainer of APRS Track Direct has nothing to do with this website.
    </p>

    <h2>4. I have a map created in <a target="_blank" href="https://mymaps.google.com/">Google My Maps</a>, can I render it on top of this map?</h2>
    <p>
        Sure! Follow the following instructions...
    </p>
    <ol>
        <li>Open your map at <a target="_blank" href="https://mymaps.google.com/">Google My Maps</a>.</li>
        <li>Look at the current URL and try to find a value named <b>mid</b>. Copy that value!</li>
        <li>Open this website. Add <b>"&mid={the mid value}"</b> to the end of the URL.</li>
        <li>Press Enter!</li>
    </ol>

    <h2>5. My latest packet seems to be using different path's depending on what website I look at (APRS-IS related). Why?</h2>
    <p>
        The websites you compare are not collecting packets from the same APRS-IS servers. Each APRS-IS server performes duplicate filtering, and which packet that is considered to be a duplicate may differ depending on which APRS-IS server you ask.
    </p>

    <h2>6. Where does the displayed data come from?</h2>
    <p>On each station you can see the specified source. APRS data can be received from <a href="http://www.aprs-is.net" target="_blank">APRS-IS</a>, <a href="http://www.wxqa.com" target="_blank">CWOP-IS</a> or <a href="https://www.glidernet.org" target="_blank">OGN</a> (and more).

    <h2>7. How do I prevent my data from being displayed on websites such as this?</h2>
    <h3>A. Answer for APRS-IS/CWOP-IS and more</h3>
    <p>
        If you do not want your APRS data to be publiched on APRS-websites you can append <b>NOGATE</b> to the end of your path (or use <b>RFONLY</b>). If your digipeater path is <b>WIDE1-1,WIDE2-1</b>, you just change it to <b>WIDE1-1,WIDE2-1,NOGATE</b>.
    </p>

    <h3>B. Answer for OGN (Open Glider Network)</h3>
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

    <h2>8. How is the coverage map created?</h2>
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

    <h2>9. Can you tell me how the marker logic works?</h2>
    <p>
        Okay, let me tell you more about our brilliant marker logic :-)
    </p>
    <ul>
        <li>We have a speed limit filter and other filters that sorts out packets that has a faulty position.</li>
        <li>If a moving station sends a packet that is sorted out by our speed limit filter the packet will be marked as unconfirmed, if we later receive a packet that confirmes that the station is moving in that direction, the previous packet will be confirmed then.</li>
        <li>If a station moves in one area and suddently appear in another area the two tails will be connected by a dashed polyline.</li>
        <li>A moving station that reports it's speed and direction will have an animated direction polyline (will be hidden after 15min).</li>
        <li>The dotted polyline shows the packet transmit path, will be shown when you hover over a marker or a "dotmarker". If a station in the path hasn't sent a position packet in a long time it will show up for some seconds and than disappear again.</li>
        <li>Note that the time-interval specified in the station info-window (on the map) is how long a station has been on that location <u>without any downtime longer than 24h</u>.</li>
    </ul>

    <h2>10. Can I link to this website?</h4>
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

    <h2>11. What browsers do this website support?</h2>
    <p>
        Our goal is that APRS Direct should work on all broswers that supports websockets (an HTML5 feature). The following browser version (and newer) supports the websocket-protocol.
    </p>
    <ul>
        <li>Internet Explorer 10 (released 4/9 2012)</li>
        <li>Edge 12 (released 30/3 2015)</li>
        <li>Firefox 11 (released 31/1 2012)</li>
        <li>Chrome 16 (released 25/10 2012)</li>
        <li>Safari 7 (released 22/10 2013)</li>
        <li>Opera 6.1 (released 5/11 2012)</li>
        <li>iOS Safari 6.1 (released 28/1 2013)</li>
        <li>Android Browser 4.4 (released 9/12 2013)</li>
        <li>Blackberry browser 7 (released 1/1 2012)</li>
        <li>Opera Mobile 12.1 (released 9/10 2012)</li>
        <li>Chrome 53 for Android (released 8/9 2016)</li>
        <li>Firefox 49 for Android (released 20/9 2016)</li>
        <li>IE Mobile 10 (released 20/6 2012)</li>
        <li>UC Browser 11 (released 17/8 2016)</li>
        <li>Samsung Internet 4 (released 19/4 2016)</li>
    </ul>
</div>
