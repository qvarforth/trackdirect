/**
 * Class trackdirect.models.PhgCircle
 * @see https://developers.google.com/maps/documentation/javascript/reference#Circle
 * @param {trackdirect.models.Packet} packet
 * @param {trackdirect.models.Map} map
 * @param {boolean} isHalf
 */
trackdirect.models.PhgCircle = function (packet, map, isHalf) {
  this._defaultMap = map;

  if (typeof google === "object" && typeof google.maps === "object") {
    const googleCircle = new google.maps.Circle(
      this._getGoogleCircleOptions(packet, isHalf)
    );

    for (const key of Object.keys(this)) {
      googleCircle[key] = this[key];
    }
    for (const key of Object.getOwnPropertyNames(
      Object.getPrototypeOf(this)
    )) {
      if (key !== "constructor" && typeof this[key] === "function") {
        googleCircle[key] = this[key];
      }
    }

    return googleCircle;
  } else if (typeof L === "object") {
    if (L.version <= "0.7.7") {
      let range = this._getCircleRadius(packet, isHalf);
      let center = this._getCircleCenter(packet, isHalf);
      L.Circle.call(
        this,
        [center.lat, center.lng],
        range,
        this._getLeafletCircleOptions(packet, isHalf)
      );
    } else {
      L.Circle.call(
        this,
        this._getCircleCenter(packet, isHalf),
        this._getLeafletCircleOptions(packet, isHalf)
      );
    }
  }
};
if (typeof google === "object" && typeof google.maps === "object") {
  trackdirect.models.PhgCircle.prototype = Object.create(
    google.maps.Circle.prototype
  );
} else if (typeof L === "object") {
  trackdirect.models.PhgCircle.prototype = Object.create(L.Circle.prototype);
}
trackdirect.models.PhgCircle.prototype.constructor =
  trackdirect.models.PhgCircle;

/**
 * show the circle if it is not shown
 */
trackdirect.models.PhgCircle.prototype.show = function () {
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
trackdirect.models.PhgCircle.prototype.hide = function () {
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
trackdirect.models.PhgCircle.prototype._getGoogleCircleOptions = function (
  packet,
  isHalf
) {
  let color = trackdirect.services.stationColorCalculator.getColor(packet);
  let range = this._getCircleRadius(packet, isHalf);
  let center = this._getCircleCenter(packet, isHalf);

  let options = {
    strokeColor: color,
    strokeOpacity: 0.6,
    strokeWeight: 1,
    fillColor: color,
    fillOpacity: 0.3,
    map: null,
    center: center,
    radius: range,
  };

  return options;
};

/**
 * Get default options used for initializing circle
 * @param {trackdirect.models.Packet} packet
 * @param {boolean} isHalf
 * @return {object}
 */
trackdirect.models.PhgCircle.prototype._getLeafletCircleOptions = function (
  packet,
  isHalf
) {
  let color = trackdirect.services.stationColorCalculator.getColor(packet);
  let range = this._getCircleRadius(packet, isHalf);
  let options = {
    color: color,
    opacity: 0.6,
    weight: 1,
    fillColor: color,
    fillOpacity: 0.3,
    radius: range,
  };

  return options;
};

/**
 * Get circle radius based on packet
 * @param {trackdirect.models.Packet} packet
 * @param {boolean} isHalf
 * @return {float}
 */
trackdirect.models.PhgCircle.prototype._getCircleRadius = function (
  packet,
  isHalf
) {
  let range = packet.getPHGRange();
  if (range === null) {
    range = 0;
  }
  if (isHalf) {
    range = range / 2;
  }
  return range;
};

/**
 * Get circle center based on packet
 * @param {trackdirect.models.Packet} packet
 * @param {boolean} isHalf
 * @return {object}
 */
trackdirect.models.PhgCircle.prototype._getCircleCenter = function (
  packet,
  isHalf
) {
  let direction = packet.getPhgDirectionDegree();
  let center = packet.getLatLngLiteral();
  if (direction != null) {
    let range = packet.getPHGRange();
    if (range === null) {
      range = 0;
    }

    if (isHalf) {
      range = range / 2;
    }

    let distance = (range * 2) / 3 / 2;
    center = trackdirect.services.distanceCalculator.getPositionByDistance(
      center,
      direction,
      distance
    );
  }

  return center;
};
