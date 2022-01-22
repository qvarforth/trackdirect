/**
 * Class trackdirect.models.MapState
 */
trackdirect.models.MapState = function () {
  this._init();
};

/**
 * Init object
 */
trackdirect.models.MapState.prototype._init = function () {
  // Filtering on stations
  this.isFilterMode = false;
  this.filterStationIds = [];

  // Booleans that controls what is visible
  this.isGhostMarkersVisible = false;
  this.isCwopMarkersVisible = true;
  this.isStationaryMarkersVisible = true;
  this.isInternetMarkersVisible = true;
  this.isUnknownMarkersVisible = true;
  this.isOgflymMarkersVisible = true;

  // Array of vissible symbols (each value is an array with two values)
  this.visibleSymbols = [];

  /// Imperial och Metric
  this.useImperialUnit = false;

  // Show PHG and RNG circles?
  this.showPHGCircles = 0;
  this.showRNGCircles = 0;

  // Tracking
  this.trackStationId = null;
  this.onlyTrackRecentPackets = false;

  this.timeLengthInSeconds = 3600;
  this.endTimeTravelTimestamp = null;

  // Z-index counter
  this.currentMarkerZindex = 200;

  // Diff between client and server unix timestamp
  this.serverClientTimestampDiff = 0;

  // Currently open trackdirect.models.InfoWindow
  this.openInfoWindow = null;

  // markerIdKey to open info window for as soon as possible
  this.openInfoWindowForMarkerIdKey = null;
};

/**
 * Returns the currently oldest allowed packet timestamp
 * @return int
 */
trackdirect.models.MapState.prototype.getOldestAllowedPacketTimestamp =
  function () {
    var oldestAllowedTimestamp =
      Math.floor(Date.now() / 1000) - this.timeLengthInSeconds;
    if (this.endTimeTravelTimestamp !== null) {
      oldestAllowedTimestamp =
        this.endTimeTravelTimestamp - this.timeLengthInSeconds;
    }
    return oldestAllowedTimestamp;
  };

/**
 * Set the time length currently used, how old a packet may be (in seconds)
 * @param {int} seconds
 */
trackdirect.models.MapState.prototype.setTimeLength = function (seconds) {
  this.timeLengthInSeconds = seconds;
};

/**
 * Returns the time length currently used, how old a packet may be (in seconds)
 * @return {int}
 */
trackdirect.models.MapState.prototype.getTimeLength = function () {
  return this.timeLengthInSeconds;
};

/**
 * Get client timestamp based on server timestamp
 * @param {int} serverTimestamp
 * @return {int}
 */
trackdirect.models.MapState.prototype.getClientTimestamp = function (
  serverTimestamp
) {
  return serverTimestamp - this.serverClientTimestampDiff;
};

/**
 * Set normal performance by not forcing user to zoom more for details
 * @param {int} serverTimestamp
 */
trackdirect.models.MapState.prototype.setServerCurrentTimestamp = function (
  serverTimestamp
) {
  this.serverClientTimestampDiff =
    serverTimestamp - Math.floor(Date.now() / 1000);
};

/**
 * Is info window open
 */
trackdirect.models.MapState.prototype.isInfoWindowOpen = function () {
  if (this.openInfoWindow === null) {
    return false;
  }
  return this.openInfoWindow.isInfoWindowOpen();
};

/**
 * Is info window open for specified marker
 * @param {trackdirect.models.Marker} marker
 */
trackdirect.models.MapState.prototype.isMarkerInfoWindowOpen = function (
  marker
) {
  if (!this.isInfoWindowOpen()) {
    return false;
  }

  if (this.openInfoWindow.getPolyline() !== null) {
    return false;
  }

  if (this.openInfoWindow.getMarker() === marker) {
    return true;
  }

  return false;
};

/**
 * Is info window open for specified polyline
 * @param {google.maps.Polyline} polyline
 */
trackdirect.models.MapState.prototype.isPolylineInfoWindowOpen = function (
  polyline
) {
  if (!this.isInfoWindowOpen()) {
    return false;
  }

  if (this.openInfoWindow.getPolyline() === null) {
    return false;
  }

  if (this.openInfoWindow.getPolyline() === polyline) {
    return true;
  }

  return false;
};

/**
 * Returns an array of stationIds that we are fitlering on
 * @return {array}
 */
trackdirect.models.MapState.prototype.getFilterStationIds = function () {
  return this.filterStationIds;
};

/**
 * get track station
 * @return {int}
 */
trackdirect.models.MapState.prototype.getTrackStationId = function () {
  return this.trackStationId;
};
