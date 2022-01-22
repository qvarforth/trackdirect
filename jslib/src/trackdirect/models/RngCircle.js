/**
 * Class trackdirect.models.RngCircle inherits google.maps.Circle
 * @see https://developers.google.com/maps/documentation/javascript/reference#Circle
 * @param {trackdirect.models.Packet} packet
 * @param {trackdirect.models.Map} map
 * @param {boolean} isHalf
 */
trackdirect.models.RngCircle = function (packet, map, isHalf) {
  this._defaultMap = map;

  // Call the parent constructor
  if (typeof google === "object" && typeof google.maps === "object") {
    google.maps.Circle.call(this, this._getGoogleCircleOptions(packet, isHalf));
  } else if (typeof L === "object") {
    var center = packet.getLatLngLiteral();
    if (L.version <= "0.7.7") {
      var range = this._getCircleRadius(packet, isHalf);
      L.Circle.call(
        this,
        [center.lat, center.lng],
        range,
        this._getLeafletCircleOptions(packet, isHalf)
      );
    } else {
      L.Circle.call(
        this,
        center,
        this._getLeafletCircleOptions(packet, isHalf)
      );
    }
  }
};
if (typeof google === "object" && typeof google.maps === "object") {
  trackdirect.models.RngCircle.prototype = Object.create(
    google.maps.Circle.prototype
  );
} else if (typeof L === "object") {
  trackdirect.models.RngCircle.prototype = Object.create(L.Circle.prototype);
}
trackdirect.models.RngCircle.prototype.constructor =
  trackdirect.models.RngCircle;

/**
 * show the circle if it is not shown
 */
trackdirect.models.RngCircle.prototype.show = function () {
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
 * hide circle if it is visible
 */
trackdirect.models.RngCircle.prototype.hide = function () {
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
 * Get default options used for initializing circle
 * @param {trackdirect.models.Packet} packet
 * @param {boolean} isHalf
 * @return {object}
 */
trackdirect.models.RngCircle.prototype._getGoogleCircleOptions = function (
  packet,
  isHalf
) {
  var color = trackdirect.services.stationColorCalculator.getColor(packet);
  var range = this._getCircleRadius(packet, isHalf);

  var options = {
    strokeColor: color,
    strokeOpacity: 0.6,
    strokeWeight: 1,
    fillColor: color,
    fillOpacity: 0.3,
    map: null,
    center: packet.getLatLngLiteral(),
    radius: range * 1000,
  };

  return options;
};

/**
 * Get default options used for initializing circle
 * @param {trackdirect.models.Packet} packet
 * @param {boolean} isHalf
 * @return {object}
 */
trackdirect.models.RngCircle.prototype._getLeafletCircleOptions = function (
  packet,
  isHalf
) {
  var color = trackdirect.services.stationColorCalculator.getColor(packet);
  var range = this._getCircleRadius(packet, isHalf);

  var options = {
    color: color,
    opacity: 0.6,
    weight: 1,
    fillColor: color,
    fillOpacity: 0.3,
    radius: range * 1000,
  };

  return options;
};

/**
 * Get circle radius based on packet
 * @param {trackdirect.models.Packet} packet
 * @param {boolean} isHalf
 * @return {float}
 */
trackdirect.models.RngCircle.prototype._getCircleRadius = function (
  packet,
  isHalf
) {
  var range = packet.getRNGRange();
  if (range === null) {
    range = 0;
  }
  if (isHalf) {
    range = range / 2;
  }

  return range;
};
