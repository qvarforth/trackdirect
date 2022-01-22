/**
 * Class trackdirect.models.Marker
 * @see https://developers.google.com/maps/documentation/javascript/reference#Marker
 * @param {trackdirect.models.Packet} packet
 * @param {boolean} isDotMarker
 * @param {trackdirect.models.Map} map
 */
trackdirect.models.Marker = function (packet, isDotMarker, map) {
  this.packet = packet;
  this._isDotMarker = isDotMarker;
  this._defaultMap = map;

  // Call the parent constructor
  if (typeof google === "object" && typeof google.maps === "object") {
    google.maps.Marker.call(this, this._getGoogleMarkerOptions());
  } else if (typeof L === "object") {
    L.Marker.call(
      this,
      this.packet.getLatLngLiteral(),
      this._getLeafletMarkerOptions()
    );
  }

  this._init();
  if (typeof google === "object" && typeof google.maps === "object") {
    this.setMap(null);
  }
};
if (typeof google === "object" && typeof google.maps === "object") {
  trackdirect.models.Marker.prototype = Object.create(
    google.maps.Marker.prototype
  );
} else if (typeof L === "object") {
  trackdirect.models.Marker.prototype = Object.create(L.Marker.prototype);
}
trackdirect.models.Marker.prototype.constructor = trackdirect.models.Marker;

/**
 * Init object
 */
trackdirect.models.Marker.prototype._init = function () {
  // Init variables
  this._tdEventListeners = {};

  this.hasLabel = false;
  this.showAsMarker = false;
  this.overwrite = false;

  this.markerIdKey = null;
  this.label = null;

  this.transmitPolyLine = null;
  this.directionPolyLine = null;

  this.phgCircle = null;
  this.rngCircle = null;

  this.hideTimerId = null;
  this.toOldTimerId = null;

  if (!this._isDotMarker) {
    this.showAsMarker = true;
    if (
      this.packet.map_id != 1 &&
      this.packet.map_id != 2 &&
      this.packet.map_id != 12
    ) {
      // Ghost marker!
      this.setOpacity(0.5);
    } else {
      this.hasLabel = true;
    }
  }

  if (this._defaultMap.state.endTimeTravelTimestamp === null) {
    this._addMarkerToOldTimeout(0);
  }
  this._addMarkerTooltip();
};

/**
 * Add listener to events
 * @param {string} event
 * @param {string} handler
 */
trackdirect.models.Marker.prototype.addTdListener = function (event, handler) {
  if (!(event in this._tdEventListeners)) {
    this._tdEventListeners[event] = [];
  }
  this._tdEventListeners[event].push(handler);
};

/**
 * Returns true if marker is of type "dot-marker"
 */
trackdirect.models.Marker.prototype.isDotMarker = function () {
  return this._isDotMarker;
};

/**
 * Returns true if marker is visible
 * @return {boolean}
 */
trackdirect.models.Marker.prototype.isVisible = function () {
  if (typeof google === "object" && typeof google.maps === "object") {
    if (typeof this.getMap() !== "undefined" && this.getMap() !== null) {
      return true;
    }
  } else if (typeof L === "object") {
    if (this._defaultMap.hasLayer(this)) {
      return true;
    }
  }
  return false;
};

/**
 * Get position literal
 * @return {LatLngLiteral}
 */
trackdirect.models.Marker.prototype.getPositionLiteral = function () {
  if (typeof google === "object" && typeof google.maps === "object") {
    var latLng = this.getPosition();
    if (typeof latLng !== "undefined" && typeof latLng.lat === "function") {
      return { lat: latLng.lat(), lng: latLng.lng() };
    } else {
      return latLng;
    }
  } else if (typeof L === "object") {
    var latLng = this.getLatLng();
    if (typeof latLng !== "undefined") {
      return { lat: latLng.lat, lng: latLng.lng };
    } else {
      return latLng;
    }
  }
  return {};
};

/**
 * Show marker on default map
 */
trackdirect.models.Marker.prototype.show = function () {
  if (typeof google === "object" && typeof google.maps === "object") {
    if (typeof this.getMap() === "undefined" || this.getMap() === null) {
      this.setMap(this._defaultMap);
    }
  } else if (typeof L === "object") {
    if (!this._defaultMap.hasLayer(this)) {
      this.addTo(this._defaultMap);
    }
  }

  if (this.hideTimerId !== null) {
    clearTimeout(this.hideTimerId);
  }

  this._emitTdEventListeners("onshow");
};

/**
 * Hide marker
 * @param {int} delayInMilliSeconds
 * @param {boolean} onlyHideIfNeeded
 */
trackdirect.models.Marker.prototype.hide = function (
  delayInMilliSeconds,
  onlyHideIfNeeded,
  hideOpenInfoWindow
) {
  delayInMilliSeconds =
    typeof delayInMilliSeconds !== "undefined" ? delayInMilliSeconds : 0;
  onlyHideIfNeeded =
    typeof onlyHideIfNeeded !== "undefined" ? onlyHideIfNeeded : false;
  hideOpenInfoWindow =
    typeof hideOpenInfoWindow !== "undefined" ? hideOpenInfoWindow : true;

  if (delayInMilliSeconds > 0) {
    this._hideLater(delayInMilliSeconds, onlyHideIfNeeded);
    return;
  }

  if (onlyHideIfNeeded && this.shouldMarkerBeVisible()) {
    return;
  }

  if (
    hideOpenInfoWindow &&
    this._defaultMap.state.isMarkerInfoWindowOpen(this)
  ) {
    this._defaultMap.state.openInfoWindow.hide();
  }

  if (this.isVisible()) {
    if (typeof google === "object" && typeof google.maps === "object") {
      this.setMap(null);
    } else if (typeof L === "object") {
      this._defaultMap.removeLayer(this);
    }
  }

  if (this.showAsMarker) {
    this.hideLabel();
  }

  this.hidePHGCircle();
  this.hideRNGCircle();

  if (this.hideTimerId !== null) {
    clearTimeout(this.hideTimerId);
  }

  this._emitTdEventListeners("onhide");
};

/**
 * get Marker default Map
 * @return {trackdirect.models}
 */
trackdirect.models.Marker.prototype.getDefaultMap = function () {
  return this._defaultMap;
};

/**
 * get Marker currently active Map
 * @return {trackdirect.models}
 */
trackdirect.models.Marker.prototype.getMap = function () {
  if (typeof google === "object" && typeof google.maps === "object") {
    var map = google.maps.Marker.prototype.getMap.call(this);
    if (typeof map !== "undefined") {
      return map;
    }
  } else if (typeof L === "object") {
    if (this._defaultMap.hasLayer(this)) {
      return this._defaultMap;
    }
  }
  return null;
};

/**
 * get Marker Map State
 * @return {trackdirect.models.MapState}
 */
trackdirect.models.Marker.prototype.getState = function () {
  return this._defaultMap.state;
};

/**
 * get Marker zIndex
 * @return {int}
 */
trackdirect.models.Marker.prototype.getZIndex = function () {
  if (typeof google === "object" && typeof google.maps === "object") {
    return this.zIndex;
  } else if (typeof L === "object") {
    return this.options.zIndexOffset;
  }
  return 0;
};

/**
 * Show marker including all realted that should be visible at current zoom level
 */
trackdirect.models.Marker.prototype.showCompleteMarker = function () {
  // In filter-mode we only show stations that we filter on
  if (
    this._defaultMap.state.isFilterMode &&
    this._defaultMap.state.filterStationIds.indexOf(this.packet.station_id) == -1
  ) {
    return;
  }

  // We check that marker is not to old (if we are filtering we show station latest marker even if it is to old)
  if (this.shouldMarkerBeVisible()) {
    if (this.showAsMarker) {
      this.show();
    }

    if (this._defaultMap.state.isFilterMode) {
      this.showMarkerPrevPosition();
      this.showMarkerTail();
      this.showLabel();
    } else {
      if (
        this._defaultMap.getZoom() >=
        trackdirect.settings.minZoomForMarkerPrevPosition
      ) {
        // If we also should show details, do it
        this.showMarkerPrevPosition();
      }
      if (
        this._defaultMap.getZoom() >= trackdirect.settings.minZoomForMarkerTail
      ) {
        // If we also should show tail, do it
        this.showMarkerTail();
      }
      if (
        this._defaultMap.getZoom() >= trackdirect.settings.minZoomForMarkerLabel
      ) {
        // If we also should show label, do it
        this.showLabel();
      }
    }

    if (this._defaultMap.state.showPHGCircles == 1) {
      this.showPHGCircle(true);
    } else if (this._defaultMap.state.showPHGCircles == 2) {
      this.showPHGCircle(false);
    }

    if (this._defaultMap.state.showRNGCircles == 1) {
      this._showRNGCircle(true);
    } else if (this._defaultMap.state.showRNGCircles == 2) {
      this._showRNGCircle(false);
    }
  }
};

/**
 * Hide marker including all related
 */
trackdirect.models.Marker.prototype.hideCompleteMarker = function () {
  this.hide();

  // If markers is hidden also the details should be
  this.hideMarkerPrevPosition();
  this.hideMarkerTail();
};

/**
 * Show markers details that should be visible
 */
trackdirect.models.Marker.prototype.showMarkerDetails = function () {
  if (
    this._defaultMap.getZoom() >=
    trackdirect.settings.minZoomForMarkerPrevPosition
  ) {
    // If we also should show details, do it
    this.showMarkerPrevPosition();
  }

  if (this._defaultMap.getZoom() >= trackdirect.settings.minZoomForMarkerTail) {
    // If we also should show details, do it
    this.showMarkerTail();
  }

  if (
    this._defaultMap.getZoom() >= trackdirect.settings.minZoomForMarkerLabel
  ) {
    // If we also should show label, do it
    this.showLabel();
  }
};

/**
 * Hide markers details that should not be visible
 */
trackdirect.models.Marker.prototype.hideMarkerDetails = function () {
  if (
    this._defaultMap.getZoom() <
    trackdirect.settings.minZoomForMarkerPrevPosition
  ) {
    this.hideMarkerPrevPosition();
  }

  if (this._defaultMap.getZoom() < trackdirect.settings.minZoomForMarkerTail) {
    this.hideMarkerTail();
  }

  if (this._defaultMap.getZoom() < trackdirect.settings.minZoomForMarkerLabel) {
    this.hideLabel();
  }
};

/**
 * Show marker label
 */
trackdirect.models.Marker.prototype.showLabel = function () {
  if (
    !this._defaultMap.state.isFilterMode ||
    this._defaultMap.state.filterStationIds.indexOf(this.packet.station_id) > -1
  ) {
    if (
      this.isVisible() &&
      this.label !== null &&
      (this._defaultMap.getZoom() >=
        trackdirect.settings.minZoomForMarkerLabel ||
        this._defaultMap.state.filterStationIds.indexOf(
          this.packet.station_id
        ) > -1) &&
      this.hasLabel &&
      this.packet.hasConfirmedMapId()
    ) {
      this.label.show();
    }
  }
};

/**
 * Hide marker label
 */
trackdirect.models.Marker.prototype.hideLabel = function () {
  if (this.label !== null && this.hasLabel) {
    this.label.hide();
  }
};

/**
 * Show marker previous positions (the dot markers)
 */
trackdirect.models.Marker.prototype.showMarkerPrevPosition = function () {
  if (this.shouldMarkerBeVisible() && this.packet.hasConfirmedMapId()) {
    // Handle the history dots

    var oldestAllowedPacketTimestamp =
      this._defaultMap.state.getOldestAllowedPacketTimestamp();
    var dotMarkers = this._defaultMap.markerCollection.getDotMarkers(
      this.markerIdKey
    );
    for (var i = 0; i < dotMarkers.length; i++) {
      var dotMarker = dotMarkers[i];

      // Only show prev positions that is not to old (not even prev positions for filtered stations)
      if (
        this._defaultMap.state.getClientTimestamp(dotMarker.packet.timestamp) >
        oldestAllowedPacketTimestamp
      ) {
        dotMarker.show();
      }
    }

    // Handle markers that still is marker but shown as dotmarker (this happens when a newer marker exists)
    if (!this.showAsMarker) {
      this.show();
    }
  }
};

/**
 * Hide marker previous positions (the dot markers)
 */
trackdirect.models.Marker.prototype.hideMarkerPrevPosition = function () {
  if (this.packet.hasConfirmedMapId()) {
    // Handle the history dots
    var dotMarkers = this._defaultMap.markerCollection.getDotMarkers(
      this.markerIdKey
    );
    for (var i = 0; i < dotMarkers.length; i++) {
      var dotMarker = dotMarkers[i];
      dotMarker.hide();
    }

    if (!this.showAsMarker) {
      // Handle markers that still is marker but shown as dotmarker (this happens when a newer packet with another markerId exists)
      this.hide();
    }
  }
};

/**
 * Show marker tail (the polyline)
 */
trackdirect.models.Marker.prototype.showMarkerTail = function () {
  if (this.shouldMarkerBeVisible()) {
    if (
      this.packet.hasConfirmedMapId() === false &&
      this._defaultMap.state.showGhostPosition
    ) {
      // Ghost markers is calculated as tail
      this.show();
    }

    // Handle polylines
    if (
      this._defaultMap.markerCollection.hasPolyline(this.markerIdKey) &&
      this.packet.hasConfirmedMapId()
    ) {
      var polyline = this._defaultMap.markerCollection.getMarkerPolyline(
        this.markerIdKey
      );
      // Before we show polyline we remove all points that is to old
      while (
        this._defaultMap.state.getClientTimestamp(
          polyline.getPathItem(0).marker.packet.timestamp
        ) < this._defaultMap.state.getOldestAllowedPacketTimestamp()
      ) {
        var relatedMarker = polyline.getPathItem(0).marker;
        if (relatedMarker.getMap() === null) {
          // related marker is to old and is not visible, it will never be shown.
          // We let the regular remove-functionality remove the marker
          polyline.removePathItem(0);
        } else {
          break;
        }
      }
      polyline.show();
    }

    // Handle dashed polylines
    var dashedPolyline =
      this._defaultMap.markerCollection.getMarkerDashedPolyline(
        this.markerIdKey
      );
    if (dashedPolyline !== null && this.packet.hasConfirmedMapId()) {
      // The related marker is the marker where the dashed polyline STARTS
      var dashedPolyLineRelatedMarker =
        this._defaultMap.markerCollection.getMarker(
          dashedPolyline.relatedMarkerIdKey
        );

      // Validate that the related marker is shown or will be shown before showing dashed polyline
      // Since related marker is older than current we never need to show it if it is to old (not even when we are filtering)
      if (
        this._defaultMap.state.getClientTimestamp(
          dashedPolyLineRelatedMarker.packet.timestamp
        ) > this._defaultMap.state.getOldestAllowedPacketTimestamp()
      ) {
        dashedPolyline.show();

        if (typeof dashedPolyline.relatedMarkerIdKey !== "undefined") {
          var relatedMarker = this._defaultMap.markerCollection.getMarker(
            dashedPolyline.relatedMarkerIdKey
          );
          if (
            relatedMarker !== null &&
            relatedMarker.markerIdKey !== this.markerIdKey
          ) {
            relatedMarker.showMarkerTail();
          }
        }
      }
    }

    // Handle direction polyline
    if (this.directionPolyLine !== null) {
      this.directionPolyLine.show();
    }
  }
};

/**
 * Hide marker tail (the polyline)
 * @param {int} markerIdKey
 */
trackdirect.models.Marker.prototype.hideMarkerTail = function (markerIdKey) {
  var latestMarker = this._defaultMap.markerCollection.getStationLatestMarker(
    this.packet.station_id
  );
  if (
    this._defaultMap.state.isMarkerInfoWindowOpen(this) ||
    this._defaultMap.state.isMarkerInfoWindowOpen(latestMarker)
  ) {
    // do not hide if info window is open
    return;
  }

  if (
    this.packet.map_id != 1 &&
    this.packet.map_id != 2 &&
    this.packet.map_id != 12
  ) {
    // Ghost markers is calculated as tail
    this.hide();
    if (this.showAsMarker) {
      this.hideLabel();
    }
  }

  // Handle polylines
  var polyline = this._defaultMap.markerCollection.getMarkerPolyline(
    this.markerIdKey
  );
  if (polyline !== null) {
    if (this._defaultMap.state.isPolylineInfoWindowOpen(polyline)) {
      this._defaultMap.state.openInfoWindow.hide();
    }

    polyline.hide();
  }

  // TODO: NEEDED?
  // Handle dashed polylines that STARTS at this marker
  /*
    if (this._defaultMap.markerCollection.hasRelatedDashedPolyline(this)) {
        if (this._defaultMap.state.isPolylineInfoWindowOpen(this._relatedMarkerOriginDashedPolyLine)) {
            this._defaultMap.state.openInfoWindow.hide();
        }
        this._relatedMarkerOriginDashedPolyLine.hide();
    }
    */

  // Handle dashed polylines that ENDS at this marker
  // Since tail for this marker is hidden also the dashed tail should be hidden
  var dashedPolyline =
    this._defaultMap.markerCollection.getMarkerDashedPolyline(this.markerIdKey);
  if (dashedPolyline !== null) {
    dashedPolyline.hide();

    if (typeof dashedPolyline.relatedMarkerIdKey !== "undefined") {
      var relatedMarker = this._defaultMap.markerCollection.getMarker(
        dashedPolyline.relatedMarkerIdKey
      );
      if (
        relatedMarker !== null &&
        relatedMarker.markerIdKey !== this.markerIdKey
      ) {
        relatedMarker.hideMarkerTail();
      }
    }
  }

  // Handle direction polyline
  if (this.directionPolyLine !== null) {
    this.directionPolyLine.hide();
  }
};

/**
 * Hide RNG Cirlce
 */
trackdirect.models.Marker.prototype.hideRNGCircle = function () {
  if (this.rngCircle !== null) {
    this.rngCircle.hide();
  }
};

/**
 * Show marker RNG Cirlce
 * @param {boolean} isHalf
 */
trackdirect.models.Marker.prototype.showRNGCircle = function (isHalf) {
  this.hideRNGCircle();
  this.rngCircle = new trackdirect.models.RngCircle(
    this.packet,
    this._defaultMap,
    isHalf
  );
  this.rngCircle.show();
};

/**
 * Hide RNG Cirlce
 */
trackdirect.models.Marker.prototype.hidePHGCircle = function () {
  if (this.phgCircle !== null) {
    this.phgCircle.hide();
  }
};

/**
 * Show marker RNG Cirlce
 * @param {boolean} isHalf
 */
trackdirect.models.Marker.prototype.showPHGCircle = function (isHalf) {
  this.hidePHGCircle();
  this.phgCircle = new trackdirect.models.PhgCircle(
    this.packet,
    this._defaultMap,
    isHalf
  );
  this.phgCircle.show();
};

/**
 * Set this marker to be overwritten by next packet from this station
 */
trackdirect.models.Marker.prototype.markToBeOverWritten = function () {
  this.overwrite = true;
};

/**
 * Returns true if marker is moving and is based on only one single packet
 * @return boolean
 */
trackdirect.models.Marker.prototype.isSingleMovingMarker = function () {
  var markerCounter = 0;
  if (
    typeof this.packet.marker_counter !== "undefined" &&
    this.packet.marker_counter !== null
  ) {
    markerCounter = this.packet.marker_counter;
  }

  if (
    this.packet.position_timestamp == this.packet.timestamp &&
    this.packet.is_moving == 1 &&
    [1, 2, 7, 12].indexOf(this.packet.map_id) >= 0 &&
    markerCounter <= 1 &&
    !this._defaultMap.markerCollection.hasDotMarkers(this.markerIdKey)
  ) {
    return true;
  }
  return false;
};

/**
 * Returns true if marker should be visible, otherwise false
 * @return {boolean}
 */
trackdirect.models.Marker.prototype.shouldMarkerBeVisible = function () {
  if (this.packet.map_id == 14) {
    // A kill-packet should never be visible
    return false;
  }

  if (
    this.packet.source_id == 2 &&
    !this._defaultMap.state.isCwopMarkersVisible
  ) {
    // CWOP weather stations should not be visible
    return false;
  }

  if (!this._defaultMap.state.isStationaryMarkersVisible) {
    if (!this.isMovingStation()) {
      return false;
    }
  }

  if (!this._defaultMap.state.isUnknownMarkersVisible) {
    if (this.packet.station_name.substring(0, 7) == "UNKNOWN") {
      return false;
    }
  }

  if (!this._defaultMap.state.isOgflymMarkersVisible) {
    if (this.packet.raw_path.indexOf("OGFLYM") >= 0) {
      return false;
    }
  }

  if (!this._defaultMap.state.isInternetMarkersVisible) {
    if (
      this.packet.raw_path.indexOf("TCPIP") >= 0 ||
      this.packet.raw_path.indexOf("qAC") >= 0 ||
      this.packet.raw_path.indexOf("qAX") >= 0 ||
      this.packet.raw_path.indexOf("qAU") >= 0 ||
      this.packet.raw_path.indexOf("qAS") >= 0
    ) {
      if (this.packet.station_id_path.length == 0) {
        // Internet stations should not be visible
        return false;
      }
    }
  }

  if (this._defaultMap.state.visibleSymbols.length > 0) {
    var symbolFound = false;
    for (var key in this._defaultMap.state.visibleSymbols) {
      var visibleSymbol = this._defaultMap.state.visibleSymbols[key];
      if (
        this.packet.symbol.charCodeAt(0) == visibleSymbol[0] &&
        this.packet.symbol_table.charCodeAt(0) == visibleSymbol[1]
      ) {
        symbolFound = true;
      }
    }
    if (!symbolFound) {
      return false;
    }
  }

  if (
    this.packet.map_id != 1 &&
    this.packet.map_id != 2 &&
    this.packet.map_id != 12 &&
    !this._defaultMap.state.isGhostMarkersVisible
  ) {
    // Ghost positions should not be visible
    return false;
  }

  if (
    this._defaultMap.state.isFilterMode &&
    this._defaultMap.state.filterStationIds.indexOf(this.packet.station_id) > -1
  ) {
    // We are filtering and we are filtering on this station
    var latestStationMarker =
      this._defaultMap.markerCollection.getStationLatestMarker(
        this.packet.station_id
      );
    if (
      this._defaultMap.state.getClientTimestamp(this.packet.timestamp) <=
        this._defaultMap.state.getOldestAllowedPacketTimestamp() &&
      typeof latestStationMarker !== "undefined" &&
      latestStationMarker !== null &&
      !this._isMarkersEqual(latestStationMarker)
    ) {
      // Is to old (and later confirmed markers exists)
      return false;
    }

    return true;
  } else {
    if (
      this._defaultMap.state.isFilterMode &&
      this._defaultMap.state.filterStationIds.indexOf(
        this.packet.station_id
      ) === -1
    ) {
      // We are filtering and we are not filtering on this station
      return false;
    }

    if (
      this.packet.map_id != 1 &&
      this.packet.map_id != 2 &&
      this.packet.map_id != 12 &&
      this._defaultMap.getZoom() < trackdirect.settings.minZoomForMarkerTail
    ) {
      // Ghost markers is only visible when tail is visible (when we are not in filtering mode)
      return false;
    }

    if (
      this._defaultMap.state.getClientTimestamp(this.packet.timestamp) <=
      this._defaultMap.state.getOldestAllowedPacketTimestamp()
    ) {
      // Is to old
      return false;
    }

    if (
      this._defaultMap.getZoom() < trackdirect.settings.minZoomForMarkers
    ) {
      // We are to much zoomed out
      return false;
    }

    return true;
  }
};

/**
 * Returnes true if it looks like it is a moving marker
 * @return {boolean}
 */
trackdirect.models.Marker.prototype.isMovingStation = function () {
  if (this.packet.is_moving == 0) {
    return false;
  }

  if (
    this._defaultMap.state.getClientTimestamp(this.packet.position_timestamp) <
    this._defaultMap.state.getOldestAllowedPacketTimestamp()
  ) {
    // This marker is supposed to be moving but has not moved for a long time
    // Check that we have no later marker for this station that is considered moving
    var stationLatestMovingMarkerIdKey =
      this._defaultMap.markerCollection.getStationLatestMovingMarkerIdKey(
        this.packet.station_id
      );
    if (stationLatestMovingMarkerIdKey == this.markerIdKey) {
      // Stationary stations should not be visible
      return false;
    }
  }

  return true;
};

/**
 * Stop existing direction polyline is exists and is active
 */
trackdirect.models.Marker.prototype.stopDirectionPolyline = function () {
  if (this.directionPolyLine !== null) {
    this.directionPolyLine.stop();
  }
};

/**
 * Stop the marker to old timeout that removes marker
 */
trackdirect.models.Marker.prototype.stopToOldTimeout = function () {
  clearTimeout(this.toOldTimerId);
  var dotMarkers = this._defaultMap.markerCollection.getDotMarkers(
    this.markerIdKey
  );
  for (var j = 0; j < dotMarkers.length; j++) {
    clearTimeout(dotMarkers[j].toOldTimerId);
  }
};

/**
 * Get tooltip content for this marker
 * @return {string}
 */
trackdirect.models.Marker.prototype.getToolTipContent = function () {
  var iconUrl = trackdirect.services.symbolPathFinder.getFilePath(
    this.packet.symbol_table,
    this.packet.symbol,
    null,
    null,
    null,
    20,
    20
  );
  var date = new Date(this.packet.timestamp * 1000);
  var positionDate = new Date(this.packet.position_timestamp * 1000);

  var dateString = moment(date).format(
    trackdirect.settings.dateFormatNoTimeZone
  );
  if (this.packet.timestamp > this.packet.position_timestamp) {
    dateString =
      moment(positionDate).format(trackdirect.settings.dateFormatNoTimeZone) +
      " - " +
      moment(date).format(trackdirect.settings.dateFormatNoTimeZone);
  }

  if (this.packet.getOgnRegistration() != null) {
    var name = escapeHtml(this.packet.station_name);
    name += ", ";
    name += escapeHtml(this.packet.getOgnRegistration());
    if (this.packet.getOgnCN() !== null) {
      name += " [" + escapeHtml(this.packet.getOgnCN()) + "]";
    }
    return (
      '<div><img style="float: left; width:20px; height:20px;" src="' +
      iconUrl +
      '" />' +
      '<span style="font-weight: bold; font-family: Helvetica; font-size: 10px; line-height: 22px; margin-left: 5px; margin-right: 25px">' +
      name +
      "</span></div>" +
      '<div style="clear:both; font-family: Helvetica; font-size: 9px;">' +
      dateString +
      "</div>"
    );
  } else if (this.packet.station_name == this.packet.sender_name) {
    return (
      '<div><img style="float: left; width:20px; height:20px;" src="' +
      iconUrl +
      '" />' +
      '<span style="font-weight: bold; font-family: Helvetica; font-size: 10px; line-height: 22px; margin-left: 5px; margin-right: 25px">' +
      escapeHtml(this.packet.station_name) +
      "</span></div>" +
      '<div style="clear:both; font-family: Helvetica; font-size: 9px;">' +
      dateString +
      "</div>"
    );
  } else {
    return (
      '<div><img style="float: left; width:20px; height:20px;" src="' +
      iconUrl +
      '" />' +
      '<span style="font-weight: bold; font-family: Helvetica; font-size: 10px; line-height: 22px; margin-left: 5px; margin-right: 25px">' +
      escapeHtml(this.packet.station_name) +
      "</span></div>" +
      '<div style="clear:both; font-family: Helvetica; font-size: 9px;">Sent by ' +
      escapeHtml(this.packet.sender_name) +
      "</div>" +
      '<div style="clear:both; font-family: Helvetica; font-size: 9px;">' +
      dateString +
      "</div>"
    );
  }
};

/**
 * Get a suitable google marker options object
 * @return {object}
 */
trackdirect.models.Marker.prototype._getGoogleMarkerOptions = function () {
  var anchorPoint = null;
  if (this._isDotMarker) {
    var colorId = trackdirect.services.stationColorCalculator.getColorId(
      this.packet
    );
    var iconUrl =
      trackdirect.settings.baseUrl +
      trackdirect.settings.imagesBaseDir +
      "dotColor" +
      colorId +
      ".png";
    var scaledImageSize = new google.maps.Size(12, 12);
    var imageSize = new google.maps.Size(12, 12);
    var imageAnchor = new google.maps.Point(6, 6);
    var opacity = 1.0;
  } else {
    var scalePx = 24;
    var sizePx = 24;
    if (this._shouldMarkerSymbolBeScaled()) {
      scalePx = 48;
    }
    if (this.packet.course !== null) {
      sizePx = sizePx + 7;
      if (scalePx < sizePx) {
        scalePx = sizePx;
      }
    }

    var imageSize = new google.maps.Size(scalePx, scalePx);
    var imageAnchor = new google.maps.Point(
      Math.floor(scalePx / 2),
      Math.floor(scalePx / 2)
    );
    var scaledImageSize = new google.maps.Size(scalePx, scalePx);
    var iconUrl = trackdirect.services.symbolPathFinder.getFilePath(
      this.packet.symbol_table,
      this.packet.symbol,
      this.packet.course,
      sizePx,
      sizePx,
      scalePx,
      scalePx
    );
    if (isHighDensity()) {
      imageSize = new google.maps.Size(scalePx * 2, scalePx * 2);
      anchorPoint = new google.maps.Point(0, -Math.floor(scalePx / 2));
      iconUrl = trackdirect.services.symbolPathFinder.getFilePath(
        this.packet.symbol_table,
        this.packet.symbol,
        this.packet.course,
        sizePx,
        sizePx,
        scalePx * 2,
        scalePx * 2
      );
    }

    var opacity = 1.0;
  }

  return {
    position: this.packet.getLatLngLiteral(),
    zIndex: this._defaultMap.state.currentMarkerZindex,
    icon: {
      url: iconUrl,
      size: imageSize,
      scaledSize: scaledImageSize,
      origin: new google.maps.Point(0, 0),
      anchor: imageAnchor,
    },
    opacity: opacity,
    anchorPoint: anchorPoint,
  };
};

/**
 * Get a suitable leaflet marker options object
 * @return {object}
 */
trackdirect.models.Marker.prototype._getLeafletMarkerOptions = function () {
  if (this._isDotMarker) {
    var colorId = trackdirect.services.stationColorCalculator.getColorId(
      this.packet
    );
    var iconUrl =
      trackdirect.settings.baseUrl +
      trackdirect.settings.imagesBaseDir +
      "dotColor" +
      colorId +
      ".png";
    var icon = L.icon({
      iconUrl: iconUrl,
      iconSize: [12, 12],
      iconAnchor: [6, 6],
    });
    var opacity = 0.8;
  } else {
    var scalePx = 24;
    var sizePx = 24;
    if (this._shouldMarkerSymbolBeScaled()) {
      scalePx = 48;
    }
    if (this.packet.course !== null) {
      sizePx = sizePx + 7;
      if (scalePx < sizePx) {
        scalePx = sizePx;
      }
    }

    var iconUrl = trackdirect.services.symbolPathFinder.getFilePath(
      this.packet.symbol_table,
      this.packet.symbol,
      this.packet.course,
      sizePx,
      sizePx,
      scalePx,
      scalePx
    );
    var iconRetinaUrl = trackdirect.services.symbolPathFinder.getFilePath(
      this.packet.symbol_table,
      this.packet.symbol,
      this.packet.course,
      sizePx,
      sizePx,
      scalePx * 2,
      scalePx * 2
    );
    var icon = L.icon({
      iconUrl: iconUrl,
      iconRetinaUrl: iconRetinaUrl,
      iconSize: [scalePx, scalePx],
      iconAnchor: [Math.floor(scalePx / 2), Math.floor(scalePx / 2)],
    });

    var opacity = 1.0;
  }

  var tooltipTitle = "";
  if (typeof L.tooltip == "undefined") {
    tooltipTitle = this.packet.station_name;
  }

  return {
    zIndexOffset: this._defaultMap.state.currentMarkerZindex,
    icon: icon,
    opacity: opacity,
    title: tooltipTitle,
  };
};

/**
 * Returnes ture for symbols that that look better if they are scaled to twice the size
 * @param {boolean}
 */
trackdirect.models.Marker.prototype._shouldMarkerSymbolBeScaled = function () {
  if (typeof trackdirect.settings.symbolsToScale === "undefined") {
    return false;
  }

  for (var i = 0; i < trackdirect.settings.symbolsToScale.length; i++) {
    var symbol = trackdirect.settings.symbolsToScale[i][0];
    var symbolTable = trackdirect.settings.symbolsToScale[i][1];

    if (symbolTable == null && this.packet.symbol.charCodeAt() == symbol) {
      return true;
    } else if (
      this.packet.symbol.charCodeAt() == symbol &&
      this.packet.symbol_table.charCodeAt() == symbolTable
    ) {
      return true;
    }
  }

  return false;
};

/**
 * Hide marker
 * @param {int} delayInMilliSeconds
 * @param {boolean} hideIfNeeded
 */
trackdirect.models.Marker.prototype._hideLater = function (
  delayInMilliSeconds,
  onlyHideIfNeeded
) {
  var me = this;
  this.hideTimerId = window.setTimeout(function () {
    if (me._defaultMap.state.isMarkerInfoWindowOpen(me)) {
      // User is looking at this marker, try to hide it later
      me.hide(500);
    } else {
      // Only hide it if we are not filtering or if station has newer markers
      if (!me.shouldMarkerBeVisible()) {
        me.hide(0, onlyHideIfNeeded);
      }
    }
  }, delayInMilliSeconds);
};

/**
 * Create marker tooltip
 */
trackdirect.models.Marker.prototype._addMarkerTooltip = function () {
  if (typeof google === "object" && typeof google.maps === "object") {
    this._addMarkerGoogleMapTooltip();
  } else if (typeof L === "object") {
    this._addMarkerLeafletMapTooltip();
  }
};

/**
 * Create Leaflet map tooltip on marker
 */
trackdirect.models.Marker.prototype._addMarkerLeafletMapTooltip = function () {
  if (!trackdirect.isMobile) {
    if (typeof L.tooltip != "undefined") {
      var tooltip = L.tooltip({
        direction: "right",
        noWrap: true,
        offset: [6, 30],
        className: "leaflet-marker-tooltiptext",
      });
    }

    var me = this;
    var isMyTooltipVisible = false;
    this.on("mouseover", function (e) {
      if (typeof tooltip !== "undefined") {
        tooltip.setContent(me.getToolTipContent());
        tooltip.setLatLng(
          new L.LatLng(me.packet.latitude, me.packet.longitude)
        );
        tooltip.addTo(me._defaultMap);
        isMyTooltipVisible = true;
      }

      if (me.transmitPolyLine == null) {
        me.transmitPolyLine = new trackdirect.models.TransmitPolyline(
          me.packet,
          me._defaultMap
        );
      }
      me.transmitPolyLine.show();
    });

    this.on("mouseout", function (e) {
      if (me.transmitPolyLine != null && me.transmitPolyLine.isVisible()) {
        me.transmitPolyLine.hide(2000);
      }

      if (
        typeof tooltip !== "undefined" &&
        isMyTooltipVisible &&
        me._defaultMap.hasLayer(tooltip)
      ) {
        tooltip.remove();
        isMyTooltipVisible = false;
      }
    });

    this.on("remove", function (e) {
      if (me.transmitPolyLine != null && me.transmitPolyLine.isVisible()) {
        me.transmitPolyLine.hide(0);
      }

      if (
        typeof tooltip !== "undefined" &&
        isMyTooltipVisible &&
        me._defaultMap.hasLayer(tooltip)
      ) {
        tooltip.remove();
        isMyTooltipVisible = false;
      }
    });
  }
};

/**
 * Create Google map tooltip on marker
 */
trackdirect.models.Marker.prototype._addMarkerGoogleMapTooltip = function () {
  if (!trackdirect.isMobile) {
    if (!$("#marker-tooltip").length) {
      // Does not exists, create it
      var tooltip = $(document.createElement("div"));
      tooltip.attr("id", "marker-tooltip");
      tooltip.css("display", "none");
      tooltip.css("position", "absolute");

      tooltip.css("margin", "15px");
      tooltip.css("z-index", "90");
      tooltip.css("padding", "3px");

      // opacity
      tooltip.css("opacity", "0.95");
      tooltip.css("filter", "alpha(opacity=95)"); // For IE8 and earlier

      // Radius
      tooltip.css("-webkit-border-radius", "1px");
      tooltip.css("-moz-border-radius", "1px");
      tooltip.css("border-radius", "1px");

      // Shadow
      tooltip.css("-webkit-box-shadow", "0px 0px 3px 0px rgba(0,0,0,0.3)");
      tooltip.css("-moz-box-shadow", "0px 0px 3px 0px rgba(0,0,0,0.3)");
      tooltip.css("box-shadow", "0px 0px 3px 0px rgba(0,0,0,0.3)");

      tooltip.css("background-color", "#fff");
      tooltip.css("background", "#ffffff");

      $("body").append(tooltip);
    }

    var me = this;
    var isMyTooltipVisible = false;
    google.maps.event.addListener(this, "mouseover", function () {
      var point = this._fromGoogleLatLngToPoint(me.getPosition());
      var mapElementId = this._defaultMap.getMapElementId();
      $("#marker-tooltip")
        .html(me.getToolTipContent())
        .css({
          left: point.x + $("#" + mapElementId).offset().left,
          top: point.y + $("#" + mapElementId).offset().top,
        })
        .show();
      isMyTooltipVisible = true;

      if (me.transmitPolyLine == null) {
        me.transmitPolyLine = new trackdirect.models.TransmitPolyline(
          me.packet,
          me._defaultMap
        );
      }
      me.transmitPolyLine.show();
    });

    google.maps.event.addListener(this, "mouseout", function () {
      if (me.transmitPolyLine != null && me.transmitPolyLine.isVisible()) {
        me.transmitPolyLine.hide(2000);
      }

      if (isMyTooltipVisible) {
        $("#marker-tooltip").hide();
        isMyTooltipVisible = false;
      }
    });

    this.addTdListener("onhide", function () {
      if (me.transmitPolyLine != null && me.transmitPolyLine.isVisible()) {
        me.transmitPolyLine.hide(0);
      }

      if (isMyTooltipVisible) {
        $("#marker-tooltip").hide();
        isMyTooltipVisible = false;
      }
    });
  }
};

/**
 * Convert Google latlng to Point
 * @param {object} LatLng
 * @return {object} Point
 */
trackdirect.models.Marker.prototype._fromGoogleLatLngToPoint = function (
  latLng
) {
  var topRight = this._defaultMap
    .getProjection()
    .fromLatLngToPoint(this._defaultMap.getBounds().getNorthEast());
  var bottomLeft = this._defaultMap
    .getProjection()
    .fromLatLngToPoint(this._defaultMap.getBounds().getSouthWest());
  var scale = Math.pow(2, this._defaultMap.getZoom());
  var worldPoint = this._defaultMap.getProjection().fromLatLngToPoint(latLng);
  return new google.maps.Point(
    (worldPoint.x - bottomLeft.x) * scale,
    (worldPoint.y - topRight.y) * scale
  );
};

/**
 * Returns true if markers are equal
 * @param {object} marker2
 * @return {boolean}
 */
trackdirect.models.Marker.prototype._isMarkersEqual = function (marker2) {
  var marker1 = this;
  if (
    typeof marker2 !== "undefined" &&
    marker2 !== null &&
    typeof marker1.packet !== "undefined" &&
    typeof marker2.packet !== "undefined" &&
    marker1.packet.station_id === marker2.packet.station_id &&
    marker1.packet.timestamp === marker2.packet.timestamp &&
    Math.round(marker1.packet.latitude * 100000) ===
      Math.round(marker2.packet.latitude * 100000) &&
    Math.round(marker1.packet.longitude * 100000) ===
      Math.round(marker2.packet.longitude * 100000) &&
    marker1.packet.map_id === marker2.packet.map_id
  ) {
    return true;
  } else {
    return false;
  }
};

/**
 * Create timeout that removes marker when it it to old
 * @param {int} altDelayMilliSeconds
 */
(trackdirect.models.Marker.prototype._addMarkerToOldTimeout = function (
  altDelayMilliSeconds
) {
  var markerCollection = this._defaultMap.markerCollection;
  var state = this._defaultMap.state;
  var delay =
    (this._defaultMap.state.getClientTimestamp(this.packet.timestamp) -
      state.getOldestAllowedPacketTimestamp()) *
    1000;
  if (altDelayMilliSeconds !== 0) {
    delay = altDelayMilliSeconds;
  }

  if (delay < 0) {
    // Looks like this marker should be hidden allready, make sure it is soon
    delay = 10;
  }

  if (typeof this.toOldTimerId !== "undefined" && this.toOldTimerId !== null) {
    clearTimeout(this.toOldTimerId);
  }

  var me = this;
  this.toOldTimerId = window.setTimeout(function () {
    if (me._defaultMap.state.isMarkerInfoWindowOpen(me)) {
      // User is looking at this marker, try again later...
      me._addMarkerToOldTimeout(500);
    } else {
      var latestStationMarker = markerCollection.getStationLatestMarker(
        me.packet.station_id
      );
      var latestMarker = markerCollection.getMarker(me.markerIdKey);

      // Only hide it if we are not filtering or if station has newer markers
      if (
        !me._isMarkersEqual(latestStationMarker) ||
        state.filterStationIds.indexOf(me.packet.station_id) == -1
      ) {
        if (latestMarker === me) {
          // This is the latest marker for this markerId, hide all of it!
          var callback = function () {
            me.hideCompleteMarker();
            markerCollection.resetMarkerPolyline(me.markerIdKey);
            markerCollection.resetDotMarkers(me.markerIdKey);
          };
          trackdirect.services.callbackExecutor.add(me, callback, []);
        } else if (markerCollection.hasDotMarkers(me.markerIdKey)) {
          // We should hide a dotmarker that we know exists
          var index = markerCollection.getDotMarkerIndex(me.markerIdKey, me);
          if (index == 0) {
            var callback = function () {
              if (markerCollection.hasDotMarkers(me.markerIdKey)) {
                var success = markerCollection.removeOldestDotMarker(
                  me.markerIdKey
                );
                if (!success) {
                  // Failed (should not happen), we try again later
                  me._addMarkerToOldTimeout(500);
                }
              }
            };

            trackdirect.services.callbackExecutor.add(me, callback, []);
          } else if (index > 0) {
            // Reschedule first marker removal (just to be sure)
            var dotMarkers = markerCollection.getDotMarkers(me.markerIdKey);
            dotMarkers[0]._addMarkerToOldTimeout(0);

            // Try again later
            me._addMarkerToOldTimeout(100);
          }
        }
      } else {
        // Check again in a while if station has got a new marker
        me._addMarkerToOldTimeout(1000);
      }
    }
  }, delay);
}),
  /**
   * Emit all event listeners for a specified event
   * @param {string} event
   * @param {object} arg
   */
  (trackdirect.models.Marker.prototype._emitTdEventListeners = function (
    event,
    arg
  ) {
    if (event in this._tdEventListeners) {
      for (var i = 0; i < this._tdEventListeners[event].length; i++) {
        this._tdEventListeners[event][i](arg);
      }
    }
  });
