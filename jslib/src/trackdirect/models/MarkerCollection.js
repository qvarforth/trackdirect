/**
 * Class trackdirect.models.MarkerCollection
 */
trackdirect.models.MarkerCollection = function () {
  // Contains markerKeys and is indexed by markerId
  this._markerKeys = {};

  // Array of all markers
  this._markers = [];

  // Contains markerKeys indexed by stationId
  this._stationMarkers = {};

  // Contains markerIdKey indexed by stationId
  this._stationLastMovingMarkerIdKey = {};

  // Contains markerIdKey indexed by stationId
  this._stationLastMarker = {};

  // Contains markerIdKey indexed by senderId
  this._senderLastMarker = {};

  // Contains markerKeys indexed by latitude:longitude
  this._positionMarkersIdKeys = {};

  // Array of all marker dot markers, using the same index as in the array _markers
  this._dotMarkers = [];

  // Array of all marker polylines, using the same index as in the array _markers
  this._markerPolyLines = [];

  //Array of all marker dashed polylines, using the same index as in the array _markers
  this._markerOriginDashedPolyLines = [];

  // Contains arrays of markerKeys and is indexed by mapSectorId
  this._mapSectorMarkerIdKeys = {};

  // Contains coverage values indexed by stationId
  this._stationCoverage = {};

  this.resetAllMarkers();
};

/**
 * Returns markerIdKey based on specified markerId
 * @param {int} markerId
 * @return {int} markerIdKey
 */
trackdirect.models.MarkerCollection.prototype.getMarkerIdKey = function (
  markerId
) {
  if (!(markerId in this._markerKeys)) {
    this._markers.push(null);
    this._markerPolyLines.push(null);
    this._dotMarkers.push(null);
    this._markerOriginDashedPolyLines.push(null);

    var markerIdKey = this._markers.length - 1;
    this._markerKeys[markerId] = markerIdKey;

    return markerIdKey;
  } else {
    return this._markerKeys[markerId];
  }
};

/**
 * Returns true if marker exists
 * @param {int} markerIdKey
 * @return {boolean}
 */
trackdirect.models.MarkerCollection.prototype.isExistingMarker = function (
  markerIdKey
) {
  if (markerIdKey in this._markers && this._markers[markerIdKey] !== null) {
    return true;
  }
  return false;
};

/**
 * Set marker for specified markerIdKey
 * @param {int} markerIdKey
 * @param {trackdirect.models.Marker} marker
 */
trackdirect.models.MarkerCollection.prototype.setMarker = function (
  markerIdKey,
  marker
) {
  if (marker !== null && typeof marker.packet !== "undefined") {
    var packet = marker.packet;

    this._markers[markerIdKey] = marker;
    this._addStationMarkerId(markerIdKey, packet);
    this._addStationLastMarker(packet, marker);
    this.addPostionMarkerId(markerIdKey, packet);
  }
};

/**
 * Returns the marker that has the specified markerIdKey
 * @param {int} markerIdKey
 * @return {object}
 */
trackdirect.models.MarkerCollection.prototype.getMarker = function (
  markerIdKey
) {
  if (markerIdKey !== null && markerIdKey in this._markers) {
    return this._markers[markerIdKey];
  }
  return null;
};

/**
 * Returns all markers
 * @return {array}
 */
trackdirect.models.MarkerCollection.prototype.getAllMarkers = function () {
  return this._markers;
};

/**
 * Remove marker with specified markerIdKey
 * @param {int} markerIdKey
 */
trackdirect.models.MarkerCollection.prototype.removeMarker = function (
  markerIdKey
) {
  if (markerIdKey !== null && markerIdKey in this._markers) {
    this._markers.splice(markerIdKey, 1);
  }
};

/**
 * Returns the number of markers
 * @return {int}
 */
trackdirect.models.MarkerCollection.prototype.getNumberOfMarkers = function () {
  return this._markers.length;
};

/*
 * Set marker label for specified markerIdKey
 * @param {int} markerIdKey
 * @param {object} label
 */
trackdirect.models.MarkerCollection.prototype.setMarkerLabel = function (
  markerIdKey,
  label
) {
  if (markerIdKey in this._markers && this._markers[markerIdKey] !== null) {
    this._markers[markerIdKey].label = label;
  }
};

/**
 * Returns the marker label that has the specified markerIdKey
 * @param {int} markerIdKey
 * @return {object}
 */
trackdirect.models.MarkerCollection.prototype.getMarkerLabel = function (
  markerIdKey
) {
  if (markerIdKey in this._markers && this._markers[markerIdKey] !== null) {
    return this._markers[markerIdKey].label;
  }
  return null;
};

/**
 * Returns true if specified marker has a label
 * @param {int} markerIdKey
 * @return {boolean}
 */
trackdirect.models.MarkerCollection.prototype.hasMarkerLabel = function (
  markerIdKey
) {
  if (
    markerIdKey in this._markers &&
    this._markers[markerIdKey] !== null &&
    this._markers[markerIdKey].label !== null
  ) {
    return true;
  }
  return false;
};

/**
 * Set a new position for the marker label
 * @param {int} markerIdKey
 * @param {object} position
 */
trackdirect.models.MarkerCollection.prototype.setMarkerLabelPosition =
  function (markerIdKey, position) {
    if (
      markerIdKey in this._markers &&
      this._markers[markerIdKey] !== null &&
      this._markers[markerIdKey].label !== null
    ) {
      this._markers[markerIdKey].label.position = position;
    }
  };

/**
 * Returns true if packet is a duplicate,
 * this method should be used on realtime-packet since they will not be checked on server
 * @param {int} markerIdKey
 */
trackdirect.models.MarkerCollection.prototype.isDuplicate = function (packet) {
  if (packet.is_moving == 0) {
    // We don't care for duplicates for stationary stations
    return false;
  }

  for (var markerIdKey in this.getPositionMarkerIdKeys(
    packet.latitude,
    packet.longitude
  )) {
    var marker = this.getMarker(markerIdKey);
    if (
      marker !== null &&
      marker.packet.station_id == packet.station_id &&
      marker.packet.symbol == packet.symbol &&
      marker.packet.symbol_table == packet.symbol_table &&
      marker.packet.course == packet.course
    ) {
      // My guess is that this is a duplicate
      return true;
    }
  }
  return false;
};

/*
 * Add dot marker for specified markerIdKey
 * @param {int} markerIdKey
 * @param {object} dotMarker
 */
trackdirect.models.MarkerCollection.prototype.addDotMarker = function (
  markerIdKey,
  dotMarker
) {
  if (markerIdKey in this._dotMarkers) {
    if (this._dotMarkers[markerIdKey] === null) {
      this._dotMarkers[markerIdKey] = [];
    }
    this._dotMarkers[markerIdKey].push(dotMarker);
  }
};

/**
 * Returns the marker dot markers
 * @param {int} markerIdKey
 * @return {array}
 */
trackdirect.models.MarkerCollection.prototype.getDotMarkers = function (
  markerIdKey
) {
  if (
    markerIdKey in this._dotMarkers &&
    this._dotMarkers[markerIdKey] !== null
  ) {
    return this._dotMarkers[markerIdKey];
  }
  return [];
};

/**
 * Returns true if specified marker has dot markers
 * @param {int} markerIdKey
 * @return {boolean}
 */
trackdirect.models.MarkerCollection.prototype.hasDotMarkers = function (
  markerIdKey
) {
  if (
    markerIdKey in this._dotMarkers &&
    this._dotMarkers[markerIdKey] !== null &&
    this._dotMarkers[markerIdKey].length > 0
  ) {
    return true;
  }
  return false;
};

/*
 * Add dot marker for specified markerIdKey
 * @param {int} markerIdKey
 * @param {object} dotMarker
 */
trackdirect.models.MarkerCollection.prototype.addStationCoverage = function (
  stationId,
  stationCoveragePolygon
) {
  this._stationCoverage[stationId] = stationCoveragePolygon;
};

/**
 * Returns the station coverage
 * @param {int} stationId
 * @return {StationCoveragePolygon}
 */
trackdirect.models.MarkerCollection.prototype.getStationCoverage = function (
  stationId
) {
  if (
    stationId in this._stationCoverage &&
    this._stationCoverage[stationId] !== null
  ) {
    return this._stationCoverage[stationId];
  }
  return null;
};

/**
 * Returns an array of stations the has a visible coverage
 * @return {array}
 */
trackdirect.models.MarkerCollection.prototype.getStationIdListWithVisibleCoverage =
  function () {
    var result = [];
    for (var stationId in this._stationCoverage) {
      if (this._stationCoverage[stationId].isRequestedToBeVisible()) {
        result.push(stationId);
      }
    }
    return result;
  };

/**
 * Returns true if specified station has a coverage polygon
 * @param {int} stationId
 * @return {boolean}
 */
trackdirect.models.MarkerCollection.prototype.hasCoveragePolygon = function (
  stationId
) {
  if (
    stationId in this._stationCoverage &&
    this._stationCoverage[stationId] !== null
  ) {
    return true;
  }
  return false;
};

/**
 * Reset the dot markers for a specified marker
 * @param {int} markerIdKey
 */
trackdirect.models.MarkerCollection.prototype.resetDotMarkers = function (
  markerIdKey
) {
  if (
    markerIdKey in this._dotMarkers &&
    this._dotMarkers[markerIdKey] !== null
  ) {
    this._dotMarkers[markerIdKey] = [];
  }
};

/**
 * Remove the oldest dot markers for a specified marker
 * @param {int} markerIdKey
 * @return {boolean}
 */
trackdirect.models.MarkerCollection.prototype.removeOldestDotMarker = function (
  markerIdKey
) {
  if (this.hasDotMarkers(markerIdKey)) {
    latestMarker = this.getMarker(markerIdKey);
    var latestMarkerIndex = this.getDotMarkerIndex(markerIdKey, latestMarker);
    var dotMarkers = this.getDotMarkers(markerIdKey);
    var maxNumberOfPolyLinePoints = dotMarkers.length;
    if (latestMarkerIndex > -1) {
      // Seems like the latest marker also is a dotmarker, this may happen if it is a moving object
      maxNumberOfPolyLinePoints = maxNumberOfPolyLinePoints - 1;
    }

    var removedItems = this._dotMarkers[markerIdKey].splice(0, 1);
    if (removedItems.length == 1) {
      var removedMarker = removedItems[0];
      removedMarker.hide();
      if (this.hasPolyline(removedMarker.markerIdKey)) {
        var polyline = this.getMarkerPolyline(removedMarker.markerIdKey);
        while (polyline.getPathLength() > maxNumberOfPolyLinePoints) {
          polyline.removePathItem(0);
        }
      }
      removedMarker = null;

      return true;
    }
  }
  return false;
};

/**
 * Get dot marker index
 * @param {int} markerIdKey
 * @param {trackdirect.models.Marker} marker
 * @return int
 */
trackdirect.models.MarkerCollection.prototype.getDotMarkerIndex = function (
  markerIdKey,
  marker
) {
  if (!this.hasDotMarkers(markerIdKey)) {
    return -1;
  }
  for (var i = 0, len = this._dotMarkers[markerIdKey].length; i < len; i++) {
    var foundMarker = this._dotMarkers[markerIdKey][i];
    if (foundMarker === null) {
      continue;
    }

    if (
      typeof marker.packet.id !== "undefined" &&
      marker.packet.id !== null &&
      foundMarker.packet.id === marker.packet.id &&
      foundMarker.packet.map_id === marker.packet.map_id
    ) {
      return i;
    }

    if (
      foundMarker.packet.station_id === marker.packet.station_id &&
      foundMarker.packet.timestamp === marker.packet.timestamp &&
      Math.round(foundMarker.packet.latitude * 100000) ===
        Math.round(marker.packet.latitude * 100000) &&
      Math.round(foundMarker.packet.longitude * 100000) ===
        Math.round(marker.packet.longitude * 100000) &&
      foundMarker.packet.map_id === marker.packet.map_id
    ) {
      return i;
    }
  }
  return -1;
};

/*
 * Add marker polyline for specified markerIdKey
 * @param {int} markerIdKey
 * @param {object} polyline
 */
trackdirect.models.MarkerCollection.prototype.setMarkerPolyline = function (
  markerIdKey,
  polyline
) {
  if (markerIdKey in this._markerPolyLines) {
    this._markerPolyLines[markerIdKey] = polyline;
  }
};

/**
 * Returns the marker polyline
 * @param {int} markerIdKey
 * @return {array}
 */
trackdirect.models.MarkerCollection.prototype.getMarkerPolyline = function (
  markerIdKey
) {
  if (this.hasPolyline(markerIdKey)) {
    return this._markerPolyLines[markerIdKey];
  }
  return null;
};

/**
 * Returns true if specified marker has a polyline
 * @param {int} markerIdKey
 * @return {boolean}
 */
trackdirect.models.MarkerCollection.prototype.hasPolyline = function (
  markerIdKey
) {
  if (
    markerIdKey in this._markerPolyLines &&
    this._markerPolyLines[markerIdKey] !== null
  ) {
    if (this._markerPolyLines[markerIdKey].getPathLength() > 1) {
      return true;
    } else {
      // We only consider polyline to exists if it has a path length of 2 or more
      this._markerPolyLines[markerIdKey].hide();
      this._markerPolyLines[markerIdKey] = null;
      return false;
    }
  }
  return false;
};

/**
 * Reset the marker polyline
 * @param {int} markerIdKey
 */
trackdirect.models.MarkerCollection.prototype.resetMarkerPolyline = function (
  markerIdKey
) {
  if (markerIdKey in this._markerPolyLines) {
    this._markerPolyLines[markerIdKey] = null;
  }
};

/*
 * Add marker dashed polyline for specified markerIdKey
 * @param {int} markerIdKey
 * @param {object} polyline
 */
trackdirect.models.MarkerCollection.prototype.setMarkerDashedPolyline =
  function (markerIdKey, polyline) {
    if (markerIdKey in this._markerOriginDashedPolyLines) {
      this._markerOriginDashedPolyLines[markerIdKey] = polyline;
    }
  };

/**
 * Returns the marker dashed polyline
 * @param {int} markerIdKey
 * @return {array}
 */
trackdirect.models.MarkerCollection.prototype.getMarkerDashedPolyline =
  function (markerIdKey) {
    if (this.hasDashedPolyline(markerIdKey)) {
      return this._markerOriginDashedPolyLines[markerIdKey];
    }
    return null;
  };

/**
 * Returns true if specified marker has a dashed polyline
 * @param {int} markerIdKey
 * @return {boolean}
 */
trackdirect.models.MarkerCollection.prototype.hasDashedPolyline = function (
  markerIdKey
) {
  if (
    markerIdKey in this._markerOriginDashedPolyLines &&
    this._markerOriginDashedPolyLines[markerIdKey] !== null
  ) {
    if (this._markerOriginDashedPolyLines[markerIdKey].getPathLength() > 1) {
      return true;
    } else {
      // We only consider polyline to exists if it has a path length of 2 or more
      this._markerOriginDashedPolyLines[markerIdKey].hide();
      this._markerOriginDashedPolyLines[markerIdKey] = null;
      return false;
    }
  }
  return false;
};

/**
 * Reset the marker dashed polyline
 * @param {int} markerIdKey
 */
trackdirect.models.MarkerCollection.prototype.resetMarkerDashedPolyline =
  function (markerIdKey) {
    if (markerIdKey in this._markerOriginDashedPolyLines) {
      this._markerOriginDashedPolyLines[markerIdKey] = null;
    }
  };

/**
 * returnes the latest packet of the specified station
 * @param {int} stationId
 * @return {object}
 */
trackdirect.models.MarkerCollection.prototype.getStationLatestPacket =
  function (stationId) {
    if (
      typeof this._stationLastMarker[stationId] !== "undefined" &&
      this._stationLastMarker[stationId] !== null &&
      typeof this._stationLastMarker[stationId].packet !== "undefined"
    ) {
      return this._stationLastMarker[stationId].packet;
    } else {
      return null;
    }
  };

/**
 * returnes the latest marker of the specified station
 * @param {int} stationId
 * @return {object}
 */
trackdirect.models.MarkerCollection.prototype.getStationLatestMarker =
  function (stationId) {
    if (
      typeof this._stationLastMarker[stationId] !== "undefined" &&
      this._stationLastMarker[stationId] !== null
    ) {
      return this._stationLastMarker[stationId];
    } else {
      return null;
    }
  };

/**
 * returnes the latest packet of the specified sender
 * @param {int} senderId
 * @return {object}
 */
trackdirect.models.MarkerCollection.prototype.getSenderLatestPacket = function (
  senderId
) {
  if (
    typeof this._senderLastMarker[senderId] !== "undefined" &&
    this._senderLastMarker[senderId] !== null &&
    typeof this._senderLastMarker[senderId].packet !== "undefined"
  ) {
    return this._senderLastMarker[senderId].packet;
  } else {
    return null;
  }
};

/**
 * Returns the latest moving marker for station with specified id
 * @param {int} stationId
 * @return {int}
 */
trackdirect.models.MarkerCollection.prototype.getStationLatestMovingMarkerIdKey =
  function (stationId) {
    if (
      this._stationLastMovingMarkerIdKey !== null &&
      typeof this._stationLastMovingMarkerIdKey[stationId] !== "undefined" &&
      this._stationLastMovingMarkerIdKey[stationId] !== null &&
      this.isExistingMarker(this._stationLastMovingMarkerIdKey[stationId])
    ) {
      return this._stationLastMovingMarkerIdKey[stationId];
    }
    return null;
  };

/**
 * Get the latest markerIdKey connected to specified markerIdKey
 * @param {int} markerIdKey
 * @return int
 */
trackdirect.models.MarkerCollection.prototype.getMarkerMasterMarkerKeyId =
  function (markerIdKey) {
    if (this.isExistingMarker(markerIdKey)) {
      var marker = this._markers[markerIdKey];
      if (this.hasRelatedDashedPolyline(marker)) {
        return this.getMarkerMasterMarkerKeyId(
          marker._relatedMarkerOriginDashedPolyLine.ownerMarkerIdKey
        );
      }
    }
    return markerIdKey;
  };

/**
 * Get latest visible marker for a stationId
 * @param {int} stationId
 * @return {object}
 */
trackdirect.models.MarkerCollection.prototype.getStationLatestVisibleMarker =
  function (stationId) {
    var latestVisibleMarker = null;
    var latestVisibleMarkerTimestamp = null;
    for (var markerIdKey in this._stationMarkers[stationId]) {
      var marker = this._markers[markerIdKey];
      if (
        typeof marker !== "undefined" &&
        marker !== null &&
        typeof marker.getMap() !== "undefined" &&
        marker.getMap() !== null
      ) {
        if (
          latestVisibleMarkerTimestamp === null ||
          marker.packet.timestamp > latestVisibleMarkerTimestamp
        ) {
          latestVisibleMarker = marker;
          latestVisibleMarkerTimestamp = marker.packet.timestamp;
        }
      }
    }
    return latestVisibleMarker;
  };

/**
 * Get an object with all station markerKeyIds as keys
 * @param {int} stationId
 * @return {object}
 */
trackdirect.models.MarkerCollection.prototype.getStationMarkerIdKeys =
  function (stationId) {
    if (stationId in this._stationMarkers) {
      return this._stationMarkers[stationId];
    }
    return {};
  };

/**
 * Get  an object with all markerKeyIds at a specified position as keys
 * @param {number} latitude
 * @param {number} longitude
 * @return {object}
 */
trackdirect.models.MarkerCollection.prototype.getPositionMarkerIdKeys =
  function (latitude, longitude) {
    var key = this._getCompareablePosition(latitude, longitude);
    if (key in this._positionMarkersIdKeys) {
      return this._positionMarkersIdKeys[key];
    }
    return {};
  };

/**
 * Add marker to postition
 * @param {int} markerIdKey
 * @param {trackdirect.models.Packet} packet
 */
trackdirect.models.MarkerCollection.prototype.addPostionMarkerId = function (
  markerIdKey,
  packet
) {
  var key = this._getCompareablePosition(packet.latitude, packet.longitude);
  if (!(key in this._positionMarkersIdKeys)) {
    this._positionMarkersIdKeys[key] = {};
  }
  this._positionMarkersIdKeys[key][markerIdKey] = true;
};

/**
 * Remove marker from postition
 * @param {number} latitude
 * @param {number} longitude
 * @param {int} markerIdKey
 */
trackdirect.models.MarkerCollection.prototype.removePostionMarkerId = function (
  latitude,
  longitude,
  markerIdKey
) {
  var key = this._getCompareablePosition(latitude, longitude);
  if (key in this._positionMarkersIdKeys) {
    if (markerIdKey in this._positionMarkersIdKeys[key]) {
      this._positionMarkersIdKeys[key][markerIdKey] = false;
    }
  }
};

/**
 * Add marker specified map sector
 * @param {int} markerIdKey
 * @param {int} markerMapSector
 */
trackdirect.models.MarkerCollection.prototype.addMarkerToMapSector = function (
  markerIdKey,
  markerMapSector
) {
  if (!(markerMapSector in this._mapSectorMarkerIdKeys)) {
    this._mapSectorMarkerIdKeys[markerMapSector] = [];
  }

  if (this._mapSectorMarkerIdKeys[markerMapSector].indexOf(markerIdKey) < 0) {
    // only add markerIdKey to map-sector if it is not allready there
    this._mapSectorMarkerIdKeys[markerMapSector].push(markerIdKey);
  }
};

/**
 * Add marker specified map sector
 * @param {int} markerIdKey
 * @param {int} markerMapSector
 */
trackdirect.models.MarkerCollection.prototype.getMapSectorMarkerKeys =
  function (mapSector) {
    if (mapSector in this._mapSectorMarkerIdKeys) {
      return this._mapSectorMarkerIdKeys[mapSector];
    }
    return [];
  };

/**
 * Reset all markers, this will remove everything from memory
 */
trackdirect.models.MarkerCollection.prototype.resetAllMarkers = function () {
  this._markerKeys = {};
  this._markers = [];
  this._markerPolyLines = [];
  this._dotMarkers = [];
  this._markerOriginDashedPolyLines = [];
  this._stationMarkers = {};
  this._stationLastMovingMarkerIdKey = {};
  this._stationLastMarker = {};
  this._senderLastMarker = {};
  this._positionMarkersIdKeys = {};
  this._mapSectorMarkerIdKeys = {};
  this._stationCoverage = {};
};

/**
 * Remove marker from memory
 * @param {int} markerIdKey
 */
trackdirect.models.MarkerCollection.prototype.resetMarker = function (
  markerIdKey
) {
  if (this.isExistingMarker(markerIdKey)) {
    var marker = this._markers[markerIdKey];

    this._markers[markerIdKey] = null;
    this._markerPolyLines[markerIdKey] = null;
    this._dotMarkers[markerIdKey] = null;
    this._markerOriginDashedPolyLines[markerIdKey] = null;

    if (
      typeof marker.packet.latitude != "undefined" &&
      typeof marker.packet.longitude != "undefined"
    ) {
      this.removePostionMarkerId(
        marker.packet.latitude,
        marker.packet.longitude,
        markerIdKey
      );
    }
  }
};

/**
 * Returns true if marker has a related marker origin dashed polyline.
 * A related dashed poly line is a dashed polyline ending at this marker.
 * @param {trackdirect.models.Marker} marker
 * @return {boolean}
 */
trackdirect.models.MarkerCollection.prototype.hasRelatedDashedPolyline =
  function (marker) {
    if (
      typeof marker._relatedMarkerOriginDashedPolyLine !== "undefined" &&
      marker._relatedMarkerOriginDashedPolyLine !== null
    ) {
      return true;
    }
    return false;
  };

/**
 * Returns true if this station has a marker id not equal to this that is moving
 * @param {trackdirect.models.Packet} packet
 * @return {boolean}
 */
trackdirect.models.MarkerCollection.prototype.hasNonRelatedMovingMarkerId =
  function (packet) {
    // If latest marker is related we will have no non related that is visible,
    // since we only allow one moving marker per station.
    // So we only need to compare latest moving marker...
    var latestStationMovingMarkerIdKey = this.getStationLatestMovingMarkerIdKey(
      packet.station_id
    );
    var newMarkerIdKey = this.getMarkerIdKey(packet.marker_id);
    if (
      latestStationMovingMarkerIdKey !== null &&
      latestStationMovingMarkerIdKey !== newMarkerIdKey
    ) {
      var latestStationMovingMarker = this.getMarker(
        latestStationMovingMarkerIdKey
      );
      if (latestStationMovingMarker.packet.hasConfirmedMapId()) {
        return true;
      }
    }
    return false;
  };

/**
 * Returns true if new packet should replace current marker
 * @param {trackdirect.models.Packet} packet
 * @return {boolean}
 */
trackdirect.models.MarkerCollection.prototype.isPacketReplacingMarker =
  function (packet) {
    var markerIdKey = this.getMarkerIdKey(packet.marker_id);
    if (this.isExistingMarker(markerIdKey)) {
      var marker = this.getMarker(markerIdKey);
      if (marker !== null) {
        if (packet.map_id == 14) {
          // Packets that kill other packets should allways replace previous packet
          return true;
        }

        if (packet.is_moving == 0) {
          // Stationary allways replace previous marker if they have the same marker_id
          return true;
        }

        if ([1, 2, 7, 12].indexOf(packet.map_id) < 0) {
          // For ghost packets we allways replace markers with the same marker_id
          return true;
        }
      }
    }
    return false;
  };

/**
 * Add markerId to station
 * @param {int} markerIdKey
 * @param {trackdirect.models.Packet} packet
 */
trackdirect.models.MarkerCollection.prototype._addStationMarkerId = function (
  markerIdKey,
  packet
) {
  if (!(packet.station_id in this._stationMarkers)) {
    this._stationMarkers[packet.station_id] = {};
  }
  this._stationMarkers[packet.station_id][markerIdKey] = true;

  if (packet.is_moving == 1 && packet.hasConfirmedMapId()) {
    this._stationLastMovingMarkerIdKey[packet.station_id] = markerIdKey;
  }
};

/**
 * Add station latest marker
 * @param {trackdirect.models.Packet} packet
 * @param {trackdirect.models.Marker} marker
 */
trackdirect.models.MarkerCollection.prototype._addStationLastMarker = function (
  packet,
  marker
) {
  if (packet.hasConfirmedMapId()) {
    if (
      typeof this._stationLastMarker[packet.station_id] === "undefined" ||
      this._stationLastMarker[packet.station_id] === null
    ) {
      this._stationLastMarker[packet.station_id] = marker;
      if (packet.station_name == packet.sender_name) {
        this._senderLastMarker[packet.sender_id] = marker;
      }
    } else if (
      this._stationLastMarker[packet.station_id].packet.timestamp <=
      packet.timestamp
    ) {
      this._stationLastMarker[packet.station_id] = marker;
      if (packet.station_name == packet.sender_name) {
        this._senderLastMarker[packet.sender_id] = marker;
      }
    }
  }
};

/**
 * Get string representation of a position that may be used for comparison
 * @param {number} latitude
 * @param {number} longitude
 * @return {string}
 */
trackdirect.models.MarkerCollection.prototype._getCompareablePosition =
  function (latitude, longitude) {
    var latCmp = Math.round(latitude * 100000);
    var lngCmp = Math.round(longitude * 100000);
    return String(latCmp) + ":" + String(lngCmp);
  };
