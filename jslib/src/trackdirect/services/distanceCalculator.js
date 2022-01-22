trackdirect.services.distanceCalculator = {
  /**
   * Get distance in meters between to positions
   * @param {LatLngLiteral} p1
   * @param {LatLngLiteral} p2
   * @return {float}
   */
  getDistance: function (p1, p2) {
    var R = 6378137; // Earth’s mean radius in meter
    var dLat = this._radians(p2.lat - p1.lat);
    var dLong = this._radians(p2.lng - p1.lng);
    var a =
      Math.sin(dLat / 2) * Math.sin(dLat / 2) +
      Math.cos(this._radians(p1.lat)) *
        Math.cos(this._radians(p2.lat)) *
        Math.sin(dLong / 2) *
        Math.sin(dLong / 2);
    var c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
    var d = R * c;
    if (isNaN(d)) {
      return null;
    } else {
      return d; // returns the distance in meter
    }
  },

  /**
   * Get center of specified coordinates
   * @param {array} coords
   * @return {LatLngLiteral}
   */
  getCenter: function (coords) {
    var x = coords.map(function (a) {
      return a.lat;
    });
    var y = coords.map(function (a) {
      return a.lng;
    });
    var minX = Math.min.apply(null, x);
    var maxX = Math.max.apply(null, x);
    var minY = Math.min.apply(null, y);
    var maxY = Math.max.apply(null, y);
    return { lat: (minX + maxX) / 2, lng: (minY + maxY) / 2 };
  },

  /**
   * Get position by course and distance
   * @param {LatLngLiteral} latLng
   * @param {int} course
   * @param {int} distanceInMeters
   * @return {LatLngLiteral}
   */
  getPositionByDistance: function (latLng, course, distanceInMeters) {
    var dist = distanceInMeters / 1000; // Convert to km
    dist = dist / 6371; // Divide by Earth radius
    var brng = (course * Math.PI) / 180; // Convert to Rad

    var lat1 = (latLng.lat * Math.PI) / 180,
      lon1 = (latLng.lng * Math.PI) / 180;

    var lat2 = Math.asin(
      Math.sin(lat1) * Math.cos(dist) +
        Math.cos(lat1) * Math.sin(dist) * Math.cos(brng)
    );

    var lon2 =
      lon1 +
      Math.atan2(
        Math.sin(brng) * Math.sin(dist) * Math.cos(lat1),
        Math.cos(dist) - Math.sin(lat1) * Math.sin(lat2)
      );

    if (isNaN(lat2) || isNaN(lon2)) return null;

    // Convert to deg and return
    var latitude = (lat2 * 180) / Math.PI;
    var longitude = (lon2 * 180) / Math.PI;
    return {
      lat: Math.round(latitude * 100000) / 100000,
      lng: Math.round(longitude * 100000) / 100000,
    };
  },

  /**
   * Get bearing between two points
   * @param {object} p1
   * @param {object} p2
   * @return {float}
   */
  getBearing: function (p1, p2) {
    startLat = this._radians(p1.lat);
    startLong = this._radians(p1.lng);
    endLat = this._radians(p2.lat);
    endLong = this._radians(p2.lng);

    var dLong = endLong - startLong;
    var dPhi = Math.log(
      Math.tan(endLat / 2.0 + Math.PI / 4.0) /
        Math.tan(startLat / 2.0 + Math.PI / 4.0)
    );

    //var dLong = Math.sin(endLong - startLong) * Math.cos(endLat);
    //var dPhi = Math.cos(startLat)*Math.sin(endLat) - Math.sin(startLat)*Math.cos(endLat)*Math.cos(endLong-startLong);

    if (Math.abs(dLong) > Math.PI) {
      if (dLong > 0.0) {
        dLong = -(2.0 * Math.PI - dLong);
      } else {
        dLong = 2.0 * Math.PI + dLong;
      }
    }

    return (this._degrees(Math.atan2(dLong, dPhi)) + 360.0) % 360.0;
  },

  /**
   * Convert degrees to radians
   * @param {float} n
   * @return {float}
   */
  _radians: function (n) {
    return n * (Math.PI / 180);
  },

  /**
   * Convert radians to degrees
   * @param {float} n
   * @return {float}
   */
  _degrees: function (n) {
    return n * (180 / Math.PI);
  },
};
