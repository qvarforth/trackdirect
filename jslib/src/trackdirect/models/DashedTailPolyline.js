/**
 * Class trackdirect.models.DashedTailPolyline
 * @see https://developers.google.com/maps/documentation/javascript/reference#Polyline
 * @param {string} color
 * @param {trackdirect.models.Map} map
 */
trackdirect.models.DashedTailPolyline = function (color, map) {
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
  trackdirect.models.DashedTailPolyline.prototype = Object.create(
    google.maps.Polyline.prototype
  );
} else if (typeof L === "object") {
  trackdirect.models.DashedTailPolyline.prototype = Object.create(
    L.Polyline.prototype
  );
}
trackdirect.models.DashedTailPolyline.prototype.constructor =
  trackdirect.models.DashedTailPolyline;

/**
 * Get latLng object by index
 */
trackdirect.models.DashedTailPolyline.prototype.getPathItem = function (index) {
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
trackdirect.models.DashedTailPolyline.prototype.pushPathItem = function (
  latLng
) {
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
trackdirect.models.DashedTailPolyline.prototype.removePathItem = function (
  index
) {
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
trackdirect.models.DashedTailPolyline.prototype.getPathLength = function (
  index
) {
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
trackdirect.models.DashedTailPolyline.prototype.getPath = function () {
  if (typeof google === "object" && typeof google.maps === "object") {
    return google.maps.Polyline.prototype.getPath.call(this).getArray();
  } else if (typeof L === "object") {
    return this.getLatLngs();
  }
  return [];
};

/**
 * Get Polyline currently active Map
 * @return {google.maps.Map}
 */
trackdirect.models.DashedTailPolyline.prototype.getMap = function () {
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
trackdirect.models.DashedTailPolyline.prototype.setMarkerIdKey = function (
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
trackdirect.models.DashedTailPolyline.prototype.setRelatedMarkerIdKey =
  function (markerIdKey) {
    this.relatedMarkerIdKey = markerIdKey;
  };

/**
 * Show polyline on default map
 */
trackdirect.models.DashedTailPolyline.prototype.show = function () {
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
 * Hide polyline
 */
trackdirect.models.DashedTailPolyline.prototype.hide = function () {
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
 * Add packet to polyline
 * @param {trackdirect.models.Packet} packet
 */
trackdirect.models.DashedTailPolyline.prototype.addPacket = function (packet) {
  if (typeof google === "object" && typeof google.maps === "object") {
    var latLng = new google.maps.LatLng(
      parseFloat(packet.latitude),
      parseFloat(packet.longitude)
    );
    this.pushPathItem(latLng);
  } else if (typeof L === "object") {
    var latLng = new L.latLng(
      parseFloat(packet.latitude),
      parseFloat(packet.longitude)
    );
    this.addLatLng(latLng);
  }
};

/**
 * Add infowindow listener
 * @param {int} markerIdKey
 */
trackdirect.models.DashedTailPolyline.prototype._addInfoWindowListener =
  function (markerIdKey) {
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
trackdirect.models.DashedTailPolyline.prototype._getGooglePolylineOptions =
  function (color) {
    var lineSymbol = {
      path: "M 0,-1 0,1",
      strokeOpacity: 0.4,
      scale: 3,
    };

    var options = {
      geodesic: false,
      strokeOpacity: 0,
      strokeColor: color,
      icons: [
        {
          icon: lineSymbol,
          offset: "20px",
          repeat: "15px",
        },
      ],
      map: null,
      zIndex: 100,
    };

    return options;
  };

/**
 * Get a suitable leaflet polyline options object
 * @param {string} color
 * @return {object}
 */
trackdirect.models.DashedTailPolyline.prototype._getLeafletPolylineOptions =
  function (color) {
    return {
      opacity: 0.6,
      weight: 3,
      dashArray: "6,8",
      lineJoin: "round",
      color: color,
    };
  };
