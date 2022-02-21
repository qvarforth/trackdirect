/**
 * Class trackdirect.models.StationCoveragePolygon
 * @param {LatLngLiteral} center
 * @param {trackdirect.models.Map} map
 * @param {boolean} tryToShowCoveragePolygon
 */
trackdirect.models.StationCoveragePolygon = function (
  center,
  map,
  tryToShowCoveragePolygon
) {
  tryToShowCoveragePolygon =
    typeof tryToShowCoveragePolygon !== "undefined"
      ? tryToShowCoveragePolygon
      : true;
  this._showPolygon = tryToShowCoveragePolygon;

  this._map = map;
  this._center = center;
  this._isRequestedToBeVisible = false;

  this._polygon = null;
  this._polygonCoordinates = null;

  this._heatmapCoordinates = null;
  this._heatmap = null;

  this._tdEventListeners = {};
  this._tdEventListenersOnce = {};

  // I recommend ignoring positions with a very long distance.
  // Ignoring everything with a distance longer than 1000km is reasonable.
  this._upperMaxRangeInMeters = 1000 * 1000;

  // To get a smooth ploygon we add som padding to the convex hull positions.
  this._paddingInPercentOfMaxRange = 10;
  this._paddingMinInMeters = 1000;
};

/**
 * Set coverage data
 * @param {array} data
 * @param {int} percentile
 */
trackdirect.models.StationCoveragePolygon.prototype.setData = function (data, percentile) {
  this._addParametersToData(data);
  this._heatmapCoordinates = this._getCoordinates(data);

  if (this._showPolygon) {
    var maxRange = this._getCoveragePolygonMaxRange(data, percentile);
    if (maxRange <= 0) {
      this._showPolygon = false;
    } else {
      this._polygonCoordinates = this._getConvexHullCoordinates(data, maxRange);
    }
  }

  if (typeof google === "object" && typeof google.maps === "object") {
    this._googleMapsInit();
  } else if (typeof L === "object") {
    this._leafletInit();
  }
};

/**
 * Add listener to events
 * @param {string} event
 * @param {string} handler
 */
trackdirect.models.StationCoveragePolygon.prototype.addTdListener = function (
  event,
  handler,
  execOnce
) {
  execOnce = typeof execOnce !== "undefined" ? execOnce : false;

  if (execOnce) {
    if (!(event in this._tdEventListenersOnce)) {
      this._tdEventListenersOnce[event] = [];
    }
    this._tdEventListenersOnce[event].push(handler);
  } else {
    if (!(event in this._tdEventListeners)) {
      this._tdEventListeners[event] = [];
    }
    this._tdEventListeners[event].push(handler);
  }
};

/**
 * Returns true if polygon has an area
 * @return {boolean}
 */
trackdirect.models.StationCoveragePolygon.prototype.hasContent = function () {
  if (
    this._heatmapCoordinates !== null &&
    this._heatmapCoordinates.length > 0
  ) {
    return true;
  }
  return false;
};

/**
 * Returns true if polygon is visible
 * @return {boolean}
 */
trackdirect.models.StationCoveragePolygon.prototype.isRequestedToBeVisible =
  function () {
    return this._isRequestedToBeVisible;
  };

/**
 * Request polygon to be shown when complete
 */
trackdirect.models.StationCoveragePolygon.prototype.showWhenDone = function () {
  this._isRequestedToBeVisible = true;
};

/**
 * Show coverage
 */
trackdirect.models.StationCoveragePolygon.prototype.show = function () {
  if (typeof google === "object" && typeof google.maps === "object") {
    if (this._polygon !== null) {
      this._polygon.setMap(this._map);
    }
    if (this._heatmap !== null) {
      this._heatmap.setMap(this._map);
    }
  } else if (typeof L === "object") {
    if (this._polygon !== null) {
      this._polygon.addTo(this._map);
    }
    if (this._heatmap !== null) {
      this._heatmap.addTo(this._map);
    }
  }
  this._isRequestedToBeVisible = true;

  // show will be called again when data has been updated
  if (this._showPolygon && this._polygonCoordinates !== null) {
    this._emitTdEventListeners("visible");
  } else if (this._heatmapCoordinates !== null) {
    this._emitTdEventListeners("visible");
  }
};

/**
 * Hide coverage
 * @param {boolean} stillMarkAsVisible
 */
trackdirect.models.StationCoveragePolygon.prototype.hide = function (
  stillMarkAsVisible
) {
  stillMarkAsVisible =
    typeof stillMarkAsVisible !== "undefined" ? stillMarkAsVisible : false;

  if (typeof google === "object" && typeof google.maps === "object") {
    if (this._polygon !== null) {
      this._polygon.setMap(null);
    }
    if (this._heatmap !== null) {
      this._heatmap.setMap(null);
    }
  } else if (typeof L === "object") {
    if (this._polygon !== null) {
      this._map.removeLayer(this._polygon);
    }
    if (this._heatmap !== null) {
      this._map.removeLayer(this._heatmap);
    }
  }
  if (!stillMarkAsVisible) {
    this._isRequestedToBeVisible = false;
  }
  this._emitTdEventListeners("hidden");
};

/**
 * Init function for Gogle Maps
 */
trackdirect.models.StationCoveragePolygon.prototype._googleMapsInit =
  function () {
    if (
      this._polygonCoordinates !== null &&
      this._polygonCoordinates.length > 0
    ) {
      this._polygon = new google.maps.Polygon({
        paths: this._polygonCoordinates,
        strokeColor: "#0000FF",
        strokeOpacity: 0,
        strokeWeight: 0,
        fillColor: "#0000FF",
        fillOpacity: 0.2,
      });
    }

    if (
      this._heatmapCoordinates !== null &&
      this._heatmapCoordinates.length > 0
    ) {
      var data = [];
      for (var i = 0; i < this._heatmapCoordinates.length; i++) {
        data.push({ location: this._heatmapCoordinates[i], weight: 1 });
      }

      this._heatmap = new google.maps.visualization.HeatmapLayer({
        data: data,
        radius: 8,
        maxIntensity: 5,
        gradient: [
          "rgba(0, 255, 255, 0)",
          "rgba(0, 255, 255, 1)",
          "rgba(0, 191, 255, 1)",
          "rgba(0, 127, 255, 1)",
          "rgba(0, 63, 255, 1)",
          "rgba(0, 0, 255, 1)",
          "rgba(0, 0, 223, 1)",
          "rgba(0, 0, 191, 1)",
          "rgba(0, 0, 159, 1)",
          "rgba(0, 0, 127, 1)",
          "rgba(63, 0, 91, 1)",
          "rgba(127, 0, 63, 1)",
          "rgba(191, 0, 31, 1)",
          "rgba(255, 0, 0, 1)",
        ],
        map: null,
      });
    }
  };

/**
 * Init function for Leaflet
 */
trackdirect.models.StationCoveragePolygon.prototype._leafletInit = function () {
  if (
    this._polygonCoordinates !== null &&
    this._polygonCoordinates.length > 0
  ) {
    this._polygon = new L.polygon(this._polygonCoordinates, {
      color: "#0000FF",
      opacity: 0,
      weight: 0,
      fillColor: "#0000FF",
      fillOpacity: 0.2,
    });
  }

  if (
    this._heatmapCoordinates !== null &&
    this._heatmapCoordinates.length > 0
  ) {
    var data = [];
    for (var i = 0; i < this._heatmapCoordinates.length; i++) {
      data.push([
        this._heatmapCoordinates[i].lat,
        this._heatmapCoordinates[i].lng,
        10,
      ]);
    }
    this._heatmap = L.heatLayer(this._heatmapCoordinates, {
      minOpacity: 0.35,
      radius: 6,
      blur: 4,
    });
  }
};

/**
 * Get convex hull coordinates
 * @param {array} data
 * @param {int} maxRange
 * @return {array}
 */
trackdirect.models.StationCoveragePolygon.prototype._getConvexHullCoordinates =
  function (data, maxRange) {
    var positions = this._getFilteredPositions(data, maxRange);
    positions.push(this._center);

    var xyPositions = this._convertToXYPos(positions);
    var convexHullXYPositions = convexhull.makeHull(xyPositions);

    // Calc padding
    var latLngPadding =
      this._paddingInPercentOfMaxRange * 0.01 * maxRange * 0.000009;
    var latLngPaddingMin = this._paddingMinInMeters * 0.000009;
    if (isNaN(latLngPadding) || latLngPadding < latLngPaddingMin) {
      latLngPadding = latLngPaddingMin;
    }

    // Add padding
    var xyPositionsWithPadding = [];
    for (var i = 0; i < convexHullXYPositions.length; i++) {
      xyPositionsWithPadding.push(convexHullXYPositions[i]);

      for (var angle = 0; angle < 360; angle += 10) {
        var x =
          convexHullXYPositions[i]["x"] +
          latLngPadding * Math.cos((angle * Math.PI) / 180);
        var y =
          convexHullXYPositions[i]["y"] +
          latLngPadding * Math.sin((angle * Math.PI) / 180) * 2;
        if (!isNaN(x) && !isNaN(y)) {
          xyPositionsWithPadding.push({ x: x, y: y });
        }
      }
    }
    var convexHullXYPositionsWithPadding = convexhull.makeHull(
      xyPositionsWithPadding
    );

    // Convert to LatLng and return
    return this._convertToLatLngPos(convexHullXYPositionsWithPadding);
  };

/**
 * Get an array with valid positions
 * @param {array} data
 * @param {int} maxRange
 * @return {array}
 */
trackdirect.models.StationCoveragePolygon.prototype._getFilteredPositions =
  function (data, maxRange) {
    var result = [];

    for (var i = 0; i < data.length; i++) {
      if (typeof maxRange !== "undefined" && data[i].distance > maxRange) {
        continue;
      }

      result.push(data[i].latLngLiteral);
    }

    return result;
  };

/**
 * Calculate coverage polygon max range
 * @param {array} data
 * @param {int} percentile
 * @return {int}
 */
trackdirect.models.StationCoveragePolygon.prototype._getCoveragePolygonMaxRange =
  function (data, percentile) {
    var maxRange = this._getDistancePercentile(
      data,
      percentile,
      this._upperMaxRangeInMeters
    );
    if (isNaN(maxRange)) {
      maxRange = 0;
    }

    return maxRange;
  };

/**
 * Calculate the specified percentile
 * @param {array} data
 * @param {int} percentile
 * @param {int} upperMaxRange
 * @return {int}
 */
trackdirect.models.StationCoveragePolygon.prototype._getDistancePercentile =
  function (data, percentile, upperMaxRange) {
    var values = [];
    for (var i = 0; i < data.length; i++) {
      if (data[i].distance + 0 < upperMaxRange) {
        values.push(data[i].distance);
      }
    }

    values.sort(function (a, b) {
      return a - b;
    });

    var index = (percentile / 100) * values.length;
    var result;
    if (Math.floor(index) == index) {
      result = (values[index - 1] + values[index]) / 2;
    } else {
      result = values[Math.floor(index)];
    }

    return result;
  };

/**
 * Calculate number of values
 * @param {array} data
 * @param {int} maxRange
 * @return {int}
 */
trackdirect.models.StationCoveragePolygon.prototype._getNumberOfValues =
  function (data, maxRange) {
    var counter = 0;
    for (var i = 0; i < data.length; i++) {
      if (data[i].distance > maxRange) {
        continue;
      }

      counter++;
    }

    return counter;
  };

/**
 * Convert to xy positions
 * @param {array} data
 * @return {array}
 */
trackdirect.models.StationCoveragePolygon.prototype._convertToXYPos = function (
  positions
) {
  var result = [];
  for (var i = 0; i < positions.length; i++) {
    result.push({ x: positions[i].lat, y: positions[i].lng });
  }
  return result;
};

/**
 * Convert to lat/lng positions
 * @param {array} data
 * @return {array}
 */
trackdirect.models.StationCoveragePolygon.prototype._convertToLatLngPos =
  function (positions) {
    var result = [];
    for (var i = 0; i < positions.length; i++) {
      result.push({ lat: positions[i].x, lng: positions[i].y });
    }
    return result;
  };

/**
 * Get an array of all coordinates for the specified move type
 * @param {array} data
 * @return {array}
 */
trackdirect.models.StationCoveragePolygon.prototype._getCoordinates = function (
  data
) {
  var result = [];

  for (var j = 0; j < data.length; j++) {
    if (typeof google === "object" && typeof google.maps === "object") {
      var position = new google.maps.LatLng(
        parseFloat(data[j]["latitude"]),
        parseFloat(data[j]["longitude"])
      );
    } else {
      var position = {
        lat: parseFloat(data[j]["latitude"]),
        lng: parseFloat(data[j]["longitude"]),
      };
    }
    result.push(position);
  }

  return result;
};

/**
 * Add the angle paramter for each coverage position
 * @param {array} data
 */
trackdirect.models.StationCoveragePolygon.prototype._addParametersToData =
  function (data) {
    for (var j = 0; j < data.length; j++) {
      var latLngLiteral = {
        lat: parseFloat(data[j].latitude),
        lng: parseFloat(data[j].longitude),
      };
      data[j].latLngLiteral = latLngLiteral;
      data[j].angle = trackdirect.services.distanceCalculator.getBearing(
        this._center,
        latLngLiteral
      );
    }
  };

/**
 * Emit all event listeners for a specified event
 * @param {string} event
 * @param {object} arg
 */
trackdirect.models.StationCoveragePolygon.prototype._emitTdEventListeners =
  function (event, arg) {
    if (event in this._tdEventListeners) {
      for (var i = 0; i < this._tdEventListeners[event].length; i++) {
        this._tdEventListeners[event][i](arg);
      }
    }

    if (event in this._tdEventListenersOnce) {
      var eventListenersOnce = this._tdEventListenersOnce[event].splice(0);
      this._tdEventListenersOnce[event] = [];
      for (var i = 0; i < eventListenersOnce.length; i++) {
        eventListenersOnce[i](arg);
      }
    }
  };
