/**
 * Class trackdirect.models.Ruler
 * @param {int} defaultLength
 * @param {trackdirect.models.Map} map
 */
trackdirect.models.Ruler = function (defaultLength, map) {
  this._map = map;

  if (typeof google === "object" && typeof google.maps === "object") {
    this._googleMapsInit(defaultLength);
    this._addGoolgeMapsListeners();
  } else if (typeof L === "object") {
    this.leafletInit(defaultLength);
    this._addLeafletListeners();
  }
};

/**
 * Init ruler for Gogle Maps
 * @param {int} defaultLength
 */
trackdirect.models.Ruler.prototype._googleMapsInit = function (defaultLength) {
  this.marker1 = new google.maps.Marker({
    position: trackdirect.services.distanceCalculator.getPositionByDistance(
      this._map.getCenterLiteral(),
      270,
      defaultLength / 2
    ),
    draggable: true,
    map: this._map,
  });

  this.marker2 = new google.maps.Marker({
    position: trackdirect.services.distanceCalculator.getPositionByDistance(
      this._map.getCenterLiteral(),
      90,
      defaultLength / 2
    ),
    draggable: true,
    map: this._map,
  });

  this.marker1.markerLabel = new trackdirect.models.Label(
    {
      position: this.marker1.getPosition(),
      text: this._getDistance(this.marker1, this.marker2),
    },
    this._map
  );
  this.marker1.markerLabel.show();

  this.marker2.markerLabel = new trackdirect.models.Label(
    {
      position: this.marker2.getPosition(),
      text: this._getDistance(this.marker2, this.marker1),
    },
    this._map
  );
  this.marker2.markerLabel.show();

  this.line = new google.maps.Polyline({
    path: [this.marker1.getPosition(), this.marker2.getPosition()],
    strokeColor: "#ffff00",
    strokeOpacity: 0.7,
    strokeWeight: 6,
  });
  this.line.setMap(this._map);
};

/**
 * Init ruler for Leaflet
 * @param {int} defaultLength
 */
trackdirect.models.Ruler.prototype.leafletInit = function (defaultLength) {
  this.marker1 = new L.Marker(
    trackdirect.services.distanceCalculator.getPositionByDistance(
      this._map.getCenterLiteral(),
      270,
      defaultLength / 2
    ),
    { draggable: true }
  );
  this.marker1.addTo(this._map);

  this.marker2 = new L.Marker(
    trackdirect.services.distanceCalculator.getPositionByDistance(
      this._map.getCenterLiteral(),
      90,
      defaultLength / 2
    ),
    { draggable: true }
  );
  this.marker2.addTo(this._map);

  this.marker1.markerLabel = new trackdirect.models.Label(
    {
      position: this.marker1.getLatLng(),
      text: this._getDistance(this.marker1, this.marker2),
    },
    this._map
  );
  this.marker1.markerLabel.show();

  this.marker2.markerLabel = new trackdirect.models.Label(
    {
      position: this.marker2.getLatLng(),
      text: this._getDistance(this.marker2, this.marker1),
    },
    this._map
  );
  this.marker2.markerLabel.show();

  this.line = new L.Polyline(
    [this.marker1.getLatLng(), this.marker2.getLatLng()],
    {
      color: "#ffff00",
      opacity: 0.8,
      weight: 6,
    }
  );
  this.line.addTo(this._map);
};

/**
 * Show ruler
 */
trackdirect.models.Ruler.prototype.show = function () {
  this.marker1.markerLabel.show();
  this.marker2.markerLabel.show();

  if (typeof google === "object" && typeof google.maps === "object") {
    this.marker1.setMap(this._map);
    this.marker2.setMap(this._map);
    this.line.setMap(this._map);
  } else if (typeof L === "object") {
    this.marker1.addTo(this._map);
    this.marker2.addTo(this._map);
    this.line.addTo(this._map);
  }
};

/**
 * Hide ruler
 */
trackdirect.models.Ruler.prototype.hide = function () {
  this.marker1.markerLabel.hide();
  this.marker2.markerLabel.hide();

  if (typeof google === "object" && typeof google.maps === "object") {
    this.marker1.setMap(null);
    this.marker2.setMap(null);
    this.line.setMap(null);
  } else if (typeof L === "object") {
    this._map.removeLayer(this.marker1);
    this._map.removeLayer(this.marker2);
    this._map.removeLayer(this.line);
  }
};

/**
 * Add listerners
 */
trackdirect.models.Ruler.prototype._addGoolgeMapsListeners = function () {
  var me = this;
  google.maps.event.addListener(this.marker1, "drag", function () {
    me.line.setPath([me.marker1.getPosition(), me.marker2.getPosition()]);
    me._updateLabels();
  });
  google.maps.event.addListener(this.marker2, "drag", function () {
    me.line.setPath([me.marker1.getPosition(), me.marker2.getPosition()]);
    me._updateLabels();
  });
};

/**
 * Add listerners
 */
trackdirect.models.Ruler.prototype._addLeafletListeners = function () {
  var me = this;
  this.marker1.on("drag", function (e) {
    me.line.setLatLngs([me.marker1.getLatLng(), me.marker2.getLatLng()]);
    me._updateLabels();
  });
  this.marker2.on("drag", function (e) {
    me.line.setLatLngs([me.marker1.getLatLng(), me.marker2.getLatLng()]);
    me._updateLabels();
  });
};

/**
 * Update labels with new text and new position
 */
trackdirect.models.Ruler.prototype._updateLabels = function () {
  this.marker1.markerLabel.hide();
  this.marker2.markerLabel.hide();

  if (typeof google === "object" && typeof google.maps === "object") {
    this.marker1.markerLabel = new trackdirect.models.Label(
      {
        position: this.marker1.getPosition(),
        text: this._getDistance(this.marker1, this.marker2),
      },
      this._map
    );
    this.marker2.markerLabel = new trackdirect.models.Label(
      {
        position: this.marker2.getPosition(),
        text: this._getDistance(this.marker2, this.marker1),
      },
      this._map
    );
  } else if (typeof L === "object") {
    this.marker1.markerLabel = new trackdirect.models.Label(
      {
        position: this.marker1.getLatLng(),
        text: this._getDistance(this.marker1, this.marker2),
      },
      this._map
    );
    this.marker2.markerLabel = new trackdirect.models.Label(
      {
        position: this.marker2.getLatLng(),
        text: this._getDistance(this.marker2, this.marker1),
      },
      this._map
    );
  }

  this.marker1.markerLabel.show();
  this.marker2.markerLabel.show();
};

/**
 * Get distance string for ruler
 * @param {Marker} marker1
 * @param {Marker} marker2
 * @return {string}
 */
trackdirect.models.Ruler.prototype._getDistance = function (marker1, marker2) {
  var p1 = this._getPositionLiteral(marker1);
  var p2 = this._getPositionLiteral(marker2);
  var distance = Math.round(
    trackdirect.services.distanceCalculator.getDistance(p1, p2),
    0
  );
  if (distance > 99999) {
    if (this._map.state.useImperialUnit) {
      distance =
        Math.round(
          trackdirect.services.imperialConverter.convertKilometerToMile(
            distance / 1000
          )
        ).toString() + " miles";
    } else {
      distance = Math.round(distance / 1000).toString() + " km";
    }
  } else if (distance > 999) {
    if (this._map.state.useImperialUnit) {
      distance =
        (
          Math.round(
            trackdirect.services.imperialConverter.convertKilometerToMile(
              distance / 1000
            ) * 10
          ) / 10
        ).toString() + " miles";
    } else {
      distance = (Math.round(distance / 100) / 10).toString() + " km";
    }
  } else {
    distance = distance.toString() + " m";
  }
  var bearing = Math.round(
    trackdirect.services.distanceCalculator.getBearing(p2, p1),
    0
  ).toString();
  return bearing + "&ordm; " + distance;
};

/**
 * Get position literal
 * @param {Marker} marker
 * @return LatLngLiteral
 */
trackdirect.models.Ruler.prototype._getPositionLiteral = function (marker) {
  if (typeof google === "object" && typeof google.maps === "object") {
    var latLng = marker.getPosition();
    if (typeof latLng !== "undefined" && typeof latLng.lat === "function") {
      return { lat: latLng.lat(), lng: latLng.lng() };
    } else {
      return latLng;
    }
  } else if (typeof L === "object") {
    var latLng = marker.getLatLng();
    if (typeof latLng !== "undefined") {
      return { lat: latLng.lat, lng: latLng.lng };
    } else {
      return latLng;
    }
  }
  return null;
};
