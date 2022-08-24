/**
 * Class trackdirect.models.InfoWindow
 * @see https://developers.google.com/maps/documentation/javascript/reference#InfoWindow
 * @param {trackdirect.models.Marker} marker
 * @param {trackdirect.models.Map} map
 * @param {boolean} disableAutoPan
 */
trackdirect.models.InfoWindow = function (marker, map, disableAutoPan) {
  disableAutoPan =
    typeof disableAutoPan !== "undefined" ? disableAutoPan : true;
  this._marker = marker;
  this._defaultMap = map;
  this._polyline = null;
  this._tdEventListeners = {};

  // Call the parent constructor
  if (typeof google === "object" && typeof google.maps === "object") {
    google.maps.InfoWindow.call(this, {
      disableAutoPan: disableAutoPan,
    });
  } else if (typeof L === "object") {
    var yOffset = 2;
    if (!marker.isDotMarker()) {
      yOffset = -5;
    }
    L.Popup.call(this, {
      autoPan: !disableAutoPan,
      offset: [0, yOffset],
      maxWidth: 440,
      className: "leaflet-infowindow-content",
    });
  }

  // Handle close click
  var me = this;
  if (typeof google === "object" && typeof google.maps === "object") {
    google.maps.event.addListener(this, "closeclick", function () {
      me._hideRelatedMarkerTail();
    });
  } else if (typeof L === "object") {
    this.on("popupclose", function () {
      me._hideRelatedMarkerTail();
    });
  }
};
if (typeof google === "object" && typeof google.maps === "object") {
  trackdirect.models.InfoWindow.prototype = Object.create(
    google.maps.InfoWindow.prototype
  );
} else if (typeof L === "object") {
  trackdirect.models.InfoWindow.prototype = Object.create(L.Popup.prototype);
}
trackdirect.models.InfoWindow.prototype.constructor =
  trackdirect.models.InfoWindow;

/**
 * set new info window marker
 * @param {trackdirect.models.Marker} marker
 */
trackdirect.models.InfoWindow.prototype.setMarker = function (marker) {
  this._marker = marker;
};

/**
 * get info window marker
 * @return trackdirect.models.Marker
 */
trackdirect.models.InfoWindow.prototype.getMarker = function () {
  return this._marker;
};

/**
 * get info window marker polyline
 * @return trackdirect.models.Marker
 */
trackdirect.models.InfoWindow.prototype.getPolyline = function () {
  return this._polyline;
};

/**
 * Is info window open
 */
trackdirect.models.InfoWindow.prototype.isInfoWindowOpen = function () {
  if (typeof google === "object" && typeof google.maps === "object") {
    if (this.getMap() !== null) {
      return true;
    }
  } else if (typeof L === "object" && typeof windyInit === "function") {
    return this._defaultMap.hasLayer(this);
  } else if (typeof L === "object") {
    return this.isOpen();
  }

  return false;
};

/**
 * show info window
 * @param {boolean} compactVersion
 * @param {LatLngLiteral} position
 */
trackdirect.models.InfoWindow.prototype.show = function (
  compactVersion,
  position
) {
  compactVersion =
    typeof compactVersion !== "undefined" ? compactVersion : false;
  position = typeof position !== "undefined" ? position : null;
  this._create(compactVersion);

  if (typeof google === "object" && typeof google.maps === "object") {
    if (position !== null) {
      this.setPosition(position);
      this.open(this._defaultMap);
    } else {
      this.open(this._defaultMap, this._marker);
    }

    this.addListener("domready", function () {
      this._addPhgLinkListeners();
      this._addRngLinkListeners();
    });
  } else if (typeof L === "object") {
    if (this.isOpen()) {
      this._addPhgLinkListeners();
      this._addRngLinkListeners();
    } else {
      this.on("add", function () {
        this._addPhgLinkListeners();
        this._addRngLinkListeners();
      });
    }

    if (position !== null) {
      this.setLatLng(position);
      this.openOn(this._defaultMap);
    } else {
      this.setLatLng(this._marker.packet.getLatLngLiteral());
      this.openOn(this._defaultMap);
    }
  }

  // Show tail related to station related to this info-window
  if (this._defaultMap.getZoom() < trackdirect.settings.minZoomForMarkerTail) {
    if (this._marker.overwrite) {
      this._emitTdEventListeners(
        "station-tail-needed",
        this._marker.packet.station_id
      );
    }
    this._marker.showMarkerTail(true);
  }
};

/**
 * hide info window
 */
trackdirect.models.InfoWindow.prototype.hide = function () {
  if (typeof google === "object" && typeof google.maps === "object") {
    this.close();
    if (this.getMap() !== null) {
      this.setMap(null);
    }
  } else if (typeof L === "object") {
    this._defaultMap.removeLayer(this);
  }

  this._hideRelatedMarkerTail();

  if (
    this._defaultMap.state.openInfoWindow !== null &&
    this._defaultMap.state.openInfoWindow === this
  ) {
    this._defaultMap.state.openInfoWindow = null;
  }
};

/**
 * Add listener to events
 * @param {string} event
 * @param {string} handler
 */
(trackdirect.models.InfoWindow.prototype.addTdListener = function (
  event,
  handler
) {
  if (!(event in this._tdEventListeners)) {
    this._tdEventListeners[event] = [];
  }
  this._tdEventListeners[event].push(handler);
}),
  /**
   * Emit all event listeners for a specified event
   * @param {string} event
   * @param {object} arg
   */
  (trackdirect.models.InfoWindow.prototype._emitTdEventListeners = function (
    event,
    arg
  ) {
    if (event in this._tdEventListeners) {
      for (var i = 0; i < this._tdEventListeners[event].length; i++) {
        this._tdEventListeners[event][i](arg);
      }
    }
  });

/**
 * Create marker info window
 * @param {boolean} compactVersion
 */
trackdirect.models.InfoWindow.prototype._create = function (compactVersion) {
  if (compactVersion) {
    var mainDiv = this._getCompactMainDiv();
    var menuwrapper = this._getMenuDiv(false);

    this._polyline = this._defaultMap.markerCollection.getMarkerPolyline(
      this._marker.markerIdKey
    );
  } else {
    var mainDiv = this._getMainDiv();
    if (!trackdirect.isMobile) {
      mainDiv.append(this._getIconDiv());
    }

    mainDiv.append(this._getCompletePacketDiv());
    var menuwrapper = this._getMenuDiv(true);
  }

  mainDiv.append(menuwrapper);
  var wrapperDiv = $(document.createElement("div"));
  wrapperDiv.append(mainDiv);
  if (typeof google === "object" && typeof google.maps === "object") {
    this.setContent(wrapperDiv.html());
  } else if (typeof L === "object") {
    this.setContent(wrapperDiv.html());
  }
};

/**
 * Hide tail for marker related to the current open info-window
 */
trackdirect.models.InfoWindow.prototype._hideRelatedMarkerTail = function () {
  if (this._polyline !== null) {
    if (
      !this._defaultMap.state.isFilterMode &&
      this._defaultMap.getZoom() < trackdirect.settings.minZoomForMarkerTail
    ) {
      var markerIdKey = this._polyline.markerIdKey;
      if (this._defaultMap.markerCollection.isExistingMarker(markerIdKey)) {
        var stationId =
          this._defaultMap.markerCollection.getMarker(markerIdKey).packet
            .station_id;
        var stationLatestMarker =
          this._defaultMap.markerCollection.getStationLatestMarker(stationId);
        if (stationLatestMarker !== null) {
          stationLatestMarker.hideMarkerTail();
        }
      }
    }
  } else if (this._marker !== null) {
    if (
      !this._defaultMap.state.isFilterMode &&
      this._defaultMap.getZoom() < trackdirect.settings.minZoomForMarkerTail
    ) {
      this._marker.hideMarkerTail();
    }
  }
};

/**
 * Get info window main div
 * @return {object}
 */
trackdirect.models.InfoWindow.prototype._getMainDiv = function () {
  var mainDiv = $(document.createElement("div"));
  mainDiv.css("font-family", "Verdana,Arial,sans-serif");
  if (!trackdirect.isMobile) {
    mainDiv.css("font-size", "11px");
  } else {
    mainDiv.css("font-size", "10px");
  }
  mainDiv.css("line-height", "1.42857143");
  mainDiv.css("color", "#333");
  mainDiv.css("text-align", "left");
  return mainDiv;
};

/**
 * Get info window main div
 * @return {object}
 */
trackdirect.models.InfoWindow.prototype._getIconDiv = function () {
  var iconUrl64 = trackdirect.services.symbolPathFinder.getFilePath(
    this._marker.packet.symbol_table,
    this._marker.packet.symbol,
    null,
    null,
    null,
    64,
    64
  );
  var iconImg = $(document.createElement("img"));
  iconImg.css("width", "64px");
  iconImg.css("height", "64px");
  iconImg.attr("src", iconUrl64);
  iconImg.attr("alt", ""); // Set the icon description
  iconImg.attr("title", ""); // Set the icon description

  var leftIconDiv = $(document.createElement("div"));
  leftIconDiv.css("display", "inline-block");
  leftIconDiv.css("vertical-align", "top");
  leftIconDiv.css("padding-right", "15px");
  leftIconDiv.css("padding-bottom", "5px");
  leftIconDiv.append(iconImg);
  return leftIconDiv;
};

/**
 * Get info window packet div
 * @return {object}
 */
trackdirect.models.InfoWindow.prototype._getPacketDiv = function () {
  var packetDiv = $(document.createElement("div"));
  packetDiv.css("display", "inline-block");
  packetDiv.css("vertical-align", "top");
  packetDiv.css("max-width", "350px");
  return packetDiv;
};

/**
 * Get info window name div icon
 * @return {object}
 */
trackdirect.models.InfoWindow.prototype._getNameIconDiv = function () {
  var iconUrl24 = trackdirect.services.symbolPathFinder.getFilePath(
    this._marker.packet.symbol_table,
    this._marker.packet.symbol,
    null,
    null,
    null,
    24,
    24
  );
  var iconImg = $(document.createElement("img"));
  iconImg.css("width", "24px");
  iconImg.css("height", "24px");
  iconImg.css("vertical-align", "middle");
  iconImg.attr("src", iconUrl24);
  iconImg.attr("alt", "symbol");
  iconImg.attr("title", ""); // Set the icon description?
  return iconImg;
};

/**
 * Get info window name link element
 * @return {object}
 */
trackdirect.models.InfoWindow.prototype._getNameLink = function () {
  var nameLink = $(document.createElement("a"));
  nameLink.css("color", "#337ab7");
  if (trackdirect.isMobile) {
    nameLink.css("vertical-align", "-2px");
  }

  nameLink.attr("href", "");
  nameLink.attr(
    "onclick",
    "trackdirect.openStationInformationDialog(" +
      this._marker.packet.station_id +
      "); return false;"
  );

  nameLink.html(escapeHtml(this._marker.packet.station_name));
  return nameLink;
};

/**
 * Get info window sender name link element
 * @return {object}
 */
trackdirect.models.InfoWindow.prototype._getSenderNameLink = function () {
  var nameLink = $(document.createElement("span"));
  if (trackdirect.isMobile) {
    nameLink.css("vertical-align", "-2px");
  }

  nameLink.html(escapeHtml(this._marker.packet.sender_name));
  return nameLink;
};

/**
 * Get info window name div
 * @return {object}
 */
trackdirect.models.InfoWindow.prototype._getNameDiv = function () {
  var nameDiv = $(document.createElement("div"));
  nameDiv.css("clear", "both");
  nameDiv.css("font-size", "12px");
  nameDiv.css("font-weight", "bold");
  if (trackdirect.isMobile) {
    nameDiv.append(this._getNameIconDiv());
    nameDiv.append("&nbsp;");
    nameDiv.append("&nbsp;");
  }
  nameDiv.append(this._getNameLink());
  if (this._marker.packet.getOgnRegistration() != null) {
    var name = escapeHtml(this._marker.packet.getOgnRegistration());
    if (this._marker.packet.getOgnCN() !== null) {
      name += " [" + escapeHtml(this._marker.packet.getOgnCN()) + "]";
    }
    nameDiv.append(", ");
    nameDiv.append(name);
  }

  if (this._marker.packet.sender_name != this._marker.packet.station_name) {
    nameDiv.append("&nbsp;(");
    nameDiv.append(this._getSenderNameLink());
    nameDiv.append(")");
  }
  return nameDiv;
};

/**
 * Get info window packet div
 * @return {object}
 */
trackdirect.models.InfoWindow.prototype._getCompletePacketDiv = function () {
  var packetDiv = this._getPacketDiv();
  packetDiv.append(this._getNameDiv());
  packetDiv.append(this._getPacketTimeDiv());
  if (this._marker.packet.timestamp > 0) {
    if ($(window).height() >= 300) {
      packetDiv.append(this._getPacketPathDiv());
    }
    var phgRange = this._marker.packet.getPHGRange();
    var rngRange = this._marker.packet.getRNGRange();
    if (phgRange !== null || rngRange !== null) {
      packetDiv.append(this._getSpaceDiv());
      packetDiv.append(this._getPhgDiv(phgRange));
      packetDiv.append(this._getRngDiv(rngRange));
    }
    if ($(window).height() >= 300) {
      var transmitDistance = this._getTransmitDistance(this._marker.packet);
      var tailDistance = this._getTailDistance(
        this._defaultMap.markerCollection.getMarkerMasterMarkerKeyId(
          this._marker.markerIdKey
        )
      );
      if (
        (transmitDistance !== null &&
          Math.round(transmitDistance / 100) != 0) ||
        (tailDistance !== null && Math.round(tailDistance) > 0)
      ) {
        packetDiv.append(this._getSpaceDiv());
        packetDiv.append(this._getTransmitDistanceDiv(transmitDistance));
        packetDiv.append(this._getTailDistanceDiv(tailDistance));
      }
    }
    if (
      this._marker.packet.speed !== null ||
      this._marker.packet.course !== null ||
      this._marker.packet.altitude !== null
    ) {
      packetDiv.append(this._getSpaceDiv());
      packetDiv.append(this._getPacketSpeedAltitudeCourseDiv());
    }
    if (
      typeof this._marker.packet.weather !== "undefined" &&
      this._marker.packet.weather !== null
    ) {
      packetDiv.append(this._getSpaceDiv());
      packetDiv.append(this._getWeatherDiv());
    }
    if (
      typeof this._marker.packet.latest_telemetry_packet_timestamp !==
        "undefined" &&
      this._marker.packet.latest_telemetry_packet_timestamp !== null
    ) {
      packetDiv.append(this._getSpaceDiv());
      packetDiv.append(this._getTelemetryDiv());
    }

    var commentDiv = this._getPacketCommentDiv();
    if (commentDiv != null) {
      packetDiv.append(this._getSpaceDiv());
      packetDiv.append(commentDiv);
    }
  }
  return packetDiv;
};

/**
 * Get info window packet time div
 * @return {object}
 */
trackdirect.models.InfoWindow.prototype._getPacketTimeDiv = function () {
  if (this._marker.packet.timestamp == 0) {
    dateString =
      '<span style="color: grey;">No known packet for specified limits.</span>';
  } else {
    var date = new Date(this._marker.packet.timestamp * 1000);
    var dateString = moment(date).format(
      trackdirect.settings.dateFormatNoTimeZone
    );
    if (
      this._marker.packet.timestamp > this._marker.packet.position_timestamp &&
      !trackdirect.isMobile
    ) {
      var positionDate = new Date(
        this._marker.packet.position_timestamp * 1000
      );
      dateString =
        moment(positionDate).format(trackdirect.settings.dateFormatNoTimeZone) +
        " - " +
        moment(date).format(trackdirect.settings.dateFormatNoTimeZone);
    }
    if (
      this._defaultMap.state.endTimeTravelTimestamp !== null &&
      this._marker.packet.map_id == 12
    ) {
      dateString +=
        '<br/><span style="color: grey;">(exact time for this is not known)</span>';
    }
  }
  var timeDiv = $(document.createElement("div"));
  timeDiv.css("clear", "both");
  timeDiv.html(dateString);
  return timeDiv;
};

/**
 * Get info window packet path div
 * @return {object}
 */
trackdirect.models.InfoWindow.prototype._getPacketPathDiv = function () {
  var rawPath = this._marker.packet.getLinkifiedRawPath(); // Html allready escaped
  if (rawPath !== null) {
    var rawPathDiv = $(document.createElement("div"));
    rawPathDiv.css("clear", "both");
    rawPathDiv.html("[" + rawPath + "]");
    return rawPathDiv;
  }
  return null;
};

/**
 * Get info window space div
 * @return {object}
 */
trackdirect.models.InfoWindow.prototype._getSpaceDiv = function () {
  var spaceDiv = $(document.createElement("div"));
  spaceDiv.css("clear", "both");
  spaceDiv.css("line-height", "4px");
  spaceDiv.html("&nbsp;");
  return spaceDiv;
};

/**
 * Get info window phg div
 * @param {float} phgRange
 * @return {object}
 */
trackdirect.models.InfoWindow.prototype._getPhgDiv = function (phgRange) {
  if (phgRange !== null) {
    if (this._defaultMap.state.useImperialUnit) {
      var phgRange =
        Math.round(
          trackdirect.services.imperialConverter.convertKilometerToMile(
            phgRange / 1000
          ) * 10
        ) / 10; // converted to miles
      var phgRangeUnit = "miles";
    } else {
      var phgRange = Math.round(phgRange / 10) / 100; // converted to km
      var phgRangeUnit = "km";
    }
    var phgDiv = $(document.createElement("div"));
    phgDiv.attr(
      "id",
      "phglinks-" +
        this._marker.packet.station_id +
        "-" +
        this._marker.packet.id
    );
    var halfPhgLink = $(
      "<a style='color: #337ab7;' id='half-phg-" +
        this._marker.packet.station_id +
        "-" +
        this._marker.packet.id +
        "' href='#'>Half</a>"
    );
    var fullPhgLink = $(
      "<a style='color: #337ab7;' id='full-phg-" +
        this._marker.packet.station_id +
        "-" +
        this._marker.packet.id +
        "' href='#'>Full</a>"
    );
    var nonePhgLink = $(
      "<a style='color: #337ab7;' id='none-phg-" +
        this._marker.packet.station_id +
        "-" +
        this._marker.packet.id +
        "' href='#'>None</a>"
    );
    phgDiv.css("clear", "both");
    phgDiv.css("display", "none");
    phgDiv.css("color", "#440B2A");
    phgDiv.append("PHG calculated range: " + phgRange + " " + phgRangeUnit);

    if (typeof L === "object" && L.version <= "0.7.7") {
      // Skip PHG links for older Leaflet version
      return phgDiv;
    }

    if (phgRange > 0) {
      phgDiv.append("<br/>");
      phgDiv.append("PHG circle: ");
      phgDiv.append(fullPhgLink);
      phgDiv.append('<span style="color:#000"> - </span>');
      phgDiv.append(halfPhgLink);
      phgDiv.append('<span style="color:#000"> - </span>');
      phgDiv.append(nonePhgLink);
    }
    return phgDiv;
  }
  return null;
};

/**
 * Get info window rng div
 * @param {float} rngRange
 * @return {object}
 */
trackdirect.models.InfoWindow.prototype._getRngDiv = function (rngRange) {
  if (rngRange !== null) {
    if (this._defaultMap.state.useImperialUnit) {
      var rngRange =
        Math.round(
          trackdirect.services.imperialConverter.convertKilometerToMile(
            rngRange / 1000
          ) * 10
        ) / 10; // converted to miles
      var rngRangeUnit = "miles";
    } else {
      var rngRange = Math.round(rngRange * 100) / 100; // converted to km
      var rngRangeUnit = "km";
    }
    var rngDiv = $(document.createElement("div"));
    rngDiv.attr(
      "id",
      "rnglinks-" +
        this._marker.packet.station_id +
        "-" +
        this._marker.packet.id
    );
    var halfRngLink = $(
      "<a style='color: #337ab7;' id='half-rng-" +
        this._marker.packet.station_id +
        "-" +
        this._marker.packet.id +
        "' href='#'>Half</a>"
    );
    var fullRngLink = $(
      "<a style='color: #337ab7;' id='full-rng-" +
        this._marker.packet.station_id +
        "-" +
        this._marker.packet.id +
        "' href='#'>Full</a>"
    );
    var noneRngLink = $(
      "<a style='color: #337ab7;' id='none-rng-" +
        this._marker.packet.station_id +
        "-" +
        this._marker.packet.id +
        "' href='#'>None</a>"
    );
    rngDiv.css("clear", "both");
    rngDiv.css("display", "none");
    rngDiv.css("color", "#440B2A");
    rngDiv.append("RNG precalculated range: " + rngRange + " " + rngRangeUnit);

    if (typeof L === "object" && L.version <= "0.7.7") {
      // Skip RNG links for older Leaflet version
      return rngDiv;
    }

    if (rngRange > 0) {
      rngDiv.append("<br/>");
      rngDiv.append("RNG circle: ");
      rngDiv.append(fullRngLink);
      rngDiv.append('<span style="color:#000"> - </span>');
      rngDiv.append(halfRngLink);
      rngDiv.append('<span style="color:#000"> - </span>');
      rngDiv.append(noneRngLink);
    }
    return rngDiv;
  }
  return null;
};

/**
 * Get info window transmit distance div
 * @param {float} transmitDistance
 * @return {object}
 */
trackdirect.models.InfoWindow.prototype._getTransmitDistanceDiv = function (
  transmitDistance
) {
  if (transmitDistance !== null && Math.round(transmitDistance / 100) != 0) {
    var transmitDistanceDiv = $(document.createElement("div"));
    transmitDistanceDiv.css("clear", "both");
    transmitDistanceDiv.css("color", "#273c20");
    if (this._defaultMap.state.useImperialUnit) {
      transmitDistance =
        Math.round(
          trackdirect.services.imperialConverter.convertKilometerToMile(
            transmitDistance / 1000
          ) * 10
        ) / 10;
      transmitDistanceUnit = "miles";
    } else {
      transmitDistance = Math.round(transmitDistance / 100) / 10;
      transmitDistanceUnit = "km";
    }
    transmitDistanceDiv.append(
      '<span title="Transmit distance to receiving digipeater/igate">Transmit distance: ' +
        transmitDistance +
        " " +
        transmitDistanceUnit +
        "</span>"
    );
    return transmitDistanceDiv;
  }
  return null;
};

/**
 * Get info window tail distance div
 * @param {float} tailDistance
 * @return {object}
 */
trackdirect.models.InfoWindow.prototype._getTailDistanceDiv = function (
  tailDistance
) {
  if (tailDistance !== null && Math.round(tailDistance) > 0) {
    var distanceDiv = $(document.createElement("div"));
    distanceDiv.css("clear", "both");
    distanceDiv.css("color", "#273c20");
    if (tailDistance < 1000) {
      if (this._defaultMap.state.useImperialUnit) {
        tailDistance = Math.round(
          trackdirect.services.imperialConverter.convertMeterToYard(
            tailDistance
          )
        );
        tailDistanceUnit = "yd";
      } else {
        tailDistance = Math.round(tailDistance);
        tailDistanceUnit = "m";
      }
    } else {
      if (this._defaultMap.state.useImperialUnit) {
        tailDistance =
          Math.round(
            trackdirect.services.imperialConverter.convertKilometerToMile(
              tailDistance / 1000
            ) * 10
          ) / 10;
        tailDistanceUnit = "miles";
      } else {
        tailDistance = Math.round(tailDistance / 100) / 10;
        tailDistanceUnit = "km";
      }
    }
    distanceDiv.append(
      '<span title="Current shown tail distance (depends on the time settings)">Current tail distance: ' +
        tailDistance +
        " " +
        tailDistanceUnit +
        "</span>"
    );
    return distanceDiv;
  }
  return null;
};

/**
 * Get info window packet speed altitude and course div
 * @return {object}
 */
trackdirect.models.InfoWindow.prototype._getPacketSpeedAltitudeCourseDiv =
  function () {
    if (
      Math.round(this._marker.packet.speed) != 0 ||
      Math.round(this._marker.packet.course) != 0 ||
      Math.round(this._marker.packet.altitude) != 0
    ) {
      var speedDiv = $(document.createElement("div"));
      speedDiv.css("clear", "both");
      speedDiv.css("font-weight", "bold");

      if (this._marker.packet.speed !== null) {
        if (this._defaultMap.state.useImperialUnit) {
          speedDiv.append(
            Math.round(
              trackdirect.services.imperialConverter.convertKilometerToMile(
                this._marker.packet.speed
              )
            ) + " mph "
          );
        } else {
          speedDiv.append(Math.round(this._marker.packet.speed) + " km/h ");
        }
      }

      if (this._marker.packet.course !== null) {
        speedDiv.append(Math.round(this._marker.packet.course) + "&deg; ");
      }

      if (this._marker.packet.altitude !== null) {
        if (this._defaultMap.state.useImperialUnit) {
          speedDiv.append(
            " alt " +
              Math.round(
                trackdirect.services.imperialConverter.convertMeterToFeet(
                  this._marker.packet.altitude
                )
              ) +
              " ft "
          );
        } else {
          speedDiv.append(
            " alt " + Math.round(this._marker.packet.altitude) + " m "
          );
        }
      }

      return speedDiv;
    }
    return null;
  };

/**
 * Get info window weather div rain string
 * @return {string}
 */
trackdirect.models.InfoWindow.prototype._getWeatherDivRainString = function () {
  if (isNumeric(this._marker.packet.weather.rain_1h)) {
    if (this._defaultMap.state.useImperialUnit) {
      var rain1h = "-";
      if (isNumeric(this._marker.packet.weather.rain_1h)) {
        rain1h =
          Math.round(
            trackdirect.services.imperialConverter.convertMmToInch(
              this._marker.packet.weather.rain_1h
            )
          ) + "in";
      }
      var rain24h = "-";
      if (isNumeric(this._marker.packet.weather.rain_24h)) {
        rain24h =
          Math.round(
            trackdirect.services.imperialConverter.convertMmToInch(
              this._marker.packet.weather.rain_24h
            )
          ) + "in";
      }
      var rainSinceMidnight = "-";
      if (isNumeric(this._marker.packet.weather.rain_since_midnight)) {
        rainSinceMidnight =
          Math.round(
            trackdirect.services.imperialConverter.convertMmToInch(
              this._marker.packet.weather.rain_since_midnight
            )
          ) + "in";
      }
    } else {
      var rain1h = "-";
      if (isNumeric(this._marker.packet.weather.rain_1h)) {
        rain1h = Math.round(this._marker.packet.weather.rain_1h) + "mm";
      }
      var rain24h = "-";
      if (isNumeric(this._marker.packet.weather.rain_24h)) {
        rain24h = Math.round(this._marker.packet.weather.rain_24h) + "mm";
      }
      var rainSinceMidnight = "-";
      if (isNumeric(this._marker.packet.weather.rain_since_midnight)) {
        rainSinceMidnight =
          Math.round(this._marker.packet.weather.rain_since_midnight) + "mm";
      }
    }
    return (
      "<b>Rain</b> " +
      rain1h +
      "/" +
      rain24h +
      "/" +
      rainSinceMidnight +
      " (1h/24h/midnight)<br/>"
    );
  }
  return null;
};

/**
 * Get info window weather div temperature string
 * @return {string}
 */
trackdirect.models.InfoWindow.prototype._getWeatherDivTemperatureString =
  function () {
    if (isNumeric(this._marker.packet.weather.temperature)) {
      if (this._defaultMap.state.useImperialUnit) {
        return (
          "<b>Temperature</b> " +
          Math.round(
            trackdirect.services.imperialConverter.convertCelciusToFahrenheit(
              this._marker.packet.weather.temperature
            )
          ) +
          "&deg;F" +
          "<br/>"
        );
      } else {
        return (
          "<b>Temperature</b> " +
          Math.round(this._marker.packet.weather.temperature) +
          "&deg;C" +
          "<br/>"
        );
      }
    }
    return null;
  };

/**
 * Get info window weather div humidity string
 * @return {string}
 */
trackdirect.models.InfoWindow.prototype._getWeatherDivHumidityString =
  function () {
    if (isNumeric(this._marker.packet.weather.humidity)) {
      return (
        "<b>Humidity</b> " +
        Math.round(this._marker.packet.weather.humidity) +
        "%<br/>"
      );
    }
    return null;
  };

/**
 * Get info window weather div pressure string
 * @return {string}
 */
trackdirect.models.InfoWindow.prototype._getWeatherDivPressureString =
  function () {
    if (isNumeric(this._marker.packet.weather.pressure)) {
      if (this._defaultMap.state.useImperialUnit) {
        return (
          "<b>Pressure</b> " +
          Math.round(
            trackdirect.services.imperialConverter.convertMbarToMmhg(
              this._marker.packet.weather.pressure
            )
          ) +
          " mmHg<br/>"
        );
      } else {
        return (
          "<b>Pressure</b> " +
          Math.round(this._marker.packet.weather.pressure) +
          " hPa<br/>"
        );
      }
    }
    return null;
  };

/**
 * Get info window weather div wind string
 * @return {string}
 */
trackdirect.models.InfoWindow.prototype._getWeatherDivWindString = function () {
  if (isNumeric(this._marker.packet.weather.wind_speed)) {
    var windDir = "";
    if (
      typeof this._marker.packet.weather.wind_direction !== "undefined" &&
      isNumeric(this._marker.packet.weather.wind_direction)
    ) {
      windDir =
        this._marker.packet.weather.wind_direction.toString() + "&deg; ";
    }

    if (this._defaultMap.state.useImperialUnit) {
      if (isNumeric(this._marker.packet.weather.wind_gust)) {
        return (
          "<b>Wind</b> " +
          windDir +
          Math.round(
            trackdirect.services.imperialConverter.convertMpsToMph(
              this._marker.packet.weather.wind_speed
            ) * 10
          ) /
            10 +
          " mph" +
          " (" +
          Math.round(
            trackdirect.services.imperialConverter.convertMpsToMph(
              this._marker.packet.weather.wind_gust
            ) * 10
          ) /
            10 +
          " mph)<br/>"
        );
      } else {
        return (
          "<b>Wind</b> " +
          windDir +
          Math.round(
            trackdirect.services.imperialConverter.convertMpsToMph(
              this._marker.packet.weather.wind_speed
            ) * 10
          ) /
            10 +
          " mph<br/>"
        );
      }
    } else {
      if (isNumeric(this._marker.packet.weather.wind_gust)) {
        return (
          "<b>Wind</b> " +
          windDir +
          Math.round(this._marker.packet.weather.wind_speed * 10) / 10 +
          " m/s" +
          " (" +
          Math.round(this._marker.packet.weather.wind_gust * 10) / 10 +
          " m/s)<br/>"
        );
      } else {
        return (
          "<b>Wind</b> " +
          windDir +
          Math.round(this._marker.packet.weather.wind_speed * 10) / 10 +
          " m/s <br/>"
        );
      }
    }
  }
  return null;
};

/**
 * Get info window weather div
 * @return {object}
 */
trackdirect.models.InfoWindow.prototype._getWeatherDiv = function () {
  var weatherDiv = $(document.createElement("div"));
  weatherDiv.css("clear", "both");
  weatherDiv.css("color", "#227152");

  var weatherDate = new Date(this._marker.packet.timestamp * 1000);
  if (
    typeof this._marker.packet.weather.timestamp !== "undefined" &&
    this._marker.packet.weather.timestamp !== null
  ) {
    weatherDate = new Date(this._marker.packet.weather.timestamp * 1000);
  }
  weatherDateString = moment(weatherDate).format(
    trackdirect.settings.dateFormatNoTimeZone
  );
  weatherDiv.append("<b>Latest Weather</b>  " + weatherDateString + "<br/>");

  if (!trackdirect.isMobile && $(window).height() >= 300) {
    weatherDiv.append(this._getWeatherDivTemperatureString());
    weatherDiv.append(this._getWeatherDivHumidityString());
    weatherDiv.append(this._getWeatherDivPressureString());
    weatherDiv.append(this._getWeatherDivRainString());
    weatherDiv.append(this._getWeatherDivWindString());
  }
  return weatherDiv;
};

/**
 * Get info window telemetry div
 * @return {object}
 */
trackdirect.models.InfoWindow.prototype._getTelemetryDiv = function () {
  var telemetryDiv = $(document.createElement("div"));
  telemetryDiv.css("clear", "both");
  telemetryDiv.css("color", "#823030");

  var telemetryDate = new Date(
    this._marker.packet.latest_telemetry_packet_timestamp * 1000
  );
  telemetryDateString = moment(telemetryDate).format(
    trackdirect.settings.dateFormatNoTimeZone
  );
  telemetryDiv.append("Latest Telemetry  " + telemetryDateString + "<br/>");

  return telemetryDiv;
};

/**
 * Get info window comment div
 * @return {object}
 */
trackdirect.models.InfoWindow.prototype._getPacketCommentDiv = function () {
  var comment = "";
  var ognSummary = escapeHtml(this._marker.packet.getOgnSummary());
  if (ognSummary != "") {
    comment = ognSummary;
  } else if (
    typeof this._marker.packet.comment !== "undefined" &&
    this._marker.packet.comment !== null
  ) {
    comment = Autolinker.link(escapeHtml(this._marker.packet.comment), {
      newWindow: true,
    });
  }
  if (comment == "") {
    return null;
  }
  var commentDiv = $(document.createElement("div"));
  commentDiv.css("clear", "both");
  commentDiv.css("font-weight", "bold");
  if (!trackdirect.isMobile) {
    commentDiv.css("font-size", "11px");
  } else {
    commentDiv.css("font-size", "10px");
  }
  commentDiv.html(comment);
  return commentDiv;
};

/**
 * Add info window PHG link listeners
 * @return none
 */
trackdirect.models.InfoWindow.prototype._addPhgLinkListeners = function () {
  var marker = this._marker;
  $("#half-phg-" + marker.packet.station_id + "-" + marker.packet.id).click(
    function (e) {
      marker.showPHGCircle(true);
      return false;
    }
  );

  $("#full-phg-" + marker.packet.station_id + "-" + marker.packet.id).click(
    function (e) {
      marker.showPHGCircle(false);
      return false;
    }
  );

  $(
    "#none-phg-" + this._marker.packet.station_id + "-" + marker.packet.id
  ).click(function (e) {
    marker.hidePHGCircle();
    return false;
  });

  if (
    $("#phglinks-" + marker.packet.station_id + "-" + marker.packet.id).length
  ) {
    $("#phglinks-" + marker.packet.station_id + "-" + marker.packet.id).show();
  }
};

/**
 * Add info window RNG link listeners
 * @return none
 */
trackdirect.models.InfoWindow.prototype._addRngLinkListeners = function () {
  var marker = this._marker;
  $("#half-rng-" + marker.packet.station_id + "-" + marker.packet.id).click(
    function (e) {
      marker.showRNGCircle(true);
      return false;
    }
  );

  $("#full-rng-" + marker.packet.station_id + "-" + marker.packet.id).click(
    function (e) {
      marker.showRNGCircle(false);
      return false;
    }
  );

  $("#none-rng-" + marker.packet.station_id + "-" + marker.packet.id).click(
    function (e) {
      marker.hideRNGCircle();
      return false;
    }
  );

  if (
    $("#rnglinks-" + marker.packet.station_id + "-" + marker.packet.id).length
  ) {
    $("#rnglinks-" + marker.packet.station_id + "-" + marker.packet.id).show();
  }
};

/**
 * Returns html element that contains the info window menu
 * @param {boolean} isInfoWindowOpen
 * @return {object}
 */
trackdirect.models.InfoWindow.prototype._getMenuDiv = function (
  isInfoWindowOpen
) {
  var menuWrapperDiv = this._getMenuDivWrapperDiv();

  var menuDiv = this._getMenuDivMainDiv();
  menuWrapperDiv.append(menuDiv);

  var menuUl = this._getMenuDivUlDiv();
  menuDiv.append(menuUl);

  menuUl.append(this._getMenuDivTrackLink());
  menuUl.append(this._getMenuDivFilterLink());
  if (!trackdirect.isMobile) {
    menuUl.append(this._getMenuDivCenterLink(isInfoWindowOpen));
  }
  menuUl.append(this._getMenuDivZoomLink(isInfoWindowOpen));
  if (
    !trackdirect.isEmbedded &&
    !inIframe() &&
    !this._marker.isMovingStation() &&
    this._marker.packet.source_id != 2
  ) {
    menuUl.append(this._getMenuDivCoverageLink());
  }
  return menuWrapperDiv;
};

/**
 * Get the info window menu wrapper div
 * @return {object}
 */
trackdirect.models.InfoWindow.prototype._getMenuDivWrapperDiv = function () {
  var menuWrapperDiv = $(document.createElement("div"));
  menuWrapperDiv.addClass("infowindow-menu-wrapper");
  menuWrapperDiv.css("clear", "both");
  menuWrapperDiv.css("width", "100%");
  menuWrapperDiv.css("padding-top", "8px");
  return menuWrapperDiv;
};

/**
 * Get the info window menu main div
 * @return {object}
 */
trackdirect.models.InfoWindow.prototype._getMenuDivMainDiv = function () {
  var menuDiv = $(document.createElement("div"));
  menuDiv.addClass("infowindow-menu");
  menuDiv.css("width", "100%");
  menuDiv.css("border-top", "1px solid #cecece");
  return menuDiv;
};

/**
 * Get the info window menu ul div
 * @return {object}
 */
trackdirect.models.InfoWindow.prototype._getMenuDivUlDiv = function () {
  var menuUl = $(document.createElement("ul"));
  menuUl.css("list-style-type", "none");
  menuUl.css("list-style", "none");
  menuUl.css("text-align", "center");
  menuUl.css("margin", "0");
  menuUl.css("padding", "0");
  menuUl.css("display", "table");
  return menuUl;
};

/**
 * Get the info window menu link CSS
 * @return {object}
 */
trackdirect.models.InfoWindow.prototype._getMenuDivLinkCss = function () {
  var liLinkCss = {
    "list-style": "none",
    display: "table-cell",
    "text-align": "center",
    "padding-right": "10px",
    width: "auto",
  };
  return liLinkCss;
};

/**
 * Get the info window menu track link
 * @return {object}
 */
trackdirect.models.InfoWindow.prototype._getMenuDivTrackLink = function () {
  var trackLinkElementClass =
    "trackStationLink" + this._marker.packet.station_id;
  var menuLi = $(document.createElement("li"));
  menuLi.css(this._getMenuDivLinkCss());
  var menuLink = $(document.createElement("a"));
  menuLink.css("color", "#337ab7");
  menuLink.attr("href", "#");
  menuLink.addClass(trackLinkElementClass);
  menuLink.attr(
    "onclick",
    "trackdirect.handleTrackStationRequest(" +
      this._marker.packet.station_id +
      ', "' +
      trackLinkElementClass +
      '"); return false;'
  );
  if (
    this._defaultMap.state.getTrackStationId() !== null &&
    this._defaultMap.state.getTrackStationId() == this._marker.packet.station_id
  ) {
    menuLink.html("Untrack");
  } else {
    menuLink.html("Track");
  }
  menuLi.append(menuLink);
  return menuLi;
};

/**
 * Get the info window menu filter link
 * @return {object}
 */
trackdirect.models.InfoWindow.prototype._getMenuDivFilterLink = function () {
  var filterLinkElementClass =
    "filterStationLink" + this._marker.packet.station_id;
  var menuLi = $(document.createElement("li"));
  menuLi.css(this._getMenuDivLinkCss());
  var menuLink = $(document.createElement("a"));
  menuLink.css("color", "#337ab7");
  menuLink.addClass(filterLinkElementClass);
  menuLink.attr(
    "onclick",
    "trackdirect.handleFilterStationRequest(" +
      this._marker.packet.station_id +
      ', "' +
      filterLinkElementClass +
      '"); return false;'
  );
  if (
    this._defaultMap.state.filterStationIds.length > 0 &&
    this._defaultMap.state.filterStationIds.indexOf(
      this._marker.packet.station_id
    ) > -1
  ) {
    menuLink.html("Unfilter");
    var center = this._defaultMap.getCenterLiteral();
    menuLink.attr(
      "href",
      "/center/" +
        Number.parseFloat(center.lat).toFixed(5) +
        "," +
        Number.parseFloat(center.lng).toFixed(5) +
        "/zoom/" +
        this._defaultMap.getZoom()
    );
  } else {
    menuLink.html("Filter");
    menuLink.attr("href", "/sid/" + this._marker.packet.station_id);
  }
  menuLi.append(menuLink);
  return menuLi;
};

/**
 * Get the info window menu coverage link
 * @return {object}
 */
trackdirect.models.InfoWindow.prototype._getMenuDivCoverageLink = function () {
  var coverageLinkElementClass =
    "stationCoverageLink" + this._marker.packet.station_id;
  var menuLi = $(document.createElement("li"));
  menuLi.css(this._getMenuDivLinkCss());
  var menuLink = $(document.createElement("a"));
  menuLink.css("color", "#337ab7");
  menuLink.css("white-space", "nowrap");
  menuLink.attr("href", "#");
  menuLink.addClass(coverageLinkElementClass);
  menuLink.attr(
    "onclick",
    "trackdirect.toggleStationCoverage(" +
      this._marker.packet.station_id +
      ', "' +
      coverageLinkElementClass +
      '"); return false;'
  );

  var coveragePolygon = this._defaultMap.markerCollection.getStationCoverage(
    this._marker.packet.station_id
  );
  if (coveragePolygon !== null && coveragePolygon.isRequestedToBeVisible()) {
    menuLink.html("Hide Coverage");
  } else {
    menuLink.html("Coverage");
  }
  menuLi.append(menuLink);
  return menuLi;
};

/**
 * Get the info window menu center link
 * @param {boolean} isInfoWindowOpen
 * @return {object}
 */
trackdirect.models.InfoWindow.prototype._getMenuDivCenterLink = function (
  isInfoWindowOpen
) {
  var menuLi = $(document.createElement("li"));
  menuLi.css(this._getMenuDivLinkCss());
  var menuLink = $(document.createElement("a"));
  menuLink.css("color", "#337ab7");
  if (isInfoWindowOpen) {
    menuLink.attr(
      "href",
      "/center/" +
        this._marker.packet.latitude.toFixed(5) +
        "," +
        this._marker.packet.longitude.toFixed(5) +
        "/zoom/" +
        this._defaultMap.getZoom()
    );
    menuLink.attr(
      "onclick",
      "trackdirect.setCenter(" +
        this._marker.packet.latitude +
        "," +
        this._marker.packet.longitude +
        "); return false;"
    );
    menuLink.html("Center");
  } else {
    menuLink.attr(
      "href",
      "/center/" +
        this._marker.packet.latitude.toFixed(5) +
        "," +
        this._marker.packet.longitude.toFixed(5) +
        "/zoom/" +
        this._defaultMap.getZoom()
    );
    menuLink.attr(
      "onclick",
      "trackdirect.focusOnMarkerId(" +
        this._marker.packet.marker_id +
        "); return false;"
    );
    menuLink.html("Focus");
  }
  menuLi.append(menuLink);
  return menuLi;
};

/**
 * Get the info window menu zoom link
 * @param {boolean} isInfoWindowOpen
 * @return {object}
 */
trackdirect.models.InfoWindow.prototype._getMenuDivZoomLink = function (
  isInfoWindowOpen
) {
  var menuLi = $(document.createElement("li"));
  menuLi.css(this._getMenuDivLinkCss());
  var menuLink = $(document.createElement("a"));
  menuLink.css("color", "#337ab7");
  if (isInfoWindowOpen) {
    menuLink.attr(
      "href",
      "/center/" +
        this._marker.packet.latitude.toFixed(5) +
        "," +
        this._marker.packet.longitude.toFixed(5) +
        "/zoom/14"
    );
    menuLink.attr(
      "onclick",
      "trackdirect.setCenter(" +
        this._marker.packet.latitude +
        "," +
        this._marker.packet.longitude +
        ", 14); return false;"
    );
    menuLink.html("Zoom");
  } else {
    menuLink.attr(
      "href",
      "/center/" +
        this._marker.packet.latitude.toFixed(5) +
        "," +
        this._marker.packet.longitude.toFixed(5) +
        "/zoom/14"
    );
    menuLink.attr(
      "onclick",
      "trackdirect.focusOnMarkerId(" +
        this._marker.packet.marker_id +
        ", 14); return false;"
    );
    menuLink.html("Zoom");
  }
  menuLi.append(menuLink);
  return menuLi;
};

/**
 * Create infowindow content (compact version))
 * @return string
 */
trackdirect.models.InfoWindow.prototype._getCompactMainDiv = function () {
  var packet = this._marker.packet;

  // Init main div
  var mainDiv = $(document.createElement("div"));
  mainDiv.css("font-family", "Verdana,Arial,sans-serif");
  if (!trackdirect.isMobile) {
    mainDiv.css("font-size", "11px");
  } else {
    mainDiv.css("font-size", "10px");
  }
  mainDiv.css("line-height", "1.42857143");
  mainDiv.css("color", "#333");
  mainDiv.css("text-align", "left");

  // Init polyline div
  var polylineDiv = $(document.createElement("div"));
  polylineDiv.css("float", "left");

  // Name
  var nameDiv = $(document.createElement("div"));
  nameDiv.css("clear", "both");
  nameDiv.css("font-size", "12px");
  nameDiv.css("font-weight", "bold");

  // Init img
  var iconUrl24 = trackdirect.services.symbolPathFinder.getFilePath(
    packet.symbol_table,
    packet.symbol,
    null,
    null,
    null,
    24,
    24
  );
  var iconImg = $(document.createElement("img"));
  iconImg.css("vertical-align", "middle");
  iconImg.css("width", "24px");
  iconImg.css("height", "24px");
  iconImg.attr("src", iconUrl24);
  iconImg.attr("alt", ""); // Set the icon description
  iconImg.attr("title", ""); // Set the icon description
  nameDiv.append(iconImg);
  nameDiv.append("&nbsp;");
  nameDiv.append("&nbsp;");

  var nameLink = $(document.createElement("a"));
  nameLink.css("color", "#337ab7");
  if (trackdirect.isMobile) {
    nameLink.css("vertical-align", "-2px");
  }

  nameLink.attr("href", "");
  nameLink.attr(
    "onclick",
    "trackdirect.openStationInformationDialog(" +
      packet.station_id +
      "); return false;"
  );

  nameLink.html(escapeHtml(packet.station_name));
  nameDiv.append(nameLink);

  if (packet.sender_name != packet.station_name) {
    nameDiv.append("&nbsp;(");
    var nameLink2 = $(document.createElement("span"));
    if (trackdirect.isMobile) {
      nameLink2.css("vertical-align", "-2px");
    }

    nameLink2.html(escapeHtml(packet.sender_name));
    nameDiv.append(nameLink2);
    nameDiv.append(")");
  }
  polylineDiv.append(nameDiv);

  var tailDistance = this._getTailDistance(
    this._defaultMap.markerCollection.getMarkerMasterMarkerKeyId(
      this._marker.markerIdKey
    )
  );
  if (tailDistance !== null && Math.round(tailDistance) > 0) {
    var distanceDiv = $(document.createElement("div"));
    distanceDiv.css("clear", "both");
    distanceDiv.css("padding-top", "4px");
    distanceDiv.append("Tail distance: ");
    if (tailDistance < 1000) {
      if (this._defaultMap.state.useImperialUnit) {
        distanceDiv.append(
          Math.round(
            trackdirect.services.imperialConverter.convertMeterToYard(
              tailDistance
            )
          ) + " yd "
        );
      } else {
        distanceDiv.append(Math.round(tailDistance) + " m ");
      }
    } else {
      if (this._defaultMap.state.useImperialUnit) {
        distanceDiv.append(
          Math.round(
            trackdirect.services.imperialConverter.convertKilometerToMile(
              tailDistance / 1000
            ) * 10
          ) /
            10 +
            " miles "
        );
      } else {
        distanceDiv.append(Math.round(tailDistance / 100) / 10 + " km ");
      }
    }

    polylineDiv.append(distanceDiv);
  }

  mainDiv.append(polylineDiv);
  return mainDiv;
};

/**
 * Returns the tail distance in meters for specified marker
 * @param {int} markerIdKey
 * @return int
 */
trackdirect.models.InfoWindow.prototype._getTailDistance = function (
  markerIdKey
) {
  if (this._defaultMap.markerCollection.isExistingMarker(markerIdKey)) {
    var marker = this._defaultMap.markerCollection.getMarker(markerIdKey);
    if (
      marker.packet.hasConfirmedMapId() &&
      marker.packet.is_moving == 1 &&
      marker.overwrite !== true
    ) {
      var distance = 0;
      if (this._defaultMap.markerCollection.hasDotMarkers(markerIdKey)) {
        var prevLatLng = null;
        var dotMarkers =
          this._defaultMap.markerCollection.getDotMarkers(markerIdKey);
        for (var i = 0; i < dotMarkers.length; i++) {
          var dotMarker = dotMarkers[i];
          var latLng = dotMarker.packet.getLatLngLiteral();

          if (prevLatLng !== null) {
            distance += trackdirect.services.distanceCalculator.getDistance(
              prevLatLng,
              latLng
            );
          }
          prevLatLng = latLng;
        }

        if (prevLatLng !== null) {
          var latLng = marker.packet.getLatLngLiteral();
          if (prevLatLng !== latLng) {
            distance += trackdirect.services.distanceCalculator.getDistance(
              prevLatLng,
              latLng
            );
          }
        }
      }

      var dashedPolyline =
        this._defaultMap.markerCollection.getMarkerDashedPolyline(markerIdKey);
      if (dashedPolyline !== null) {
        // We are connected to a previous marker
        if (dashedPolyline.getPathLength() == 2) {
          distance += trackdirect.services.distanceCalculator.getDistance(
            dashedPolyline.getPathItem(0),
            dashedPolyline.getPathItem(1)
          );

          // Add previous markers distance
          distance += this._getTailDistance(dashedPolyline.relatedMarkerIdKey);
        }
      }
      return distance;
    }
  }
  return null;
};

/**
 * Returns the transmit distance in meters for specified packet
 * @param {trackdirect.models.Packet} packet
 * @return int
 */
trackdirect.models.InfoWindow.prototype._getTransmitDistance = function (
  packet
) {
  if (
    typeof packet.station_location_path !== "undefined" &&
    packet.station_location_path !== null &&
    packet.station_location_path.length >= 1
  ) {
    var relatedStationLatLng = {
      lat: parseFloat(packet.station_location_path[0][0]),
      lng: parseFloat(packet.station_location_path[0][1]),
    };
    var distance = trackdirect.services.distanceCalculator.getDistance(
      packet.getLatLngLiteral(),
      relatedStationLatLng
    );
    if (distance !== null) {
      return distance;
    }
  }

  if (
    typeof packet.station_id_path !== "undefined" &&
    packet.station_id_path !== null &&
    packet.station_id_path.length >= 1
  ) {
    for (var i = 0; i < packet.station_id_path.length; i++) {
      var relatedStationId = packet.station_id_path[i];
      var relatedStationPacket =
        this._defaultMap.markerCollection.getStationLatestPacket(
          relatedStationId
        );
      if (relatedStationPacket !== null) {
        // found first station!
        break;
      }
    }

    if (relatedStationPacket !== null) {
      var relatedStationLatLng = {
        lat: parseFloat(relatedStationPacket.latitude),
        lng: parseFloat(relatedStationPacket.longitude),
      };
      var distance = trackdirect.services.distanceCalculator.getDistance(
        packet.getLatLngLiteral(),
        relatedStationLatLng
      );
      if (distance !== null) {
        return distance;
      }
    }
  }
  return null;
};
