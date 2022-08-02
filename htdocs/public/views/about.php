<?php require dirname(__DIR__) . "../../includes/bootstrap.php"; ?>

<title>About / FAQ</title>
<div class="modal-inner-content modal-inner-content-about" style="padding-bottom: 30px;">
    <div class="modal-inner-content-menu">
        <span>About</span>
        <a href="/views/faq.php" class="tdlink" title="Frequently asked questions">FAQ</a>
    </div>
    <div class="horizontal-line">&nbsp;</div>

    <p>
	Welcome to this APRS tracking website! Our goal is to bring you a fast and easy-to-use map with APRS data from <a href="http://www.aprs-is.net" target="_blank">APRS-IS</a>, <a href="http://www.wxqa.com" target="_blank">CWOP-IS</a>, <a href="https://www.glidernet.org" target="_blank">OGN</a> or some other APRS data sourcei (depending on how this specific website is configured). We give you fast map updates and nice looking APRS symbols!
    </p>

    <img src="/images/aprs-symbols.png" title="APRS symbols" style="width:100%"/>

    <p>
        This website is based on the APRS Track Direct tools. Read more about APRS Track Direct <a href="https://www.aprsdirect.com" target="_blank">here</a> or go directly to <a href="https://github.com/qvarforth/trackdirect" target="_blank">GitHub</a>. In addition to a map with fast APRS data updates, APRS Track direct also provides related functions such as <a href="/views/latest.php" class="tdlink" title="List latest heard stations">Latest heard</a> and <a href="/views/search.php" class="tdlink" title="Search for stations">Station search</a> etc. 
    </p>

    <h3>What is APRS?</h3>
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

</div>
