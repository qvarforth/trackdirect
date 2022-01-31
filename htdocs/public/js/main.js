// Init local time presentation
jQuery(document).ready(function ($) {
  var locale = window.navigator.userLanguage || window.navigator.language;
  moment.locale(locale);
});

// Switch between regular topnav and topnav adapted for mobile
function toggleTopNav() {
  var x = document.getElementById("tdTopnav");
  if (x.className === "topnav") {
    x.className += " responsive";
  } else {
    x.className = "topnav";
  }
}

// If an external website shows map in iframe, hide all menu's
if (!inIframe()) {
  $("#tdTopnav").hide();
}

// Set correct time length option to active
jQuery(document).ready(function ($) {
  $("#tdTopnavTimelengthDefault").addClass("dropdown-content-checkbox-active");
});

// Open station dialog if user clicked on station name
jQuery(document).ready(function ($) {
  trackdirect.addListener("station-name-clicked", function (data) {
    $("#modal-station-info").show();
    if (trackdirect.isImperialUnits()) {
      $("#modal-station-info-iframe").attr(
        "src",
        "/station/overview.php?id=" + data.station_id + "&imperialUnits=1"
      );
    } else {
      $("#modal-station-info-iframe").attr(
        "src",
        "/station/overview.php?id=" + data.station_id + "&imperialUnits=0"
      );
    }
  });
});

// Update url when user moves map
jQuery(document).ready(function ($) {
  var newUrlTimeoutId = null;
  trackdirect.addListener("position-request-sent", function (data) {
    if (newUrlTimeoutId !== null) {
      clearTimeout(newUrlTimeoutId);
    }

    newUrlTimeoutId = window.setTimeout(function () {
      var url = window.location.href.replace(/^(?:\/\/|[^/]+)*\//, "");
      var newLat = Math.round(data.center.lat * 10000) / 10000;
      var newLng = Math.round(data.center.lng * 10000) / 10000;
      var newZoom = data.zoom;

      if (!url.includes("center=")) {
        if (!url.includes("?")) {
          url += "?center=" + newLat + "," + newLng;
        } else {
          url += "&center=" + newLat + "," + newLng;
        }
      } else {
        url = url.replace(/center=[^&]*/i, "center=" + newLat + "," + newLng);
      }

      if (!url.includes("zoom=")) {
        if (!url.includes("?")) {
          url += "?zoom=" + newZoom;
        } else {
          url += "&zoom=" + newZoom;
        }
      } else {
        url = url.replace(/zoom=[^&]*/i, "zoom=" + newZoom);
      }

      history.replaceState(null, "", url);
    }, 1000);
  });
});

// Handle filter response
jQuery(document).ready(function ($) {
  trackdirect.addListener("filter-changed", function (packets) {
    if (packets.length == 0) {
      // We are not filtering any more.
      $("#right-container-filtered").hide();

      // Time travel is stopped when filtering is stopped
      $("#right-container-timetravel").hide();

      // Reset tail length to default when filtering is stopped
      $("#tdTopnavTimelength>a").removeClass("dropdown-content-checkbox-active");
      $("#tdTopnavTimelengthDefault").addClass("dropdown-content-checkbox-active");
      $(".dropdown-content-checkbox-only-filtering").addClass("dropdown-content-checkbox-hidden");
    } else {
      var counts = {};
      for (var i = 0; i < packets.length; i++) {
        // Note that if related is set to 1, it is included since it is related to the station we are filtering on
        if (packets[i].related == 0) {
          counts[packets[i]["station_name"]] =
            1 + (counts[packets[i]["station_name"]] || 0);
        }
      }
      $("#right-container-filtered-content").html(
        "Filtering on " + Object.keys(counts).length + " station(s)"
      );
      $("#right-container-filtered").show();
      $(".dropdown-content-checkbox-only-filtering").removeClass("dropdown-content-checkbox-hidden");
    }
  });
});
