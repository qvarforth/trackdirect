/**
 * Class trackdirect.models.Map
 * @see https://developers.google.com/maps/documentation/javascript/reference#Map
 * @param {string} mapElementId
 * @param {object} options
 */
trackdirect.models.Map = function (mapElementId, options) {
  this._init(mapElementId, options);

  // Call the parent constructor
  if (typeof google === "object" && typeof google.maps === "object") {
    google.maps.Map.call(
      this,
      document.getElementById(mapElementId),
      this._getGoolgeMapOptions()
    );
  } else if (typeof L === "object") {
    L.Map.call(
      this,
      document.getElementById(mapElementId),
      this._getLeafletMapOptions()
    );
    this._updateLeafletTileLayer();
    L.control
      .zoom({
        position: "bottomright",
      })
      .addTo(this);
  }

  this._initMap();
};
if (typeof google === "object" && typeof google.maps === "object") {
  trackdirect.models.Map.prototype = Object.create(google.maps.Map.prototype);
} else if (typeof L === "object") {
  trackdirect.models.Map.prototype = Object.create(L.Map.prototype);
}
trackdirect.models.Map.prototype.constructor = trackdirect.models.Map;

/**
 * Init
 */
trackdirect.models.Map.prototype._init = function (mapElementId, options) {
  this._mapElementId = mapElementId;
  this._tdMapOptions = options;
  this._initBasic();
  this._initMapTypes();
};

/**
 * Init basic stuff
 */
trackdirect.models.Map.prototype._initBasic = function () {
  this._tdEventListeners = {};
  this._tdEventTimeout = null;
  this._currentContentZoom = null;
  this._visibleMapSectors = [];
  this._newMarkersToShow = [];

  this._leafletTileLayer = null;
  this._heatMap = null;

  // Init public variables
  this.markerCollection = new trackdirect.models.MarkerCollection();
  this.state = new trackdirect.models.MapState();
};

/**
 * Init map types
 */
trackdirect.models.Map.prototype._initMapTypes = function () {
  this._supportedMapTypes = {};
  if (
    typeof this._tdMapOptions.supportedMapTypes !== "undefined" &&
    this._tdMapOptions.supportedMapTypes !== null &&
    Object.keys(this._tdMapOptions.supportedMapTypes).length > 0
  ) {
    this._supportedMapTypes = this._tdMapOptions.supportedMapTypes;
  } else if (typeof google === "object" && typeof google.maps === "object") {
    this._supportedMapTypes["roadmap"] = google.maps.MapTypeId.ROADMAP;
    this._supportedMapTypes["terrain"] = google.maps.MapTypeId.TERRAIN;
    this._supportedMapTypes["satellite"] = google.maps.MapTypeId.SATELLITE;
    this._supportedMapTypes["hybrid"] = google.maps.MapTypeId.HYBRID;
  } else if (typeof L === "object") {
    this._supportedMapTypes["roadmap"] = "OpenStreetMap.Mapnik";
    this._supportedMapTypes["terrain"] = "OpenTopoMap";
  }

  if (
    typeof this._tdMapOptions.maptype !== "undefined" &&
    this._tdMapOptions.maptype !== null &&
    this._tdMapOptions.maptype in this._supportedMapTypes
  ) {
    this._mapType = this._tdMapOptions.maptype;
  } else {
    this._mapType = Object.keys(this._supportedMapTypes)[0];
  }
};

/**
 * Init the map
 */
trackdirect.models.Map.prototype._initMap = function () {
  this._heatMap = new trackdirect.models.HeatMap(this);
  this._setMapInitialLocation();
  this._initOms();
  this._initInfoWindowEvent();
  this._updateMapContent();
  this._initMapEvents();

  // create kmlLayer object from URL
  if (typeof google === "object" && typeof google.maps === "object") {
    if (typeof this._tdMapOptions.mid !== "undefined") {
      var kmlUrl =
        "https://www.google.com/maps/d/u/0/kml?mid=" + this._tdMapOptions.mid;
      var kmlLayer = new google.maps.KmlLayer(kmlUrl, { map: this });
    }
  }
};

/**
 * Trigger a resize event
 */
trackdirect.models.Map.prototype.triggerResize = function () {
  if (typeof google === "object" && typeof google.maps === "object") {
    google.maps.event.trigger(this, "resize");
  } else if (typeof L === "object") {
    L.Map.prototype._onResize.call(this);
  }
};

/**
 * Set Map center
 * @param {LatLngLiteral} pos
 * @param {int} zoom
 */
trackdirect.models.Map.prototype.setCenter = function (pos, zoom) {
  if (typeof google === "object" && typeof google.maps === "object") {
    google.maps.Map.prototype.setCenter.call(this, pos);
    if (typeof zoom !== "undefined") {
      google.maps.Map.prototype.setZoom.call(this, zoom);
    }
  } else if (typeof L === "object") {
    zoom = typeof zoom !== "undefined" ? zoom : this.getZoom();
    L.Map.prototype.setView.call(this, pos, zoom);
  }
  this._renderCordinatesContainer(pos);
};

/**
 * Get Map center literal
 * @return LatLngLiteral
 */
trackdirect.models.Map.prototype.getCenterLiteral = function () {
  if (typeof google === "object" && typeof google.maps === "object") {
    var latLng = google.maps.Map.prototype.getCenter.call(this);
    if (typeof latLng !== "undefined" && typeof latLng.lat === "function") {
      return { lat: latLng.lat(), lng: latLng.lng() };
    } else {
      return latLng;
    }
  } else if (typeof L === "object") {
    var latLng = L.Map.prototype.getCenter.call(this);
    if (typeof latLng !== "undefined") {
      return { lat: latLng.lat, lng: latLng.lng };
    } else {
      return latLng;
    }
  }
  return null;
};

/**
 * Fit bounds
 * @param {Array} bounds
 */
trackdirect.models.Map.prototype.fitBounds = function (bounds) {
  if (typeof google === "object" && typeof google.maps === "object") {
    var latLngBounds = new google.maps.LatLngBounds();
    for (var i = 0; i < bounds.length; i++) {
      latLngBounds.extend(bounds[i]);
    }
    google.maps.Map.prototype.fitBounds.call(this, latLngBounds);
  } else if (typeof L === "object") {
    L.Map.prototype.fitBounds.call(this, bounds);
  }
};

/**
 * set Map center by station position
 * @param {LatLngLiteral} pos
 */
trackdirect.models.Map.prototype.setCenterByStationId = function (stationId) {
  var latestVisibleMarker =
    this.markerCollection.getStationLatestVisibleMarker(stationId);
  if (latestVisibleMarker !== null) {
    this.setCenter(latestVisibleMarker.packet.getLatLngLiteral());
  }
};

/**
 * Get map DOM element id
 * @return {string}
 */
trackdirect.models.Map.prototype.getMapElementId = function () {
  return this._mapElementId;
};

/**
 * Get map options
 * @return {object}
 */
trackdirect.models.Map.prototype.getTdMapOptions = function () {
  return this._tdMapOptions;
};

/**
 * Returns true if specified map sector is visible
 * If we are filtering we consider all mapsectors visible
 * @param {int} mapSector
 * @return {boolean}
 */
trackdirect.models.Map.prototype.isMapSectorVisible = function (mapSector) {
  if (
    this._visibleMapSectors.indexOf(mapSector) >= 0 ||
    this.state.isFilterMode
  ) {
    return true;
  }
  return false;
};

/**
 * Returnes the number of new markers in queue
 * @return {int}
 */
trackdirect.models.Map.prototype.getNumberOfNewMarkersToShow = function () {
  return this._newMarkersToShow;
};

/**
 * Show all markers that has recently been added
 * @param {boolean} track
 */
trackdirect.models.Map.prototype.showNewMarkersInQueue = function (track) {
  track = typeof track !== "undefined" ? track : true;

  var oldestAllowedTrackingTimestamp = 0;
  if (this.state.onlyTrackRecentPackets) {
    oldestAllowedTrackingTimestamp = Math.floor(Date.now() / 1000) - 60;
  }

  while ((markerIdKey = this._newMarkersToShow.pop()) != null) {
    if (!this.markerCollection.isExistingMarker(markerIdKey)) {
      continue;
    }
    var marker = this.markerCollection.getMarker(markerIdKey);
    trackdirect.services.callbackExecutor.addWithPriority(
      marker,
      marker.showCompleteMarker,
      []
    );

    // Track
    if (track && marker.packet.packet_order_id == 1) {
      if (
        marker.shouldMarkerBeVisible() &&
        marker.showAsMarker &&
        this.state.trackStationId !== null &&
        this.state.trackStationId == marker.packet.station_id &&
        this.state.getClientTimestamp(marker.packet.timestamp) >
          oldestAllowedTrackingTimestamp
      ) {
        trackdirect.services.callbackExecutor.addWithPriority(
          this,
          this.setCenterByStationId,
          [marker.packet.station_id]
        );
      }
    }

    // Open previoulsy open info window
    if (
      this.state.openInfoWindowForMarkerIdKey !== null &&
      this.state.openInfoWindowForMarkerIdKey == markerIdKey &&
      marker.packet.packet_order_id == 1 &&
      marker.shouldMarkerBeVisible() &&
      marker.showAsMarker
    ) {
      trackdirect.services.callbackExecutor.addWithPriority(
        this,
        this.openLatestStationInfoWindow,
        [marker.packet.station_id]
      );
    }
  }
  this.state.openInfoWindowForMarkerIdKey = null;
};

/**
 * Activate filtered mode
 */
trackdirect.models.Map.prototype.activateFilteredMode = function () {
  this.state.isFilterMode = true;
  this._deactivateHeatMap();
  this._updateMapContent();
};

/**
 * Deactivate filtered mode
 */
trackdirect.models.Map.prototype.deactivateFilteredMode = function () {
  if (this.state.isFilterMode) {
    this._activateHeatMap();
    this.state.isFilterMode = false;
    this.state.filterStationIds = [];
    this._updateMapContent();
  }
};

/**
 * Get the north east latitude of the current map view
 * @return {float}
 */
trackdirect.models.Map.prototype.getNorthEastLat = function () {
  if (this.getBounds() != null) {
    if (typeof google === "object" && typeof google.maps === "object") {
      return this.getBounds().getNorthEast().lat();
    } else if (typeof L === "object") {
      return this.getBounds().getNorthEast().lat;
    }
  }
  return 0;
};

/**
 * Get the north east longtitue of the current map view
 * @return {float}
 */
trackdirect.models.Map.prototype.getNorthEastLng = function () {
  if (this.getBounds() != null) {
    if (typeof google === "object" && typeof google.maps === "object") {
      return this.getBounds().getNorthEast().lng();
    } else if (typeof L === "object") {
      return this.getBounds().getNorthEast().lng;
    }
  }
  return 0;
};

/**
 * Get the south west latitude of the current map view
 * @return {float}
 */
trackdirect.models.Map.prototype.getSouthWestLat = function () {
  if (this.getBounds() != null) {
    if (typeof google === "object" && typeof google.maps === "object") {
      return this.getBounds().getSouthWest().lat();
    } else if (typeof L === "object") {
      return this.getBounds().getSouthWest().lat;
    }
  }
  return 0;
};

/**
 * Get the south west longitude of the current map view
 * @return {float}
 */
trackdirect.models.Map.prototype.getSouthWestLng = function () {
  if (this.getBounds() != null) {
    if (typeof google === "object" && typeof google.maps === "object") {
      return this.getBounds().getSouthWest().lng();
    } else if (typeof L === "object") {
      return this.getBounds().getSouthWest().lng;
    }
  }
  return 0;
};

/**
 * Returns true if map is ready
 * @return {boolean}
 */
trackdirect.models.Map.prototype.isMapReady = function () {
  if (this.getBounds() != null) {
    return true;
  }
  return false;
};

/**
 * Set map type
 * @param {string} mapType
 */
trackdirect.models.Map.prototype.setMapType = function (mapType) {
  if (mapType in this._supportedMapTypes) {
    this._mapType = mapType;
    if (typeof google === "object" && typeof google.maps === "object") {
      this._updateGoogleMapTileLayer();
    } else if (typeof L === "object") {
      this._updateLeafletTileLayer();
    }
    this._emitTdEventListeners("change");
  }
};

/**
 * Get map type
 * @return {string}
 */
trackdirect.models.Map.prototype.getMapType = function () {
  return this._mapType;
};

/**
 * Get leaflet tile layer
 * @return {string}
 */
trackdirect.models.Map.prototype.getLeafletTileLayer = function () {
  return this._leafletTileLayer;
};

/**
 * Returns current mid
 * @return {String}
 */
trackdirect.models.Map.prototype.getMid = function () {
  if (typeof this._tdMapOptions.mid !== "undefined") {
    return this._tdMapOptions.mid;
  }
  return null;
};

/**
 * Reset all markers, this will remove everything from map and memory
 */
trackdirect.models.Map.prototype.resetAllMarkers = function () {
  while (this.markerCollection.getNumberOfMarkers() > 0) {
    var i = this.markerCollection.getNumberOfMarkers();
    while (i--) {
      var marker = this.markerCollection.getMarker(i);
      if (marker !== null) {
        marker.stopToOldTimeout();
        marker.stopDirectionPolyline();
        marker.hide();
        marker.hideMarkerPrevPosition();
        marker.hideMarkerTail();

        var stationCoverage = this.markerCollection.getStationCoverage(marker.packet.station_id);
        if (stationCoverage) {
          stationCoverage.hide();
        }
      }
      this.markerCollection.removeMarker(i);
    }
  }
  if (this.state.openInfoWindow !== null) {
    this.state.openInfoWindow.hide();
  }
  if (this.oms) {
    this.oms.clearMarkers();
  }
  this.markerCollection.resetAllMarkers();
};

/**
 * Open marker info window
 * @param {trackdirect.models.Marker} marker
 * @param {boolean} disableAutoPan
 */
trackdirect.models.Map.prototype.openMarkerInfoWindow = function (
  marker,
  disableAutoPan
) {
  disableAutoPan =
    typeof disableAutoPan !== "undefined" ? disableAutoPan : true;
  if (marker.getMap() !== null) {
    if (
      this.state.openInfoWindow !== null &&
      this.state.openInfoWindow.getMarker().packet.id != marker.packet.id
    ) {
      this.state.openInfoWindow.hide();
    }

    if (
      this.state.openInfoWindow !== null &&
      this.state.openInfoWindow.getMarker().packet.id == marker.packet.id
    ) {
      // Just update existing infoWindow
      this.state.openInfoWindow.setMarker(marker);
    } else {
      this.state.openInfoWindow = new trackdirect.models.InfoWindow(
        marker,
        this,
        disableAutoPan
      );
    }
    this._addInfoWindowListeners(this.state.openInfoWindow);
    this.state.openInfoWindow.show();
  }
};

/**
 * Open latest station info window
 * @param {int} stationId
 */
trackdirect.models.Map.prototype.openLatestStationInfoWindow = function (
  stationId
) {
  var latestVisibleMarker =
    this.markerCollection.getStationLatestVisibleMarker(stationId);
  if (latestVisibleMarker !== null) {
    // open marker info-window since this marker replaced a previous one
    this.openMarkerInfoWindow(latestVisibleMarker);
  }
};

/**
 * Open polyline info window
 * @param {trackdirect.models.Marker} marker
 * @param {LatLng} position
 */
trackdirect.models.Map.prototype.openPolylineInfoWindow = function (
  marker,
  position
) {
  if (this.state.openInfoWindow !== null) {
    this.state.openInfoWindow.hide();
  }
  this.state.openInfoWindow = new trackdirect.models.InfoWindow(marker, this);
  this._addInfoWindowListeners(this.state.openInfoWindow);
  this.state.openInfoWindow.show(true, position);
};

/**
 * Add some trackdirect.models.InfoWindow listeners
 * @param {trackdirect.models.InfoWindow} infoWindow
 */
trackdirect.models.Map.prototype._addInfoWindowListeners = function (
  infoWindow
) {
  var me = this;
  infoWindow.addTdListener("station-tail-needed", function (stationId) {
    me._emitTdEventListeners("station-tail-needed", stationId);
  });
};

/**
 * Add listener to events
 * @param {string} event
 * @param {string} handler
 */
(trackdirect.models.Map.prototype.addTdListener = function (event, handler) {
  if (!(event in this._tdEventListeners)) {
    this._tdEventListeners[event] = [];
  }
  this._tdEventListeners[event].push(handler);
}),
  /**
   * Emit all event listeners for a specified event
   * @param {string} event
   * @param {object} arg
   */
  (trackdirect.models.Map.prototype._emitTdEventListeners = function (
    event,
    arg
  ) {
    if (event in this._tdEventListeners) {
      for (var i = 0; i < this._tdEventListeners[event].length; i++) {
        this._tdEventListeners[event][i](arg);
      }
    }
  });

/**
 * Make sure all listener that are waiting for a map change event gets called
 */
(trackdirect.models.Map.prototype._triggerMapChangeEvent = function () {
  // Execute event "change", but wait some to avoid to many events
  if (this._tdEventTimeout != null) {
    clearTimeout(this._tdEventTimeout);
  }
  var me = this;
  this._tdEventTimeout = window.setTimeout(function () {
    me._emitTdEventListeners("change");
    me._tdEventTimeout = null;
  }, 5);
}),
  /**
   * Deactivate heatmap
   */
  (trackdirect.models.Map.prototype._deactivateHeatMap = function () {
    if (typeof google === "object" && typeof google.maps === "object") {
      if (
        typeof this.overlayMapTypes !== "undefined" &&
        this.overlayMapTypes.length > 0
      ) {
        this.overlayMapTypes.clear();
      }
    } else if (typeof L === "object") {
      if (this._heatMap !== null) {
        this.removeLayer(this._heatMap);
      }
    }
  });

/**
 * Activate heatmap
 */
trackdirect.models.Map.prototype._activateHeatMap = function () {
  if (typeof google === "object" && typeof google.maps === "object") {
    if (
      typeof this.overlayMapTypes !== "undefined" &&
      this.overlayMapTypes.length == 0
    ) {
      this.overlayMapTypes.setAt(0, this._heatMap);
    }
  } else if (typeof L === "object") {
    if (this._heatMap !== null) {
      this._heatMap.addTo(this);
      this._heatMap.bringToFront();
      this._heatMap.setZIndex(1000);
    }
  }
};

/**
 * Update google map tile layer
 */
trackdirect.models.Map.prototype._updateGoogleMapTileLayer = function () {
  this.setMapTypeId(this._supportedMapTypes[this._mapType]);
};

/**
 * Update Leaflet Map Tile Layer
 */
trackdirect.models.Map.prototype._updateLeafletTileLayer = function () {
  // Skip this part if we are running the Windy API or if embedded
  if (typeof windyInit !== "function") {
    if (this._leafletTileLayer !== null) {
      this._leafletTileLayer.remove();
    }

    if (typeof L.mapboxGL === "function") {
      var attribution = "";
      var accessToken = "no-token";
      var style = "";

      if ("mapboxGLStyle" in this._tdMapOptions) {
        style = this._tdMapOptions["mapboxGLStyle"];
      }
      if ("mapboxGLAccessToken" in this._tdMapOptions) {
        accessToken = this._tdMapOptions["mapboxGLAccessToken"];
      }
      if ("mapboxGLAttribution" in this._tdMapOptions) {
        attribution = this._tdMapOptions["mapboxGLAttribution"];
      }

      this._leafletTileLayer = L.mapboxGL({
        accessToken: accessToken,
        style: style,
      });
      this.addLayer(this._leafletTileLayer);
      this.attributionControl.addAttribution(attribution);
    } else {
      var options = {};
      if (isHighDensity()) {
        options["ppi"] = "320";
        options["size"] = "512";
      } else if (trackdirect.isMobile) {
        options["ppi"] = "250";
      }

      this._leafletTileLayer = L.tileLayer.provider(
        this._supportedMapTypes[this._mapType],
        options
      );
      this.addLayer(this._leafletTileLayer);
      this._leafletTileLayer.bringToBack();
    }
  }
};

/**
 * Handle map change event, show markers in new map sectors and hide markers in previous map sectors
 */
trackdirect.models.Map.prototype._updateMapContent = function () {
  if (this.getBounds() != null) {
    var previousVisibleMapSectors = [];
    for (var i = 0; i < this._visibleMapSectors.length; i++) {
      previousVisibleMapSectors.push(this._visibleMapSectors[i]);
    }

    this._visibleMapSectors =
      trackdirect.services.MapSectorCalculator.getMapSectors(this.getBounds());
    this._triggerMapChangeEvent();
    if (!this.state.isFilterMode) {
      if (this.getZoom() < trackdirect.settings.minZoomForMarkers) {
        // When all markers should be hidden we also make sure that markers in current visible map-sectors are removed
        this.hideAllMarkers();
        this._activateHeatMap();
      } else {
        this._deactivateHeatMap();

        this._hideMarkersInPreviousVisibleMapSectors(previousVisibleMapSectors);
        this._showMarkersInNewVisibleMapSectors(previousVisibleMapSectors);
        if (this._isAnyMarkerDetailsVisible()) {
          this._showVisibleMarkerDetails();
        }
        if (this._isAnyMarkerDetailsHidden()) {
          this._hideVisibleMarkerDetails();
        }
      }
    }
  }
  this._currentContentZoom = this.getZoom();
};

/**
 * Returns true if any marker details should be visible
 * @return {boolean}
 */
trackdirect.models.Map.prototype._isAnyMarkerDetailsVisible = function () {
  // This is only needed when zooming (when moving the regular show-marker will also show the details)
  var showPrevPosition =
    this.getZoom() >= trackdirect.settings.minZoomForMarkerPrevPosition &&
    this._currentContentZoom <
      trackdirect.settings.minZoomForMarkerPrevPosition;
  var showMarkerTail =
    this.getZoom() >= trackdirect.settings.minZoomForMarkerTail &&
    this._currentContentZoom < trackdirect.settings.minZoomForMarkerTail;
  var showMarkerLabel =
    this.getZoom() >= trackdirect.settings.minZoomForMarkerLabel &&
    this._currentContentZoom < trackdirect.settings.minZoomForMarkerLabel;

  if (showPrevPosition || showMarkerTail || showMarkerLabel) {
    return true;
  }
  return false;
};

/**
 * Returns true if any marker details should be hidden
 * @return {boolean}
 */
trackdirect.models.Map.prototype._isAnyMarkerDetailsHidden = function () {
  // This is only needed when zooming (when moving the regular show-marker will also show the details)
  var hidePrevPosition =
    this.getZoom() < trackdirect.settings.minZoomForMarkerPrevPosition &&
    this._currentContentZoom >=
      trackdirect.settings.minZoomForMarkerPrevPosition;
  var hideMarkerTail =
    this.getZoom() < trackdirect.settings.minZoomForMarkerTail &&
    this._currentContentZoom >= trackdirect.settings.minZoomForMarkerTail;
  var hideMarkerLabel =
    this.getZoom() < trackdirect.settings.minZoomForMarkerLabel &&
    this._currentContentZoom >= trackdirect.settings.minZoomForMarkerLabel;

  if (hidePrevPosition || hideMarkerTail || hideMarkerLabel) {
    return true;
  }
  return false;
};

/**
 * Show markers details that should be visible in visible map sectors
 */
trackdirect.models.Map.prototype._showVisibleMarkerDetails = function () {
  for (var i = 0; i < this._visibleMapSectors.length; i++) {
    var mapSector = this._visibleMapSectors[i];
    var mapSectorMarkerKeys =
      this.markerCollection.getMapSectorMarkerKeys(mapSector);
    // Array with markers fo this sector exists, we have something to show
    for (var j = 0; j < mapSectorMarkerKeys.length; j++) {
      var markerIdKey = mapSectorMarkerKeys[j];
      var marker = this.markerCollection.getMarker(markerIdKey);
      if (marker === null) {
        continue;
      }
      trackdirect.services.callbackExecutor.addWithPriority(
        marker,
        marker.showMarkerDetails,
        []
      );
    }
  }
};

/**
 * Hide markers details that should not be visible in visible map sectors
 */
trackdirect.models.Map.prototype._hideVisibleMarkerDetails = function () {
  for (var i = 0; i < this._visibleMapSectors.length; i++) {
    var mapSector = this._visibleMapSectors[i];
    var mapSectorMarkerKeys =
      this.markerCollection.getMapSectorMarkerKeys(mapSector);
    // Array with markers fo this sector exists, we have something to hide
    for (var j = 0; j < mapSectorMarkerKeys.length; j++) {
      var markerIdKey = mapSectorMarkerKeys[j];
      var marker = this.markerCollection.getMarker(markerIdKey);
      if (marker === null) {
        continue;
      }
      trackdirect.services.callbackExecutor.addWithPriority(
        marker,
        marker.hideMarkerDetails,
        []
      );
    }
  }
};

/**
 * Show all markers that should be visible and hide alla markers that should not be visible
 * This is used to show or hide markers when user activate/deactivate filters
 */
trackdirect.models.Map.prototype.showHideMarkers = function () {
  if (this.oms) {
    this.oms.unspiderfy();
  }
  if (this.state.isFilterMode) {
    for (var markerIdKey in this.markerCollection.getAllMarkers()) {
      if (this.markerCollection.isExistingMarker(markerIdKey)) {
        var marker = this.markerCollection.getMarker(markerIdKey);

        if (marker) {
          if (marker.shouldMarkerBeVisible()) {
            marker.showCompleteMarker();
          } else {
            marker.hideCompleteMarker();
          }
        }
        if (marker.packet) {
          this.showTopLabelOnPosition(
            marker.packet.latitude,
            marker.packet.longitude
          );
        }
      }
    }
  } else {
    for (var i = 0; i < this._visibleMapSectors.length; i++) {
      var mapSector = this._visibleMapSectors[i];
      var mapSectorMarkerKeys =
        this.markerCollection.getMapSectorMarkerKeys(mapSector);

      // Array with markers for this sector exists, we have something to show/hide
      for (var j = 0; j < mapSectorMarkerKeys.length; j++) {
        var markerIdKey = mapSectorMarkerKeys[j];

        if (this.markerCollection.isExistingMarker(markerIdKey)) {
          var marker = this.markerCollection.getMarker(markerIdKey);
          if (marker.shouldMarkerBeVisible()) {
            marker.showCompleteMarker();
          } else {
            marker.hideCompleteMarker();
          }
          this.showTopLabelOnPosition(
            marker.packet.latitude,
            marker.packet.longitude
          );
        }
      }
    }
  }
};

/**
 * Show or hide ALL PHG Circles
 * This is used to show or hide circles when user activate/deactivate PHG circles
 */
trackdirect.models.Map.prototype.showHidePHGCircles = function () {
  if (this.getZoom() >= trackdirect.settings.minZoomForMarkers) {
    if (this.state.isFilterMode) {
      for (var markerIdKey in this.markerCollection.getAllMarkers()) {
        if (this.markerCollection.isExistingMarker(markerIdKey)) {
          var marker = this.markerCollection.getMarker(markerIdKey);

          if (
            marker.showAsMarker &&
            marker.packet.phg != null &&
            marker.getMap() !== null &&
            marker.shouldMarkerBeVisible()
          ) {
            if (this.state.showPHGCircles == 0) {
              marker.hidePHGCircle();
            } else if (this.state.showPHGCircles == 1) {
              marker.showPHGCircle(true);
            } else if (this.state.showPHGCircles == 2) {
              marker.showPHGCircle(false);
            }
          }
        }
      }
    } else {
      for (var i = 0; i < this._visibleMapSectors.length; i++) {
        var mapSector = this._visibleMapSectors[i];
        var mapSectorMarkerKeys =
          this.markerCollection.getMapSectorMarkerKeys(mapSector);
        // Array with markers for this sector exists, we have something to show/hide
        for (var j = 0; j < mapSectorMarkerKeys.length; j++) {
          var markerIdKey = mapSectorMarkerKeys[j];

          if (this.markerCollection.isExistingMarker(markerIdKey)) {
            var marker = this.markerCollection.getMarker(markerIdKey);

            if (
              marker.showAsMarker &&
              marker.packet.phg != null &&
              marker.getMap() !== null &&
              marker.shouldMarkerBeVisible()
            ) {
              if (this.state.showPHGCircles == 0) {
                marker.hidePHGCircle();
              } else if (this.state.showPHGCircles == 1) {
                marker.showPHGCircle(true);
              } else if (this.state.showPHGCircles == 2) {
                marker.showPHGCircle(false);
              }
            }
          }
        }
      }
    }
  }
};

/**
 * Show or hide ALL RNG Circles
 * This is used to show or hide circles when user activate/deactivate PHG circles
 */
trackdirect.models.Map.prototype.showHideRNGCircles = function () {
  if (this.getZoom() >= trackdirect.settings.minZoomForMarkers) {
    if (this.state.isFilterMode) {
      for (var markerIdKey in this.markerCollection.getAllMarkers()) {
        if (this.markerCollection.isExistingMarker(markerIdKey)) {
          var marker = this.markerCollection.getMarker(markerIdKey);
          if (
            marker.showAsMarker &&
            marker.packet.rng != null &&
            marker.getMap() !== null &&
            marker.shouldMarkerBeVisible()
          ) {
            if (this.state.showRNGCircles == 0) {
              marker.hideRNGCircle();
            } else if (this.state.showRNGCircles == 1) {
              marker.showRNGCircle(true);
            } else if (this.state.showRNGCircles == 2) {
              marker.showRNGCircle(false);
            }
          }
        }
      }
    } else {
      for (var i = 0; i < this._visibleMapSectors.length; i++) {
        var mapSector = this._visibleMapSectors[i];
        var mapSectorMarkerKeys =
          this.markerCollection.getMapSectorMarkerKeys(mapSector);
        // Array with markers for this sector exists, we have something to show/hide
        for (var j = 0; j < mapSectorMarkerKeys.length; j++) {
          var markerIdKey = mapSectorMarkerKeys[j];

          if (this.markerCollection.isExistingMarker(markerIdKey)) {
            var marker = this.markerCollection.getMarker(markerIdKey);
            if (
              marker.showAsMarker &&
              marker.packet.rng != null &&
              marker.getMap() !== null &&
              marker.shouldMarkerBeVisible()
            ) {
              if (this.state.showRNGCircles == 0) {
                marker.hideRNGCircle();
              } else if (this.state.showRNGCircles == 1) {
                marker.showRNGCircle(true);
              } else if (this.state.showRNGCircles == 2) {
                marker.showRNGCircle(false);
              }
            }
          }
        }
      }
    }
  }
};

/**
 * Make sure that all markers that we know is hidden
 */
trackdirect.models.Map.prototype.hideAllMarkers = function () {
  for (var markerIdKey in this.markerCollection.getAllMarkers()) {
    var marker = this.markerCollection.getMarker(markerIdKey);
    if (marker !== null) {
      // hide this marker
      marker.hideCompleteMarker();
    }
  }
};

/**
 * Make the label of the latest received marker show on specified position
 * @param {number} latitude
 * @param {number} longitude
 */
trackdirect.models.Map.prototype.showTopLabelOnPosition = function (
  latitude,
  longitude
) {
  var topMarkerIdKey = -1;
  var topMarkerZindex = 0;

  if (
    Object.keys(
      this.markerCollection.getPositionMarkerIdKeys(latitude, longitude)
    ).length > 1
  ) {
    for (var markerIdKey in this.markerCollection.getPositionMarkerIdKeys(
      latitude,
      longitude
    )) {
      var marker = this.markerCollection.getMarker(markerIdKey);
      if (marker !== null && marker.shouldMarkerBeVisible()) {
        if (marker.getZIndex() > topMarkerZindex) {
          topMarkerZindex = marker.getZIndex();
          topMarkerIdKey = markerIdKey;
        }
        marker.hideLabel();
        marker.hasLabel = false;
      }
    }

    if (topMarkerIdKey != -1) {
      var topMarker = this.markerCollection.getMarker(topMarkerIdKey);
      topMarker.hasLabel = true;
      var topMarkerMapSector =
        trackdirect.services.MapSectorCalculator.getMapSector(
          topMarker.getPositionLiteral().lat,
          topMarker.getPositionLiteral().lng
        );
      if (this.state.isFilterMode) {
        topMarker.showLabel();
      } else if (
        this.isMapSectorVisible(topMarkerMapSector) &&
        this.getZoom() >= trackdirect.settings.minZoomForMarkerLabel
      ) {
        topMarker.showLabel();
      }
    }
  }
};

/**
 * Hide markers in previously visible map sectors
 * (This should handle both zooming and moving)
 * @param {array} previousVisibleMapSectors
 */
trackdirect.models.Map.prototype._hideMarkersInPreviousVisibleMapSectors =
  function (previousVisibleMapSectors) {
    // IMPORTANT: Do this before showing marker since marker may exist in both previus shown sectors and visible sectors
    // (if we show first we may hide something that should be visible)

    if (this._currentContentZoom >= trackdirect.settings.minZoomForMarkers) {
      var markerIdKeyListToMaybeHide = {};
      var markerIdKeyListNotToHide = {};
      for (var i = 0; i < previousVisibleMapSectors.length; i++) {
        var mapSector = previousVisibleMapSectors[i];
        if (
          !this.isMapSectorVisible(mapSector) ||
          this.getZoom() < trackdirect.settings.minZoomForMarkers
        ) {
          // Seems like this sector is not visible any more (or we have zoomed out), hide markers
          var mapSectorMarkerKeys =
            this.markerCollection.getMapSectorMarkerKeys(mapSector);
          for (var j = 0; j < mapSectorMarkerKeys.length; j++) {
            var markerIdKey = mapSectorMarkerKeys[j];
            markerIdKeyListToMaybeHide[markerIdKey] = markerIdKey;
          }
        } else if (this.getZoom() >= trackdirect.settings.minZoomForMarkers) {
          // Seems like this map sector is still visible (and we have not zoomed out)
          var mapSectorMarkerKeys =
            this.markerCollection.getMapSectorMarkerKeys(mapSector);
          for (var j = 0; j < mapSectorMarkerKeys.length; j++) {
            var markerIdKey = mapSectorMarkerKeys[j];
            // Marker exists in map sector that is still visible, do not hide it
            markerIdKeyListNotToHide[markerIdKey] = markerIdKey;
          }
        }
      }
      for (var markerIdKey in markerIdKeyListToMaybeHide) {
        if (markerIdKey in markerIdKeyListNotToHide) {
          continue;
        }
        var marker = this.markerCollection.getMarker(markerIdKey);
        if (marker !== null) {
          // hide this marker
          trackdirect.services.callbackExecutor.addWithPriority(
            marker,
            marker.hideCompleteMarker,
            []
          );
        }
      }
    }
  };

/**
 * Show markers in new visible map sectors
 * @param {array} previousVisibleMapSectors
 */
trackdirect.models.Map.prototype._showMarkersInNewVisibleMapSectors = function (
  previousVisibleMapSectors
) {
  // Show new markers that is visible in new map sectors
  // This should handle both zooming and moving

  if (this.getZoom() >= trackdirect.settings.minZoomForMarkers) {
    for (var i = 0; i < this._visibleMapSectors.length; i++) {
      var mapSector = this._visibleMapSectors[i];
      if (
        previousVisibleMapSectors.indexOf(mapSector) == -1 ||
        this._currentContentZoom < trackdirect.settings.minZoomForMarkers
      ) {
        // Seems like this sector is new (or we have zoomed in now), show markers
        var mapSectorMarkerKeys =
          this.markerCollection.getMapSectorMarkerKeys(mapSector);
        for (var j = 0; j < mapSectorMarkerKeys.length; j++) {
          var markerIdKey = mapSectorMarkerKeys[j];
          var marker = this.markerCollection.getMarker(markerIdKey);
          if (marker !== null) {
            trackdirect.services.callbackExecutor.addWithPriority(
              marker,
              marker.showCompleteMarker,
              []
            );
          }
        }
      }
    }

    // Also make sure all stations with a visible coverage is shown
    var stationIdList =
      this.markerCollection.getStationIdListWithVisibleCoverage();
    for (var i = 0; i < stationIdList.length; i++) {
      var latestMarker = this.markerCollection.getStationLatestMarker(
        stationIdList[i]
      );
      if (latestMarker !== null) {
        if (latestMarker.shouldMarkerBeVisible() && latestMarker.showAsMarker) {
          latestMarker.show();
        }
      }
    }
  }
};

/**
 * Set map initial position
 */
trackdirect.models.Map.prototype._setMapInitialLocation = function () {
  var zoom = this._getInitialZoom();
  if (
    typeof this._tdMapOptions.initCenter !== "undefined" &&
    this._tdMapOptions.initCenter !== null
  ) {
    var pos = this._tdMapOptions.initCenter;
    this.setCenter(pos, zoom);
  } else {
    this.setMapDefaultLocation();
    this.setZoom(zoom);
  }
  this._emitTdEventListeners("change");
};

/**
 * Set map default location
 */
trackdirect.models.Map.prototype.setMapDefaultLocation = function (
  setDefaultZoom
) {
  setDefaultZoom =
    typeof setDefaultZoom !== "undefined" ? setDefaultZoom : false;

  var defaultLatitude =
    typeof this._tdMapOptions.defaultLatitude !== "undefined"
      ? this._tdMapOptions.defaultLatitude
      : 59.35;
  var defaultLongitude =
    typeof this._tdMapOptions.defaultLongitude !== "undefined"
      ? this._tdMapOptions.defaultLongitude
      : 18.05;

  var pos = {
    lat: parseFloat(defaultLatitude),
    lng: parseFloat(defaultLongitude),
  };

  if (setDefaultZoom) {
    if (trackdirect.isMobile) {
      this.setCenter(pos, trackdirect.settings.defaultCurrentZoomMobile);
    } else {
      this.setCenter(pos, trackdirect.settings.defaultCurrentZoom);
    }
  } else {
    this.setCenter(pos);
  }
};

/**
 * Add marker to multiple Map-Sectors, useful for very long polylines related to a marker
 * @param {int} markerIdKey
 * @param {LatLngLiteral} startLatLng
 * @param {LatLngLiteral} endLatLng
 */
trackdirect.models.Map.prototype.addMarkerToMapSectorInterval = function (
  markerIdKey,
  startLatLng,
  endLatLng
) {
  var minLat = startLatLng.lat;
  var maxLat = endLatLng.lat;
  var minLng = startLatLng.lng;
  var maxLng = endLatLng.lng;
  if (endLatLng.lat < minLat) {
    minLat = endLatLng.lat;
    maxLat = startLatLng.lat;
  }
  if (endLatLng.lng < minLng) {
    minLng = endLatLng.lng;
    maxLng = startLatLng.lng;
  }
  for (var lat = Math.floor(minLat); lat <= Math.ceil(maxLat); lat++) {
    for (var lng = Math.floor(minLng); lng <= Math.ceil(maxLng); lng++) {
      var markerMapSector =
        trackdirect.services.MapSectorCalculator.getMapSector(lat, lng);

      this.markerCollection.addMarkerToMapSector(markerIdKey, markerMapSector);

      if (this.isMapSectorVisible(markerMapSector)) {
        if (this._newMarkersToShow.indexOf(markerIdKey) < 0) {
          this._newMarkersToShow.push(markerIdKey);
        }
      }
    }
  }
};

/**
 * Add marker the related map sector based in latest packet
 * @param {int} markerIdKey
 * @param {object} packet
 * @param {boolean} tryToShowPacket
 */
trackdirect.models.Map.prototype.addMarkerToMapSectors = function (
  markerIdKey,
  packet,
  tryToShowPacket
) {
  var markerMapSectors = [];

  markerMapSectors.push(packet.map_sector);
  if (
    typeof packet.related_map_sectors !== "undefined" &&
    packet.related_map_sectors !== null
  ) {
    for (var i = 0; i < packet.related_map_sectors.length; i++) {
      markerMapSectors.push(packet.related_map_sectors[i]);
    }
  }

  for (var i = 0; i < markerMapSectors.length; i++) {
    var markerMapSector = markerMapSectors[i];
    this.markerCollection.addMarkerToMapSector(markerIdKey, markerMapSector);

    if (tryToShowPacket) {
      if (this.isMapSectorVisible(markerMapSector)) {
        if (this._newMarkersToShow.indexOf(markerIdKey) < 0) {
          this._newMarkersToShow.push(markerIdKey);
        }
      }
    }
  }
};

/**
 * Initialize map basic events
 */
trackdirect.models.Map.prototype._initMapEvents = function () {
  if (typeof google === "object" && typeof google.maps === "object") {
    this._initGoogleMapEvents();
  } else if (typeof L === "object") {
    this._initLeafletMapEvents();
  }
};

/**
 * Initialize google map basic events
 */
trackdirect.models.Map.prototype._initGoogleMapEvents = function () {
  var me = this;
  google.maps.event.addListener(this, "mousemove", function (event) {
    me._renderCordinatesContainer(event.latLng);
  });

  google.maps.event.addListener(this, "idle", function () {
    me._updateMapContent();
  });

  google.maps.event.addListener(this, "maptypeid_changed", function () {
    me._updateMapContent();
  });

  google.maps.event.addListener(this, "bounds_changed", function () {
    if (me.isMapReady()) {
      me._emitTdEventListeners("moving");
    }
  });
};

/**
 * Initialize leaflet map basic events
 */
trackdirect.models.Map.prototype._initLeafletMapEvents = function () {
  var me = this;
  this.on("mousemove", function (event) {
    me._renderCordinatesContainer(event.latlng);
  });

  this.on("moveend", function () {
    me._updateMapContent();
  });
  /*
    this.on('maptypeid_changed', function() {
        me._updateMapContent();
    });
*/
  this.on("move", function () {
    if (me.isMapReady()) {
      me._emitTdEventListeners("moving");
    }
  });
};

/**
 * Initialize OMS
 */
trackdirect.models.Map.prototype._initOms = function () {
  var options = {};
  options["nearbyDistance"] = 12;
  if (typeof google === "object" && typeof google.maps === "object") {
    var mti = google.maps.MapTypeId;
    this.oms = new OverlappingMarkerSpiderfier(this, options);
    this.oms.legColors.usual[mti.HYBRID] = this.oms.legColors.usual[
      mti.SATELLITE
    ] = "#fff";
    this.oms.legColors.usual[mti.TERRAIN] = this.oms.legColors.usual[
      mti.ROADMAP
    ] = "#222";
    this.oms.legColors.highlighted[mti.HYBRID] = this.oms.legColors.highlighted[
      mti.SATELLITE
    ] = "#f00";
    this.oms.legColors.highlighted[mti.TERRAIN] =
      this.oms.legColors.highlighted[mti.ROADMAP] = "#f00";
  } else if (typeof L === "object") {
    this.oms = new OverlappingMarkerSpiderfier(this, options);
  }
};

/**
 * Initialize info window for markers
 */
trackdirect.models.Map.prototype._initInfoWindowEvent = function () {
  var me = this;
  if (this.oms) {
    this.oms.addListener("click", function (marker, event) {
      me.openMarkerInfoWindow(marker, false);
    });
  } else {
  }
};

/**
 * Get default google "map options", used for initializing google map
 * @return {object}
 */
trackdirect.models.Map.prototype._getGoolgeMapOptions = function () {
  var zoom = this._getInitialZoom();
  var mapOptions = {
    zoom: zoom,
    panControl: false,
    zoomControl: true,
    zoomControlOptions: {
      position: google.maps.ControlPosition.RIGHT_BOTTOM,
    },
    mapTypeControl: false,
    scaleControl: false,
    streetViewControl: false,
    overviewMapControl: false,
    fullscreenControl: false,
    mapTypeId: google.maps.MapTypeId.ROADMAP,
    gestureHandling: "greedy",
  };

  mapOptions.mapTypeId = this._supportedMapTypes[this._mapType];
  return mapOptions;
};

/**
 * Get default leaflet "map options", used for initializing google map
 * @return {object}
 */
trackdirect.models.Map.prototype._getLeafletMapOptions = function () {
  var zoom = this._getInitialZoom();
  var mapOptions = {
    zoom: zoom,
    zoomControl: true,
    attributionControl: true,
    zoomControl: false,
    minZoom: 3,
    maxZoom: 16,
    closePopupOnClick: false,
  };

  return mapOptions;
};

/**
 * Get initial zoom
 * @return {int}
 */
trackdirect.models.Map.prototype._getInitialZoom = function () {
  var zoom = trackdirect.settings.defaultCurrentZoom;
  if (
    typeof this._tdMapOptions.zoom !== "undefined" &&
    this._tdMapOptions.zoom !== null
  ) {
    zoom = parseInt(this._tdMapOptions.zoom);
  } else if (trackdirect.isMobile) {
    zoom = trackdirect.settings.defaultCurrentZoomMobile;
  }

  return zoom;
};

/**
 * Get radius in Km (radius is from center of current map view to the most north east position)
 * @return {int}
 */
trackdirect.models.Map.prototype.getCurrentRadiusInKm = function () {
  if (this.getBounds() != null) {
    if (typeof google === "object" && typeof google.maps === "object") {
      var latLng = this.getBounds().getNorthEast();
      var latLngLiteral = { lat: latLng.lat(), lng: latLng.lng() };
    } else if (typeof L === "object") {
      var latLng = this.getBounds().getNorthEast();
      var latLngLiteral = { lat: latLng.lat, lng: latLng.lng };
    }
    return (
      trackdirect.services.distanceCalculator.getDistance(
        this.getCenterLiteral(),
        latLngLiteral
      ) / 1000
    );
  }
  return 0;
};

/**
 * Print position in the cordinates container
 * @return {google.maps.LatLng/L.LatLng/LatLngLiteral} mouseLatLng
 */
trackdirect.models.Map.prototype._renderCordinatesContainer = function (
  mouseLatLng
) {
  var options = this.getTdMapOptions();
  if (typeof options.cordinatesContainer === "undefined") {
    return;
  }
  if (options.cordinatesContainer == null) {
    return;
  }

  var lat = null;
  var lng = null;
  if (typeof mouseLatLng.lat == "function") {
    lat = mouseLatLng.lat();
    lng = mouseLatLng.lng();
  } else {
    lat = mouseLatLng.lat;
    lng = mouseLatLng.lng;
  }

  if (lat <= 90 && lat >= -90 && lng <= 180 && lng >= -180) {
    var content = "";
    content += this._getGpsDegreeFromGpsDecimal(lat.toFixed(5), "lat");
    content += " " + this._getGpsDegreeFromGpsDecimal(lng.toFixed(5), "lon");
    content += "<br>" + lat.toFixed(5) + ", " + lng.toFixed(5);
    content += "<br>" + this._getMaidenheadLocatorFromGpsDecimal(lat, lng);

    $("#" + options.cordinatesContainer).html(content);
  }
};

/**
 * Convert decimal gps position to degree format
 * @param {float} dms
 * @param {string} type
 * @return {string}
 */
trackdirect.models.Map.prototype._getGpsDegreeFromGpsDecimal = function (
  dms,
  type
) {
  var sign = 1,
    Abs = 0;
  var days, minutes, secounds, direction;

  if (dms < 0) {
    sign = -1;
  }
  Abs = Math.abs(Math.round(dms * 1000000));
  //Math.round is used to eliminate the small error caused by rounding in the computer:
  //e.g. 0.2 is not the same as 0.20000000000284
  //Error checks
  if (type == "lat" && Abs > 90 * 1000000) {
    //alert(" Degrees Latitude must be in the range of -90. to 90. ");
    return false;
  } else if (type == "lon" && Abs > 180 * 1000000) {
    //alert(" Degrees Longitude must be in the range of -180 to 180. ");
    return false;
  }

  days = Math.floor(Abs / 1000000);
  minutes = Math.floor((Abs / 1000000 - days) * 60);
  secounds = (
    (Math.floor(((Abs / 1000000 - days) * 60 - minutes) * 100000) * 60) /
    100000
  ).toFixed();
  days = days * sign;
  if (type == "lat") direction = days < 0 ? "S" : "N";
  if (type == "lon") direction = days < 0 ? "W" : "E";
  //else return value
  return days * sign + "º " + minutes + "' " + secounds + "'' " + direction;
};

/**
 * Convert decimal gps position to maidenhead locator
 * @param {float} lat
 * @param {float} lng
 * @return {string}
 */
trackdirect.models.Map.prototype._getMaidenheadLocatorFromGpsDecimal = function (
  lat,
  lng,
) {
  const chars = 'ABCDEFGHIJKLMNOPQRSTUVX';
  var result = '';
  lng = lng + 180;
  lat = lat + 90;
  result  = chars.charAt(parseInt(lng / 20));
  result += chars.charAt(parseInt(lat / 10));
  result += parseInt(lng / 2 % 10);
  result += parseInt(lat % 10);
  lng_r = (lng - parseInt(lng/2)*2) * 60;
  lat_r = (lat - parseInt(lat)) * 60;
  result += chars.charAt(parseInt(lng_r/5));
  result += chars.charAt(parseInt(lat_r/2.5));
  return result;
};
