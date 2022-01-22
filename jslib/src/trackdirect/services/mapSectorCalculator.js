trackdirect.services.MapSectorCalculator = {
  /**
   * Get all visible map sectors
   * @param {LatLngBounds} bounds
   * @return {array}
   */
  getMapSectors: function (bounds) {
    var result = [];
    // We include some border map sectors so that markers appear before user enter those map-sectors (if they are loaded from server)
    if (typeof google === "object" && typeof google.maps === "object") {
      var maxLat = Math.ceil(bounds.getNorthEast().lat()) + 1;
      var minLat = Math.floor(bounds.getSouthWest().lat()) - 1;
      var maxLng = Math.ceil(bounds.getNorthEast().lng()) + 1;
      var minLng = Math.floor(bounds.getSouthWest().lng()) - 1;
    } else if (typeof L === "object") {
      var maxLat = Math.ceil(bounds.getNorthEast().lat) + 1;
      var minLat = Math.floor(bounds.getSouthWest().lat) - 1;
      var maxLng = Math.ceil(bounds.getNorthEast().lng) + 1;
      var minLng = Math.floor(bounds.getSouthWest().lng) - 1;
    }

    if (maxLng < minLng) {
      result = result.concat(
        trackdirect.services.MapSectorCalculator.getMapSectorsByInterval(
          minLat,
          maxLat,
          minLng,
          180.0
        )
      );
      minLng = -180.0;
    }

    result = result.concat(
      trackdirect.services.MapSectorCalculator.getMapSectorsByInterval(
        minLat,
        maxLat,
        minLng,
        maxLng
      )
    );

    // Add the world wide area code
    // This seems to result in very bad performance... so we skip it
    //result.push(99999999);
    return result;
  },

  /**
   * Get all visible map sectors
   * @param {float} minLat
   * @param {float} maxLat
   * @param {float} minLng
   * @param {float} maxLng
   * @return {array}
   */
  getMapSectorsByInterval: function (minLat, maxLat, minLng, maxLng) {
    var result = [];

    var minAreaCode = this.getMapSector(minLat, minLng);
    var maxAreaCode = this.getMapSector(maxLat, maxLng);

    lngDiff = parseInt(Math.ceil(maxLng)) - parseInt(Math.ceil(minLng));

    var areaCode = minAreaCode;
    while (areaCode <= maxAreaCode) {
      if (areaCode % 10 == 5) {
        result.push(areaCode);
      } else {
        result.push(areaCode);
        result.push(areaCode + 5);
      }

      for (var i = 1; i <= lngDiff; i++) {
        if (areaCode % 10 == 5) {
          result.push(areaCode + 10 * i - 5);
          result.push(areaCode + 10 * i);
        } else {
          result.push(areaCode + 10 * i);
          result.push(areaCode + 10 * i + 5);
        }
      }

      // Lat takes 0.2 jumps
      areaCode = areaCode + 20000;
    }
    return result;
  },

  /**
   * Get map sector based on latitude and longitude
   * @param {float} latitude
   * @param {float} longitude
   */
  getMapSector: function (latitude, longitude) {
    var lat = this._getMapSectorLatRepresentation(latitude);
    var lng = this._getMapSectorLngRepresentation(longitude);

    // lat interval: 0 - 18000000
    // lng interval: 0 - 00003600
    return lat + lng;
  },

  /**
   * Get map sector latitude part
   * @param {float} latitude
   * @return int
   */
  _getMapSectorLatRepresentation: function (latitude) {
    var lat = parseInt(Math.floor(latitude)) + 90; // Positive representation of lat;
    var latDecimalPart = latitude - Math.floor(latitude);

    if (latDecimalPart < 0.2) {
      lat = lat * 10 + 0;
    } else if (latDecimalPart < 0.4) {
      lat = lat * 10 + 2;
    } else if (latDecimalPart < 0.6) {
      lat = lat * 10 + 4;
    } else if (latDecimalPart < 0.8) {
      lat = lat * 10 + 6;
    } else {
      lat = lat * 10 + 8;
    }
    lat = lat * 10000;

    // lat interval: 0 - 18000000
    return lat;
  },

  /**
   * Get map sector longitude part
   * @param {float} longitude
   * @return int
   */
  _getMapSectorLngRepresentation: function (longitude) {
    lng = parseInt(Math.floor(longitude)) + 180; // Positive representation of lng;
    lngDecimalPart = longitude - Math.floor(longitude);

    if (lngDecimalPart < 0.5) {
      lng = lng * 10 + 0;
    } else {
      lng = lng * 10 + 5;
    }

    // lng interval: 0 - 00003600
    return lng;
  },
};
