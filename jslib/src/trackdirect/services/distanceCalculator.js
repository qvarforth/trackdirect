trackdirect.services.distanceCalculator = {
  /**
   * Get distance in meters between to positions
   * @param {LatLngLiteral} p1
   * @param {LatLngLiteral} p2
   * @return {float}
   */
  getDistance: function (p1, p2) {
    let R = 6378137; // Earth’s mean radius in meter
    let dLat = this._radians(p2.lat - p1.lat);
    let dLong = this._radians(p2.lng - p1.lng);
    let a =
      Math.sin(dLat / 2) * Math.sin(dLat / 2) +
      Math.cos(this._radians(p1.lat)) *
      Math.cos(this._radians(p2.lat)) *
      Math.sin(dLong / 2) *
      Math.sin(dLong / 2);
    let c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
    let d = R * c;
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
    let x = coords.map(function (a) {
      return a.lat;
    });
    let y = coords.map(function (a) {
      return a.lng;
    });
    let minX = Math.min.apply(null, x);
    let maxX = Math.max.apply(null, x);
    let minY = Math.min.apply(null, y);
    let maxY = Math.max.apply(null, y);
    return {lat: (minX + maxX) / 2, lng: (minY + maxY) / 2};
  },

  /**
   * Get position by course and distance
   * @param {LatLngLiteral} latLng
   * @param {int} course
   * @param {int} distanceInMeters
   * @return {LatLngLiteral}
   */
  getPositionByDistance: function (latLng, course, distanceInMeters) {
    let dist = distanceInMeters / 1000; // Convert to km
    dist = dist / 6371; // Divide by Earth radius
    let brng = (course * Math.PI) / 180; // Convert to Rad

    let lat1 = (latLng.lat * Math.PI) / 180,
      lon1 = (latLng.lng * Math.PI) / 180;

    let lat2 = Math.asin(
      Math.sin(lat1) * Math.cos(dist) +
      Math.cos(lat1) * Math.sin(dist) * Math.cos(brng)
    );

    let lon2 =
      lon1 +
      Math.atan2(
        Math.sin(brng) * Math.sin(dist) * Math.cos(lat1),
        Math.cos(dist) - Math.sin(lat1) * Math.sin(lat2)
      );

    if (isNaN(lat2) || isNaN(lon2)) return null;

    // Convert to deg and return
    let latitude = (lat2 * 180) / Math.PI;
    let longitude = (lon2 * 180) / Math.PI;
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

    let dLong = endLong - startLong;
    let dPhi = Math.log(
      Math.tan(endLat / 2.0 + Math.PI / 4.0) /
      Math.tan(startLat / 2.0 + Math.PI / 4.0)
    );

    //let dLong = Math.sin(endLong - startLong) * Math.cos(endLat);
    //let dPhi = Math.cos(startLat)*Math.sin(endLat) - Math.sin(startLat)*Math.cos(endLat)*Math.cos(endLong-startLong);

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
