/**
 * Class trackdirect.models.TransmitPolyline inherits google.maps.Polyline
 * @see https://developers.google.com/maps/documentation/javascript/reference#Polyline
 * @param {trackdirect.models.Marker} marker
 * @param {trackdirect.models.Map} map
 */
trackdirect.models.TransmitPolyline = function (packet, map) {
  this._packet = packet;
  this._defaultMap = map;
  this._relatedMarkerIdKeys = [];

  // Call the parent constructor
  if (typeof google === "object" && typeof google.maps === "object") {
    const googlePolyline = new google.maps.Polyline(
      this._getGooglePolylineOptions()
    );

    for (const key of Object.keys(this)) {
      googlePolyline[key] = this[key];
    }
    for (const key of Object.getOwnPropertyNames(
      Object.getPrototypeOf(this)
    )) {
      if (key !== "constructor" && typeof this[key] === "function") {
        googlePolyline[key] = this[key];
      }
    }

    return googlePolyline;
  } else if (typeof L === "object") {
    L.Polyline.call(this, {}, this._getLeafletPolylineOptions());
    this.setLatLngs(this.getCoordinates());
  }
};
if (typeof google === "object" && typeof google.maps === "object") {
  trackdirect.models.TransmitPolyline.prototype = Object.create(
    google.maps.Polyline.prototype
  );
} else if (typeof L === "object") {
  trackdirect.models.TransmitPolyline.prototype = Object.create(
    L.Polyline.prototype
  );
}
trackdirect.models.TransmitPolyline.prototype.constructor =
  trackdirect.models.TransmitPolyline;

/**
 * Get latLng object by index
 */
trackdirect.models.TransmitPolyline.prototype.getPathItem = function (index) {
  if (typeof google === "object" && typeof google.maps === "object") {
    let path = google.maps.Polyline.prototype.getPath.call(this);
    return path.getAt(index);
  } else if (typeof L === "object") {
    let list = this.getLatLngs();
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
trackdirect.models.TransmitPolyline.prototype.pushPathItem = function (latLng) {
  if (typeof google === "object" && typeof google.maps === "object") {
    let path = google.maps.Polyline.prototype.getPath.call(this);
    path.push(latLng);
  } else if (typeof L === "object") {
    this.addLatLng(latLng);
  }
};

/**
 * Remove latLng object by index
 */
trackdirect.models.TransmitPolyline.prototype.removePathItem = function (
  index
) {
  if (typeof google === "object" && typeof google.maps === "object") {
    let path = google.maps.Polyline.prototype.getPath.call(this);
    path.removeAt(index);
  } else if (typeof L === "object") {
    let list = this.getLatLngs();
    if (typeof list[index] !== "undefined") {
      list.splice(index, 1);
      this.setLatLngs(list);
    }
  }
};

/**
 * Get Path length
 */
trackdirect.models.TransmitPolyline.prototype.getPathLength = function (index) {
  if (typeof google === "object" && typeof google.maps === "object") {
    let path = google.maps.Polyline.prototype.getPath.call(this);
    return path.getLength();
  } else if (typeof L === "object") {
    let list = this.getLatLngs();
    return list.length;
  }
};

/**
 * Get latLng array
 */
trackdirect.models.TransmitPolyline.prototype.getPath = function () {
  if (typeof google === "object" && typeof google.maps === "object") {
    return google.maps.Polyline.prototype.getPath.call(this);
  } else if (typeof L === "object") {
    return this.getLatLngs();
  }
  return [];
};

/**
 * Get Polyline currently active Map
 * @return {google.maps.Map}
 */
trackdirect.models.TransmitPolyline.prototype.getMap = function () {
  if (typeof google === "object" && typeof google.maps === "object") {
    let map = google.maps.Polyline.prototype.getMap.call(this);
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
 * Show Polyline on default map
 */
trackdirect.models.TransmitPolyline.prototype.show = function () {
  if (typeof google === "object" && typeof google.maps === "object") {
    if (typeof this.getMap() === "undefined" || this.getMap() === null) {
      this.setMap(this._defaultMap);
    }
  } else if (typeof L === "object") {
    if (!this._defaultMap.hasLayer(this)) {
      this.addTo(this._defaultMap);
    }
  }

  for (let i = 0; i < this._relatedMarkerIdKeys.length; i++) {
    let relatedMarkerIdKey = this._relatedMarkerIdKeys[i];
    if (
      this._defaultMap.markerCollection.isExistingMarker(relatedMarkerIdKey)
    ) {
      let relatedMarker =
        this._defaultMap.markerCollection.getMarker(relatedMarkerIdKey);
      relatedMarker.show();
      relatedMarker.showLabel();
    }
  }
};

/**
 * Hide transmit polyline
 * @param {int} delayInMilliSeconds
 */
trackdirect.models.TransmitPolyline.prototype.hide = function (
  delayInMilliSeconds
) {
  if (typeof google === "object" && typeof google.maps === "object") {
    if (this.getMap() !== null) {
      this.setMap(null);
    }
  } else if (typeof L === "object") {
    if (this._defaultMap.hasLayer(this)) {
      this._defaultMap.removeLayer(this);
    }
  }

  for (let i = 0; i < this._relatedMarkerIdKeys.length; i++) {
    let relatedMarkerIdKey = this._relatedMarkerIdKeys[i];

    if (
      this._defaultMap.markerCollection.isExistingMarker(relatedMarkerIdKey)
    ) {
      let relatedMarker =
        this._defaultMap.markerCollection.getMarker(relatedMarkerIdKey);
      if (relatedMarker !== null && relatedMarker.getMap() !== null) {
        relatedMarker.hide(delayInMilliSeconds, true);
      }
    }
  }
};

/**
 * Returns true if marker is visible
 * @return {boolean}
 */
trackdirect.models.TransmitPolyline.prototype.isVisible = function () {
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
 * Get a suitable google polyline options object
 * @return {object}
 */
trackdirect.models.TransmitPolyline.prototype._getGooglePolylineOptions =
  function () {
    let lineCoordinates = this.getCoordinates();
    if (lineCoordinates.length <= 1) {
      lineCoordinates = [];
    }

    let lineSymbol = {
      path: "M 0,-0.1 0,0",
      strokeOpacity: 0.7,
      scale: 3,
    };

    return {
      path: lineCoordinates,
      strokeOpacity: 0,
      strokeColor: "#0000ff",
      icons: [
        {
          icon: lineSymbol,
          offset: "0px",
          repeat: "5px",
        },
      ],
      map: null,
      zIndex: 100,
    };
  };

/**
 * Get a suitable leaflet polyline options object
 * @return {object}
 */
trackdirect.models.TransmitPolyline.prototype._getLeafletPolylineOptions =
  function () {
    return {
      opacity: 0.6,
      weight: 3,
      color: "#0000ff",
      dashArray: "1,5",
      lineCap: "round",
      lineJoin: "round",
    };
  };

/**
 * Returns coordinates for the transmit polyline
 * @return {array}
 */
(trackdirect.models.TransmitPolyline.prototype.getCoordinates = function () {
  // First we try to find other position by looking at station markers on map
  // This is better if the receiving stations has moved
  let lineCoordinates = this.getCoordinatesByStationMarkers();
  if (lineCoordinates.length < this._packet.station_location_path.length + 1) {
    lineCoordinates = this.getCoordinatesByPositions();
  }
  return lineCoordinates;
}),
  /**
   * Returns coordinates for the transmit polyline by looking at station markers
   * @return {array}
   */
  (trackdirect.models.TransmitPolyline.prototype.getCoordinatesByStationMarkers =
    function () {
      let lineCoordinates = [];
      let startLatLng = this._packet.getLatLngLiteral();
      lineCoordinates.push(startLatLng);

      for (let i = 0; i < this._packet.station_id_path.length; i++) {
        let stationId = this._packet.station_id_path[i];
        let stationMarkerIdKey = null;
        let stationMarker = null;
        let stationDistance = null;
        let stationLatLng = null;

        for (let pointMarkerIdKey in this._defaultMap.markerCollection.getStationMarkerIdKeys(
          stationId
        )) {
          let pointMarker =
            this._defaultMap.markerCollection.getMarker(pointMarkerIdKey);
          if (pointMarker !== null) {
            let pointLatLng = pointMarker.packet.getLatLngLiteral();
            let distance = trackdirect.services.distanceCalculator.getDistance(
              startLatLng,
              pointLatLng
            );

            if (stationMarker === null || distance < stationDistance) {
              stationMarkerIdKey = pointMarkerIdKey;
              stationMarker = pointMarker;
              stationDistance = distance;
              stationLatLng = pointLatLng;
            }
          }
        }

        if (stationLatLng !== null) {
          lineCoordinates.push(stationLatLng);
          this._relatedMarkerIdKeys.push(stationMarkerIdKey);
        }
      }
      return lineCoordinates;
    }),
  /**
   * Returns coordinates for the transmit polyline by looking at received positions
   * @return {array}
   */
  (trackdirect.models.TransmitPolyline.prototype.getCoordinatesByPositions =
    function () {
      let lineCoordinates = [];
      let startLatLng = this._packet.getLatLngLiteral();
      lineCoordinates.push(startLatLng);

      if (
        lineCoordinates.length <
        this._packet.station_location_path.length + 1
      ) {
        // If we do not have stations on map we use the lat/lng positions
        for (let i = 0; i < this._packet.station_location_path.length; i++) {
          if (
            this._packet.station_location_path[i][0] !== null &&
            this._packet.station_location_path[i][1] !== null
          ) {
            lineCoordinates.push({
              lat: parseFloat(this._packet.station_location_path[i][0]),
              lng: parseFloat(this._packet.station_location_path[i][1]),
            });
          }
        }
      }
      return lineCoordinates;
    });
