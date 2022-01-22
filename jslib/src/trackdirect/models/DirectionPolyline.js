/**
 * Class trackdirect.models.DirectionPolyline
 * @see https://developers.google.com/maps/documentation/javascript/reference#Polyline
 * @param {trackdirect.models.Marker} marker
 * @param {trackdirect.models.Map} map
 */
trackdirect.models.DirectionPolyline = function (marker, map) {
  this._marker = marker;
  this._defaultMap = map;

  this.startTimestamp = this._marker.packet.timestamp;
  this.speed = this._marker.packet.speed;
  this.course = this._marker.packet.course;
  this.stopped = false;
  this.timerId = null;

  // Call the parent constructor
  if (typeof google === "object" && typeof google.maps === "object") {
    google.maps.Polyline.call(this, this._getGooglePolylineOptions());
  } else if (typeof L === "object") {
    L.Polyline.call(this, {}, this._getLeafletPolylineOptions());
    this.setLatLngs([
      this._getFirstCoordinate(),
      this._getExpectedCoordinate(),
    ]);
  }
};
if (typeof google === "object" && typeof google.maps === "object") {
  trackdirect.models.DirectionPolyline.prototype = Object.create(
    google.maps.Polyline.prototype
  );
} else if (typeof L === "object") {
  trackdirect.models.DirectionPolyline.prototype = Object.create(
    L.Polyline.prototype
  );
}
trackdirect.models.DirectionPolyline.prototype.constructor =
  trackdirect.models.DirectionPolyline;

/**
 * Set new path
 */
trackdirect.models.DirectionPolyline.prototype.setPathItems = function (
  pathItems
) {
  if (typeof google === "object" && typeof google.maps === "object") {
    this.setPath(pathItems);
  } else if (typeof L === "object") {
    this.setLatLngs(pathItems);
  }
};

/**
 * Get Polyline currently active Map
 * @return {google.maps.Map}
 */
trackdirect.models.DirectionPolyline.prototype.getMap = function () {
  if (typeof google === "object" && typeof google.maps === "object") {
    var map = google.maps.Polyline.prototype.getMap.call(this);
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
 * Show polyline on default map
 */
trackdirect.models.DirectionPolyline.prototype.show = function () {
  var timeInSeconds = this._getAgeInSeconds();

  if (
    this.stopped === false &&
    timeInSeconds <= 900 &&
    this._marker.packet.hasConfirmedMapId() &&
    (this._defaultMap.state.isFilterMode ||
      this._defaultMap.getZoom() >= trackdirect.settings.minZoomForMarkerTail)
  ) {
    if (typeof google === "object" && typeof google.maps === "object") {
      if (typeof this.getMap() === "undefined" || this.getMap() === null) {
        this.setMap(this._defaultMap);
      }
    } else if (typeof L === "object") {
      if (!this._defaultMap.hasLayer(this)) {
        this.addTo(this._defaultMap);
      }
    }

    this.recalculate();
  }
};

/**
 * Hide polyline
 */
trackdirect.models.DirectionPolyline.prototype.hide = function () {
  if (typeof google === "object" && typeof google.maps === "object") {
    if (this.getMap() !== null) {
      this.setMap(null);
    }
  } else if (typeof L === "object") {
    if (this._defaultMap.hasLayer(this)) {
      this._defaultMap.removeLayer(this);
    }
  }
};

/**
 * Stop it and hide it
 */
trackdirect.models.DirectionPolyline.prototype.stop = function () {
  this.stopped = true;
  this.hide();
};

/**
 * Get a suitable google polyline options object
 * @return {object}
 */
trackdirect.models.DirectionPolyline.prototype._getGooglePolylineOptions =
  function () {
    var lineCoordinates = [
      this._getFirstCoordinate(),
      this._getExpectedCoordinate(),
    ];

    var lineSymbol = {
      path: google.maps.SymbolPath.FORWARD_OPEN_ARROW,
      strokeOpacity: 1,
      scale: 0.65,
    };

    var options = {
      path: lineCoordinates,
      strokeOpacity: 0,
      strokeColor: trackdirect.services.stationColorCalculator.getColor(
        this._marker.packet
      ),
      map: null,
      icons: [
        {
          icon: lineSymbol,
          offset: "0px",
          repeat: "8px",
        },
      ],
    };
    return options;
  };

/**
 * Get a suitable leaflet polyline options object
 * @return {object}
 */
trackdirect.models.DirectionPolyline.prototype._getLeafletPolylineOptions =
  function () {
    return {
      color: trackdirect.services.stationColorCalculator.getColor(
        this._marker.packet
      ),
      weight: 4,
      opacity: 0.7,

      dashArray: "2,8",
      lineJoin: "round",
    };
  };

/**
 * Returns coordinates for the transmit polyline
 * @return {array}
 */
trackdirect.models.DirectionPolyline.prototype._getFirstCoordinate =
  function () {
    return this._marker.packet.getLatLngLiteral();
  };

/**
 * Returns coordinates for the transmit polyline
 * @return {array}
 */
trackdirect.models.DirectionPolyline.prototype._getExpectedCoordinate =
  function () {
    var timeInSeconds = this._getAgeInSeconds();
    var distance = (this.speed / 3.6) * timeInSeconds;
    var startPosition = this._getFirstCoordinate();
    if (startPosition != null) {
      return trackdirect.services.distanceCalculator.getPositionByDistance(
        startPosition,
        this.course,
        distance
      );
    }
    return null;
  };

/**
 * Animate direction polyline
 */
trackdirect.models.DirectionPolyline.prototype.recalculate = function () {
  var interval = 1000;
  var me = this;
  this.timerId = window.setInterval(function () {
    if (!me._marker.isVisible() || me.stopped || !me._marker.showAsMarker) {
      me.hide();
      clearInterval(me.timerId);
      return;
    }
    var timeInSeconds = me._getAgeInSeconds();
    if (timeInSeconds > 900) {
      // After 15 minutes we stop drawing directionPolyline
      me.stop();
      if (me.timerId !== null) {
        clearInterval(me.timerId);
      }
    } else {
      var firstPosition = me._getFirstCoordinate();
      var newPosition = me._getExpectedCoordinate();
      if (firstPosition != null && newPosition != null) {
        me.setPathItems([firstPosition, newPosition]);
      }
    }
  }, interval);
};

/**
 * Returnes the marker age in seconds
 */
trackdirect.models.DirectionPolyline.prototype._getAgeInSeconds = function () {
  var timeInSeconds = 0;
  var startTimestamp = this._defaultMap.state.getClientTimestamp(
    this.startTimestamp
  );

  if (startTimestamp < Date.now() / 1000) {
    timeInSeconds = Date.now() / 1000 - startTimestamp;
  }

  return timeInSeconds;
};
