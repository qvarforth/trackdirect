/**
 * Class trackdirect.models.HeatMap
 * @see https://developers.google.com/maps/documentation/javascript/reference#ImageMapType
 * @param {trackdirect.models.Map} map
 */
trackdirect.models.HeatMap = function (map) {
  this._defaultMap = map;

  // Call the parent constructor
  if (typeof google === "object" && typeof google.maps === "object") {
    google.maps.ImageMapType.call(this, this._getGoogleMapOptions());
  } else if (typeof L === "object") {
    L.TileLayer.call(this, this._getUrlTemplate(), this._getLeafletOptions());
  }
};
if (typeof google === "object" && typeof google.maps === "object") {
  trackdirect.models.HeatMap.prototype = Object.create(
    google.maps.ImageMapType.prototype
  );
} else if (typeof L === "object") {
  trackdirect.models.HeatMap.prototype = Object.create(L.TileLayer.prototype);
}
trackdirect.models.HeatMap.prototype.constructor = trackdirect.models.HeatMap;

/**
 * Get a suitable leaflet heatmap options object
 * @return {object}
 */
trackdirect.models.HeatMap.prototype._getLeafletOptions = function () {
  var options = {
    errorTileUrl: trackdirect.settings.baseUrl + "/heatmaps/transparent.png",
    tileSize: 256,
    maxZoom: 9,
    minZoom: 0,
  };
  return options;
};

/**
 * Get a suitable google heatmap options object
 * @return {object}
 */
trackdirect.models.HeatMap.prototype._getGoogleMapOptions = function () {
  var me = this;
  var options = {
    getTileUrl: function (coord, zoom) {
      if (zoom > trackdirect.settings.minZoomForMarkers - 1) {
        // It should be possible to return null here, but chrome tries to fetch www.website.com/null
        return trackdirect.settings.baseUrl + "/heatmaps/transparent.png";
      }

      var normalizedCoord = me._getNormalizedCoord(coord, zoom);
      if (!normalizedCoord) {
        // It should be possible to return null here, but chrome tries to fetch www.website.com/null
        return trackdirect.settings.baseUrl + "/heatmaps/transparent.png";
      }

      var xString = String(normalizedCoord.x);
      var yString = String(normalizedCoord.y);

      return me
        ._getUrlTemplate()
        .replace("{z}", zoom)
        .replace("{y}", yString)
        .replace("{x}", xString);
    },
    tileSize: new google.maps.Size(256, 256),
    maxZoom: 9,
    minZoom: 0,
    radius: 1738000,
    name: "APRSHEAT",
  };
  return options;
};

/**
 * Get tile url
 * @return {object}
 */
trackdirect.models.HeatMap.prototype._getUrlTemplate = function () {
  return (
    trackdirect.settings.baseUrl +
    "/heatmaps/latest-heatmap.{z}.{y}.{x}.png?version=" +
    this._getHeatMapVersion()
  );
};

/**
 * Returns the heat map version
 * (This method is just used to force update of heatmap at least once every day)
 * @return String
 */
trackdirect.models.HeatMap.prototype._getHeatMapVersion = function () {
  var today = new Date();
  var dd = today.getDate();
  var mm = today.getMonth() + 1; //January is 0!
  var yyyy = today.getFullYear();
  var hh = today.getHours();

  if (dd < 10) {
    dd = "0" + dd;
  }

  if (mm < 10) {
    mm = "0" + mm;
  }

  return yyyy + "-" + mm + "-" + dd + "-" + hh;
};

/**
 * get normalized coords
 * Normalizes the coords that tiles repeat across the x axis (horizontally)
 * like the standard Google map tiles.
 * @param {object} coord
 * @param {int} zoom
 * @return {object}
 */
trackdirect.models.HeatMap.prototype._getNormalizedCoord = function (
  coord,
  zoom
) {
  var y = coord.y;
  var x = coord.x;

  // tile range in one direction range is dependent on zoom level
  // 0 = 1 tile, 1 = 2 tiles, 2 = 4 tiles, 3 = 8 tiles, etc
  var tileRange = 1 << zoom;

  // don't repeat across y-axis (vertically)
  if (y < 0 || y >= tileRange) {
    return null;
  }

  // repeat across x-axis
  if (x < 0 || x >= tileRange) {
    x = ((x % tileRange) + tileRange) % tileRange;
  }

  return { x: x, y: y };
};
