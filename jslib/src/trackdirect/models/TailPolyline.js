/**
 * Class trackdirect.models.TailPolyline
 * @see https://developers.google.com/maps/documentation/javascript/reference#Polyline
 * @param {string} color
 * @param {trackdirect.models.Map} map
 */
trackdirect.models.TailPolyline = function (color, map) {
  this._defaultMap = map;
  this.markerIdKey = null;
  this.ownerMarkerIdKey = null;
  this.relatedMarkerIdKey = null;

  // Call the parent constructor
  if (typeof google === "object" && typeof google.maps === "object") {
    google.maps.Polyline.call(this, this._getGooglePolylineOptions(color));
  } else if (typeof L === "object") {
    L.Polyline.call(this, {}, this._getLeafletPolylineOptions(color));
  }
};
if (typeof google === "object" && typeof google.maps === "object") {
  trackdirect.models.TailPolyline.prototype = Object.create(
    google.maps.Polyline.prototype
  );
} else if (typeof L === "object") {
  trackdirect.models.TailPolyline.prototype = Object.create(
    L.Polyline.prototype
  );
}
trackdirect.models.TailPolyline.prototype.constructor =
  trackdirect.models.TailPolyline;

/**
 * Get latLng object by index
 */
trackdirect.models.TailPolyline.prototype.getPathItem = function (index) {
  if (typeof google === "object" && typeof google.maps === "object") {
    var path = google.maps.Polyline.prototype.getPath.call(this);
    return path.getAt(index);
  } else if (typeof L === "object") {
    var list = this.getLatLngs();
    if (typeof list[index] !== "undefined") {
      return list[index];
    } else {
      return null;
    }
  }
  return null;
};

/**
 * Push latLng object to path
 */
trackdirect.models.TailPolyline.prototype.pushPathItem = function (latLng) {
  if (typeof google === "object" && typeof google.maps === "object") {
    var path = google.maps.Polyline.prototype.getPath.call(this);
    path.push(latLng);
  } else if (typeof L === "object") {
    this.addLatLng(latLng);
  }
};

/**
 * Remove latLng object by index
 */
trackdirect.models.TailPolyline.prototype.removePathItem = function (index) {
  if (typeof google === "object" && typeof google.maps === "object") {
    var path = google.maps.Polyline.prototype.getPath.call(this);
    path.removeAt(index);
  } else if (typeof L === "object") {
    var list = this.getLatLngs();
    if (typeof list[index] !== "undefined") {
      list.splice(index, 1);
      this.setLatLngs(list);
    }
  }
};

/**
 * Get Path length
 */
trackdirect.models.TailPolyline.prototype.getPathLength = function (index) {
  if (typeof google === "object" && typeof google.maps === "object") {
    var path = google.maps.Polyline.prototype.getPath.call(this);
    return path.getLength();
  } else if (typeof L === "object") {
    var list = this.getLatLngs();
    return list.length;
  }
};

/**
 * Get latLng array
 */
trackdirect.models.TailPolyline.prototype.getPath = function () {
  if (typeof google === "object" && typeof google.maps === "object") {
    return google.maps.Polyline.prototype.getPath.call(this);
  } else if (typeof L === "object") {
    return this.getLatLngs();
  }
  return [];
};

/**
 * get polyline currently active Map
 * @return {google.maps.Map}
 */
trackdirect.models.TailPolyline.prototype.getMap = function () {
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
 * Set markerIdKey
 * @param {int} markerIdKey
 */
trackdirect.models.TailPolyline.prototype.setMarkerIdKey = function (
  markerIdKey
) {
  // Two names for the same thing...
  this.markerIdKey = markerIdKey;
  this.ownerMarkerIdKey = markerIdKey;
  this._addInfoWindowListener(markerIdKey);
};

/**
 * Set related markerIdKey
 * @param {int} markerIdKey
 */
trackdirect.models.TailPolyline.prototype.setRelatedMarkerIdKey = function (
  markerIdKey
) {
  this.relatedMarkerIdKey = markerIdKey;
};

/**
 * Show polylne on default map
 */
trackdirect.models.TailPolyline.prototype.show = function () {
  if (typeof google === "object" && typeof google.maps === "object") {
    if (typeof this.getMap() === "undefined" || this.getMap() === null) {
      this.setMap(this._defaultMap);
    }
  } else if (typeof L === "object") {
    if (!this._defaultMap.hasLayer(this)) {
      this.addTo(this._defaultMap);
    }
  }
};

/**
 * Hide polylne transmit polyline
 */
trackdirect.models.TailPolyline.prototype.hide = function () {
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
 * Add marker to polyline
 * @param {trackdirect.models.Marker} marker
 */
trackdirect.models.TailPolyline.prototype.addMarker = function (marker) {
  if (typeof google === "object" && typeof google.maps === "object") {
    var latLng = new google.maps.LatLng(
      parseFloat(marker.packet.latitude),
      parseFloat(marker.packet.longitude)
    );
    latLng.marker = marker;
    this.pushPathItem(latLng);
  } else if (typeof L === "object") {
    var latLng = new L.latLng(
      parseFloat(marker.packet.latitude),
      parseFloat(marker.packet.longitude)
    );
    latLng.marker = marker;
    this.addLatLng(latLng);
  }
};

/**
 * Add infowindow listener
 * @param {int} markerIdKey
 */
trackdirect.models.TailPolyline.prototype._addInfoWindowListener = function (
  markerIdKey
) {
  var me = this;
  if (typeof google === "object" && typeof google.maps === "object") {
    google.maps.event.addListener(this, "click", function (event) {
      var marker = me._defaultMap.markerCollection.getMarker(markerIdKey);
      me._defaultMap.openPolylineInfoWindow(marker, event.latLng);
    });
  } else if (typeof L === "object") {
    this.on("click", function (event) {
      var marker = me._defaultMap.markerCollection.getMarker(markerIdKey);
      me._defaultMap.openPolylineInfoWindow(marker, event.latlng);
    });
  }
};

/**
 * Get a suitable google polyline options object
 * @param {string} color
 * @return {object}
 */
trackdirect.models.TailPolyline.prototype._getGooglePolylineOptions = function (
  color
) {
  return {
    geodesic: false,
    strokeOpacity: 0.6,
    strokeWeight: 4,
    strokeColor: color,
    map: null,
    zIndex: 100,
  };
};

/**
 * Get a suitable leaflet polyline options object
 * @param {string} color
 * @return {object}
 */
trackdirect.models.TailPolyline.prototype._getLeafletPolylineOptions =
  function (color) {
    return {
      opacity: 0.7,
      weight: 4,
      color: color,
    };
  };
