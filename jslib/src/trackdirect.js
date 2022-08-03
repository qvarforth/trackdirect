var trackdirect = {
  services: {},
  models: {},

  _time: null, // How many minutes of history to show
  _timetravel: null, // Unix timestamp to travel to
  _center: null, // Position to center on (for example "46.52108,14.63379")
  _zoom: null, // Zoom level
  _maptype: null, // May be "roadmap", "terrain" or "satellite"
  _mid: null,

  _rulers: [],

  _filterTimeoutId: null,
  _waitForFilterResponse: false,
  _doNotChangeLocationOnFilterResponse: false,
  _doNotChangeLocationOnFilterResponseTmp: false,

  _filters: {},

  _defaultLatitude: null,
  _defaultLongitude: null,

  _eventListeners: {},
  _eventListenersOnce: {},

  _cordinatesContainerElementId: null,
  _statusContainerElementId: "td-status-text",
  _mapElementId: null,

  _wsServerUrl: null,

  _map: null,
  _websocket: null,

  _mapCreated: false,
  _trackdirectInitDone: false,

  isMobile: false,
  coverageDataUrl: null,
  coveragePercentile: 95,
  settings: {},

  /**
   * Initialize
   * @param {string} wsServerUrl
   * @param {string} mapElementId
   * @param {object} options
   */
  init: function (wsServerUrl, mapElementId, options) {
    this._initSettings();
    this._wsServerUrl = wsServerUrl;
    this._mapElementId = mapElementId;

    if ($("#" + mapElementId).length <= 0) {
      // map element does not exists, nothing to do...
      console.log("ERROR: Specified map element missing");
      return;
    }

    if (typeof google === "object" && typeof google.maps === "object") {
      // Google maps is slow with to many labels
      this.settings.defaultMinZoomForMarkerLabel = 12;
      this.settings.minZoomForMarkerLabel = 12;
    }

    this._parseOptions(options);

    var me = this;
    this.addListener("map-created", function () {
      me._initTime();

      me._websocket = new trackdirect.Websocket(me._wsServerUrl);
      me._initWebsocketListeners();
      me._handleWebsocketStateChange();

      me._initMapListeners();
      if (!me._initFilterUrlRequest()) {
        trackdirect.services.callbackExecutor.add(
          me,
          me._sendPositionRequest,
          []
        );
      }

      me._setWebsocketStateIdle();

      if (inIframe()) {
        // Somebody has included trackdirect inside an iframe... In the future we may STOP this but currently we allow it...
        var parentUrl = "";
        try {
          parentUrl =
            window.location != window.parent.location
              ? document.referrer
              : document.location.href;
        } catch (e) {
          parentUrl = "Unknown";
        }
      }

      me._emitEventListeners("trackdirect-init-done");
    });

    this._mapInit(options);
  },

  /**
   * Enable Imperial units
   * @return null
   */
  enableImperialUnits: function () {
    this._map.state.useImperialUnit = true;
    if (this._map.state.openInfoWindow !== null) {
      this._map.state.openInfoWindow.hide();
    }
  },

  /**
   * Enable Metric units
   * @return null
   */
  enableMetricUnits: function () {
    this._map.state.useImperialUnit = false;
    if (this._map.state.openInfoWindow !== null) {
      this._map.state.openInfoWindow.hide();
    }
  },

  /**
   * Enable/Disable Imperial units
   * @return null
   */
  toggleImperialUnits: function () {
    if (this._map.state.useImperialUnit) {
      this.enableMetricUnits();
    } else {
      this.enableImperialUnits();
    }
  },

  /**
   * Returns true if Imperial units is active
   * @return boolean
   */
  isImperialUnits: function () {
    return this._map.state.useImperialUnit;
  },

  /**
   * Add new event listener
   * @param {string} event
   * @param {string} handler
   * @param {boolean} execOnce
   * @return null
   */
  addListener: function (event, handler, execOnce) {
    execOnce = typeof execOnce !== "undefined" ? execOnce : false;
    if (
      (event == "map-created" && this._mapCreated) ||
      (event == "trackdirect-init-done" && this._trackdirectInitDone)
    ) {
      handler();
      if (execOnce) {
        return;
      }
    }

    if (execOnce) {
      if (!(event in this._eventListenersOnce)) {
        this._eventListenersOnce[event] = [];
      }
      this._eventListenersOnce[event].push(handler);
    } else {
      if (!(event in this._eventListeners)) {
        this._eventListeners[event] = [];
      }
      this._eventListeners[event].push(handler);
    }
  },

  /**
   * Set map center
   * @param {float} latitude
   * @param {float} longitude
   * @param {int} zoom
   * @return None
   */
  setCenter: function (latitude, longitude, zoom) {
    latitude =
      typeof latitude !== "undefined" ? latitude : this._defaultLatitude;
    longitude =
      typeof longitude !== "undefined" ? longitude : this._defaultLongitude;
    zoom =
      typeof zoom !== "undefined" ? zoom : this._map.getZoom();

    if (this._map !== null) {
      this._map.setCenter({ lat: latitude, lng: longitude }, zoom);
    }
  },

  /**
   * Set zoom
   * @param {int} value
   * @return None
   */
  setZoom: function (value) {
    if (this._map !== null) {
      this._map.setZoom(value);
    }
  },

  /**
   * Add a ruler
   * @return None
   */
  addRuler: function () {
    if (this._rulers.length > 0) {
      var ruler = this._rulers.pop();
      ruler.hide();
    } else {
      var ruler = new trackdirect.models.Ruler(
        (this._map.getCurrentRadiusInKm() * 1000) / 2,
        this._map
      );
      this._rulers.push(ruler);
    }
  },

  /**
   * Returns true if we are filtering on one or several stations
   * @return {boolean}
   */
  isFilteredMode: function () {
    return this._map.state.isFilterMode;
  },

  /**
   * Stop filter on station
   * @return {int} stationId
   */
  stopFilterOnStationId: function (stationId) {
    var currentFilterStationIds = this._map.state.getFilterStationIds();
    if (
      currentFilterStationIds.length == 1 &&
      currentFilterStationIds.indexOf(stationId) >= 0
    ) {
      this.filterOnStationId([]);
    } else {
      if (this._map.state.getTrackStationId() == stationId) {
        this.stopTrackStation();
      }
      this._setWebsocketStateLoading(false);
      this._websocket.doSendStopFilterRequest(stationId);
    }
  },

  /**
   * Filter on station
   * @return {array} stationIdArray
   */
  filterOnStationId: function (stationIdArray) {
    if (!Array.isArray(stationIdArray)) {
      stationIdArray = [stationIdArray];
    }

    // If user wants to start filtering and we are tracking something else, stop tracking
    var currentFilterStationIds = this._map.state.getFilterStationIds();
    if (currentFilterStationIds.length == 0) {
      if (
        this._map.state.getTrackStationId() !== null &&
        stationIdArray.indexOf(this._map.state.getTrackStationId()) == -1
      ) {
        this.stopTrackStation();
      }
    }

    this._setWebsocketStateLoading(false);
    this._websocket.doSendFilterRequest(
      stationIdArray,
      this._map.state.getTimeLength() / 60,
      this.getTimeTravelTimestamp()
    );
  },

  /**
   * Filter on station by name
   * @return {array} stationNameArray
   */
  filterOnStationName: function (stationNameArray) {
    if (!Array.isArray(stationNameArray)) {
      stationNameArray = [stationNameArray];
    }

    // If user wants to start filtering and we are tracking something else, stop tracking
    var currentFilterStationIds = this._map.state.getFilterStationIds();
    if (currentFilterStationIds.length == 0) {
      if (
        this._map.state.getTrackStationId() !== null &&
        stationIdArray.indexOf(this._map.state.getTrackStationId()) == -1
      ) {
        this.stopTrackStation();
      }
    }

    this._setWebsocketStateLoading(false);
    this._websocket.doSendFilterRequestByName(
      stationNameArray,
      this._map.state.getTimeLength() / 60,
      this.getTimeTravelTimestamp()
    );
  },

  /**
   * Stop track station
   * @return {int} stationId
   */
  stopTrackStation: function () {
    this._map.state.onlyTrackRecentPackets = false;
    this._map.state.trackStationId = null;
    this._emitEventListeners("track-changed", [null, null]);
  },

  /**
   * Track station
   * @param {int} stationId
   * @param {string} stationName
   * @param {boolean} alsofilterOnStation
   * @param {boolean} onlyTrackRecentPackets
   * @return null
   */
  trackStation: function (
    stationId,
    stationName,
    alsoFilterOnStation,
    onlyTrackRecentPackets
  ) {
    onlyTrackRecentPackets =
      typeof onlyTrackRecentPackets !== "undefined"
        ? onlyTrackRecentPackets
        : false;

    // if user are filtering and want to track a station that we do not filter in, start filtering on that station
    if (alsoFilterOnStation) {
      var currentFilterStationIds = this._map.state.getFilterStationIds();
      if (currentFilterStationIds.length > 0) {
        if (currentFilterStationIds.indexOf(stationId) == -1) {
          this.filterOnStationId(stationId);
        }
      }
    }

    if (stationId !== null) {
      var trackLinkElementClass = "trackStationLink" + stationId;
      $("." + trackLinkElementClass).html("Untrack");
    }

    if (this._map.state.trackStationId !== null) {
      var trackLinkElementClass =
        "trackStationLink" + this._map.state.trackStationId;
      $("." + trackLinkElementClass).html("Track");
    }

    this._map.state.onlyTrackRecentPackets = onlyTrackRecentPackets;
    this._map.state.trackStationId = stationId;

    this._emitEventListeners("track-changed", [stationId, stationName]);
  },

  /**
   * Move focus to specified station
   * @param {int} stationId
   * @param {boolean} openInfoWindow
   * @return Boolean
   */
  focusOnStation: function (stationId, openInfoWindow) {
    var map = this._map;
    openInfoWindow =
      typeof openInfoWindow !== "undefined" ? openInfoWindow : false;
    var marker = map.markerCollection.getStationLatestMarker(stationId);
    if (marker !== null) {
      marker.show();
      marker.showLabel();

      // Set focus
      if (openInfoWindow) {
        map.openMarkerInfoWindow(marker, false);
      } else {
        this.setCenter(marker.packet.latitude, marker.packet.longitude);
      }

      // This method will hide marker when infowindow is closed, if nessecery
      marker.hide(5000, true);
      return true;
    } else {
      return false;
    }
  },

  /**
   * Move focus to specified marker
   * @param {int} markerId
   * @param {int} zoom
   * @return None
   */
  focusOnMarkerId: function (markerId, zoom) {
    var map = this._map;
    var markerIdKey = map.markerCollection.getMarkerIdKey(markerId);
    if (map.markerCollection.isExistingMarker(markerIdKey)) {
      var marker = map.markerCollection.getMarker(markerIdKey);

      if (map.markerCollection.hasRelatedDashedPolyline(marker)) {
        newerMarker = map.markerCollection.getMarker(
          marker._relatedMarkerOriginDashedPolyLine.ownerMarkerIdKey
        );
        if (newerMarker.packet.hasConfirmedMapId()) {
          return this.focusOnMarkerId(newerMarker.packet.marker_id);
        }
      }

      marker.show();
      marker.showLabel();

      // Set focus
      this.setCenter(marker.packet.latitude, marker.packet.longitude, zoom);
      map.openMarkerInfoWindow(marker);

      // This method will hide marker when infowindow is closed, if nessecery
      marker.hide(5000, true);
    }
  },

  /**
   * Toggle station coverage
   * @param {int} stationId
   * @param {string} coverageLinkElementClass
   */
  toggleStationCoverage: function (stationId, coverageLinkElementClass) {
    coverageLinkElementClass =
      typeof coverageLinkElementClass !== "undefined"
        ? coverageLinkElementClass
        : null;

    var coveragePolygon =
      this._map.markerCollection.getStationCoverage(stationId);
    if (coveragePolygon !== null && coveragePolygon.isRequestedToBeVisible()) {
      coveragePolygon.hide();
      if (coverageLinkElementClass !== null) {
        $("." + coverageLinkElementClass).html("Coverage");
      }
    } else {
      if (coveragePolygon !== null) {
        coveragePolygon.show();

        if (!coveragePolygon.hasContent()) {
          alert(
            "Currently we do not have enough data to create a max range coverage plot for this station. Try again later!"
          );
        } else {
          if (coverageLinkElementClass !== null) {
            $("." + coverageLinkElementClass).html("Hide coverage");
          }
        }
      } else {
        var packet =
          this._map.markerCollection.getStationLatestPacket(stationId);
        var center = {
          lat: parseFloat(packet.latitude),
          lng: parseFloat(packet.longitude),
        };
        var coveragePolygon = new trackdirect.models.StationCoveragePolygon(
          center,
          this._map,
          true
        );
        this._map.markerCollection.addStationCoverage(
          stationId,
          coveragePolygon
        );
        coveragePolygon.showWhenDone();

        if (coverageLinkElementClass !== null) {
          $("." + coverageLinkElementClass).html(
            'Loading <i class="fa fa-spinner fa-spin" style="font-size:12px"></i>'
          );
          coveragePolygon.addTdListener(
            "visible",
            function () {
              if (!coveragePolygon.hasContent()) {
                coveragePolygon.hide();
                alert(
                  "Currently we do not have enough data to create a max range coverage plot for this station. Try again later!"
                );
                $("." + coverageLinkElementClass).html("Coverage");
              } else {
                $("." + coverageLinkElementClass).html("Hide coverage");
              }
            },
            true
          );
        }

        var me = this;
        $.getJSON(this.coverageDataUrl + "?id=" + stationId, function (data) {
          if ("station_id" in data && "coverage" in data) {
            coveragePolygon.setData(data["coverage"], me.coveragePercentile);
            var marker =
              me._map.markerCollection.getStationLatestMarker(stationId);
            if (marker.isVisible()) {
              if (coveragePolygon.isRequestedToBeVisible()) {
                coveragePolygon.show();
              }
            }
          }
        })
          .fail(function () {
            coveragePolygon.hide();
            alert("Failed to fetch coverage data. Try again later!");
            $("." + coverageLinkElementClass).html("Coverage");
          })
          .always(function () {});
      }
    }
  },

  /**
   * Set map type
   * @param {string} mapType
   * @return None
   */
  setMapType: function (mapType) {
    if (this._map !== null) {
      this._map.setMapType(mapType);
    }
  },

  /**
   * Set map type
   * @return {string}
   */
  getMapType: function () {
    if (this._map !== null) {
      return this._map.getMapType();
    }
  },

  /**
   * Set map default location
   * @param {boolean} setDefaultZoom
   * @return None
   */
  setMapDefaultLocation: function (setDefaultZoom) {
    this._map.setMapDefaultLocation(setDefaultZoom);
  },

  /**
   * Set map location based on user position by using geo location functionality
   * @param {function} failCallBack
   * @param {function} successCallBack
   * @param int timeout
   * @return None
   */
  setMapLocationByGeoLocation: function (
    failCallBack,
    successCallBack,
    timeout
  ) {
    var me = this;
    if (navigator && navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        function (position) {
          var pos = {
            lat: position.coords.latitude,
            lng: position.coords.longitude,
          };
          me._map.setCenter(pos, 12);
          if (successCallBack !== null) {
            successCallBack();
          }
        },
        function (error) {
          // User said NO (or other error)
          // Note that you will not end up here if browser is Firefox and user just says "Not now"
          if (failCallBack !== null) {
            failCallBack(error.message);
          }
        },
        {
          enableHighAccuracy: false,
          timeout: timeout,
          maximumAge: 5000,
        }
      );
    } else {
      // Browser doesn't support Geolocation
      if (failCallBack !== null) {
        failCallBack();
      }
    }
  },

  /**
   * Open station information dialog
   * @param {int} stationId
   * @return null
   */
  openStationInformationDialog: function (stationId) {
    var packet = this._map.markerCollection.getStationLatestPacket(stationId);
    if (packet == null) {
      packet = { station_id: stationId, id: null };
    }

    // Ask listener to open dialog
    this._emitEventListeners("station-name-clicked", packet);
  },

  /**
   * Open marker info window
   * @param {int} markerId
   * @return None
   */
  openMarkerInfoWindow: function (markerId) {
    var markerIdKey = this._map.markerCollection.getMarkerIdKey(markerId);
    if (this._map.markerCollection.isExistingMarker(markerIdKey)) {
      var marker = this._map.markerCollection.getMarker(markerIdKey);
      this._map.openMarkerInfoWindow(marker);
    }
  },

  /**
   * Close any open info window
   * @return None
   */
  closeAnyOpenInfoWindow: function () {
    if (this._map !== null) {
      var state = this._map.state;
      if (state.isInfoWindowOpen()) {
        state.openInfoWindow.hide();
      }
    }
  },

  /**
   * Set timetravel timestamp
   * @param {int} ts
   * @param {boolean} sendRequestToServer
   * @return null
   */
  setTimeTravelTimestamp: function (ts, sendRequestToServer) {
    if (ts != 0 || this._map.state.endTimeTravelTimestamp != null) {
      sendRequestToServer =
        typeof sendRequestToServer !== "undefined" ? sendRequestToServer : true;

      if (this._map.state.endTimeTravelTimestamp != ts) {
        if (ts != null && ts != 0 && ts != "") {
          this._map.state.endTimeTravelTimestamp = ts;
        } else {
          this._map.state.endTimeTravelTimestamp = null;
        }

        if (sendRequestToServer) {
          trackdirect.services.callbackExecutor.add(
            this,
            this._handleTimeChange,
            []
          );
        }
      }

      this._emitEventListeners("time-travel-changed", ts);
      this._emitEventListeners("mode-changed");
    }
  },

  /**
   * Returns the time travel timestamp currently used
   * @return {int}
   */
  getTimeTravelTimestamp: function () {
    return this._map.state.endTimeTravelTimestamp;
  },

  /**
   * Set time in minutes
   * @param {int} time
   * @param {boolean} sendRequestToServer
   */
  setTimeLength: function (time, sendRequestToServer) {
    sendRequestToServer =
      typeof sendRequestToServer !== "undefined" ? sendRequestToServer : true;

    if (this._map.state.getTimeLength() / 60 != time) {
      this._map.state.setTimeLength(time * 60);

      if (sendRequestToServer) {
        trackdirect.services.callbackExecutor.add(
          this,
          this._handleTimeChange,
          []
        );
      }
    }

    this._emitEventListeners("time-length-changed", time);
    this._updateMinZoomLevels();
  },

  /**
   * Toggle PHG circles
   * @return None
   */
  togglePHGCircles: function () {
    var state = this._map.state;
    if (state.showPHGCircles == 0) {
      state.showPHGCircles = 1;
    } else if (state.showPHGCircles == 1) {
      state.showPHGCircles = 2;
    } else {
      state.showPHGCircles = 0;
    }
    this._map.showHidePHGCircles();
  },

  /**
   * Toggle PHG circles
   * @return None
   */
  toggleRNGCircles: function () {
    var state = this._map.state;
    if (state.showRNGCircles == 0) {
      state.showRNGCircles = 1;
    } else if (state.showRNGCircles == 1) {
      state.showRNGCircles = 2;
    } else {
      state.showRNGCircles = 0;
    }
    this._map.showHideRNGCircles();
  },

  /**
   * Toggle Stationary positions
   * @return None
   */
  toggleStationaryPositions: function () {
    if (this.isStationaryMarkersVisible()) {
      this._map.state.isStationaryMarkersVisible = false;
    } else {
      this._map.state.isStationaryMarkersVisible = true;
    }
    this._map.showHideMarkers();
  },

  /**
   * Toggle Unknown positions
   * @return None
   */
  toggleUnknownPositions: function () {
    if (this.isUnknownMarkersVisible()) {
      this._map.state.isUnknownMarkersVisible = false;
    } else {
      this._map.state.isUnknownMarkersVisible = true;
    }
    this._map.showHideMarkers();
  },

  /**
   * Toggle Ogflym positions
   * @return None
   */
  toggleOgflymPositions: function () {
    if (this.isOgflymMarkersVisible()) {
      this._map.state.isOgflymMarkersVisible = false;
    } else {
      this._map.state.isOgflymMarkersVisible = true;
    }
    this._map.showHideMarkers();
  },

  /**
   * Toggle Stationary positions
   * @return None
   */
  toggleInternetPositions: function () {
    if (this.isInternetMarkersVisible()) {
      this._map.state.isInternetMarkersVisible = false;
    } else {
      this._map.state.isInternetMarkersVisible = true;
    }
    this._map.showHideMarkers();
  },

  /**
   * Toggle the CWOP positions option
   * @return None
   */
  toggleCwopPositions: function () {
    if (this.isCwopMarkersVisible()) {
      this._map.state.isCwopMarkersVisible = false;
    } else {
      this._map.state.isCwopMarkersVisible = true;
    }
    this._map.showHideMarkers();
  },

  /**
   * Toggle the ghost positions option
   * Ghost positions are positions that some filter has removed since it is unlikly
   * @return None
   */
  toggleGhostPositions: function () {
    if (this.isGhostMarkersVisible()) {
      this._map.state.isGhostMarkersVisible = false;
    } else {
      this._map.state.isGhostMarkersVisible = true;
    }
    this._map.showHideMarkers();
  },

  /**
   * Returns true if ghost markers is visible
   * @return {boolean}
   */
  isGhostMarkersVisible: function () {
    return this._map.state.isGhostMarkersVisible;
  },

  /**
   * Returns true if CWOP markers is visible
   * @return {boolean}
   */
  isCwopMarkersVisible: function () {
    return this._map.state.isCwopMarkersVisible;
  },

  /**
   * Returns true if INTERNET markers is visible
   * @return {boolean}
   */
  isInternetMarkersVisible: function () {
    return this._map.state.isInternetMarkersVisible;
  },

  /**
   * Returns true if stationary markers is visible
   * @return {boolean}
   */
  isStationaryMarkersVisible: function () {
    return this._map.state.isStationaryMarkersVisible;
  },

  /**
   * Set visible symbols, argument should be an array of two value arrays (first value should be the ascii value for the symbol code and the second should be the ascii value for the symbol table)
   * @param {array} symbols
   * @return None
   */
  setVisibleSymbols: function (symbols) {
    this._map.state.visibleSymbols = symbols;
    this._map.showHideMarkers();
  },

  /**
   * Add visible symbol, argument should be a two value array (first value should be the ascii value for the symbol code and the second should be the ascii value for the symbol table)
   * @param {array} symbols
   * @return None
   */
  addVisibleSymbol: function (symbol) {
    this._map.state.visibleSymbols.push(symbol);
    this._map.showHideMarkers();
  },

  /**
   * Remove visible symbol, argument should be a two value array (first value should be the ascii value for the symbol code and the second should be the ascii value for the symbol table)
   * @param {array} symbols
   * @return None
   */
  removeVisibleSymbol: function (symbol) {
    var indexToRemove = null;
    for (var i = 0; i < this._map.state.visibleSymbols.length; i++) {
      if (
        this._map.state.visibleSymbols[i][0] == symbol[0] &&
        this._map.state.visibleSymbols[i][1] == symbol[1]
      ) {
        indexToRemove = i;
        break;
      }
    }
    if (indexToRemove !== null) {
      this._map.state.visibleSymbols.splice(indexToRemove, 1);
    }
    this._map.showHideMarkers();
  },

  /**
   * Returns array of visible symbols
   * @return {array}
   */
  getVisibleSymbols: function () {
    return this._map.state.visibleSymbols;
  },

  /**
   * Returns true if unknown markers is visible
   * @return {boolean}
   */
  isUnknownMarkersVisible: function () {
    return this._map.state.isUnknownMarkersVisible;
  },

  /**
   * Returns true if ogflym markers is visible
   * @return {boolean}
   */
  isOgflymMarkersVisible: function () {
    return this._map.state.isOgflymMarkersVisible;
  },

  /**
   * Handle filter station request
   * @param {int} stationId
   * @param {string} linkElementId
   * @return {boolean}
   */
  handleFilterStationRequest: function (stationId, filterLinkElementClass) {
    filterLinkElementClass =
      typeof filterLinkElementClass !== "undefined"
        ? filterLinkElementClass
        : null;
    if (
      this._map.state.filterStationIds.length > 0 &&
      this._map.state.filterStationIds.indexOf(stationId) > -1
    ) {
      // We want to stop filtering
      this.stopFilterOnStationId(stationId);
      if (filterLinkElementClass !== null) {
        $("." + filterLinkElementClass).html("Filter");
      }
    } else {
      this.filterOnStationId(stationId);
      if (filterLinkElementClass !== null) {
        $("." + filterLinkElementClass).html("Unfilter");
      }
    }
  },

  /**
   * Handle track station request
   * @param {int} stationId
   * @param {string} trackLinkElementClass
   * @return null
   */
  handleTrackStationRequest: function (stationId, trackLinkElementClass) {
    stationId = typeof stationId !== "undefined" ? stationId : 0;
    trackLinkElementClass =
      typeof trackLinkElementClass !== "undefined"
        ? trackLinkElementClass
        : null;

    if (
      this._map.state.getTrackStationId() !== null &&
      (stationId === 0 || this._map.state.getTrackStationId() == stationId)
    ) {
      // We want to stop tracking
      if (trackLinkElementClass !== null) {
        $("." + trackLinkElementClass).html("Track");
      } else if (this._map.state.openInfoWindow !== null) {
        this._map.state.openInfoWindow.hide();
      }
      this.stopTrackStation();
    } else if (stationId !== 0) {
      if (trackLinkElementClass !== null) {
        $("." + trackLinkElementClass).html("Untrack");
      }

      var packet = this._map.markerCollection.getStationLatestPacket(stationId);
      if (packet !== null) {
        var stationName = packet.station_name;
        if (packet.sender_name != packet.station_name) {
          stationName = packet.station_name + " (" + packet.sender_name + ")";
        }
        this.trackStation(stationId, stationName, true);
      }
    }
  },

  /**
   * Init settings
   * @return null
   */
  _initSettings: function () {
    this.settings = {
      animate: true,

      defaultMinZoomForMarkerLabel: 11,
      defaultMinZoomForMarkerPrevPosition: 11,
      defaultMinZoomForMarkerTail: 9,
      defaultMinZoomForMarkers: 8,

      minZoomForMarkerLabel: 11,
      minZoomForMarkerPrevPosition: 11,
      minZoomForMarkerTail: 9,
      minZoomForMarkers: 8,

      markerSymbolBaseDir: "/symbols/",
      imagesBaseDir: "/images/",

      defaultCurrentZoom: 11,
      defaultCurrentZoomMobile: 11,

      dateFormat: "L LTSZ",
      dateFormatNoTimeZone: "L LTS",

      host: "www.aprsdirect.com",
      baseUrl: "https://www.aprsdirect.com",

      defaultTimeLength: 60,

      symbolsToScale: [],

      // Contains ascii values that corresponds to symbols without support for direction polyline (for symbols in the primary table)
      primarySymbolWithNoDirectionPolyline: [87, 64, 95],

      // Contains ascii values that corresponds to symbols without support for direction polyline (for symbols in the alterantive table)
      alternativeSymbolWithNoDirectionPolyline: [
        40, 42, 64, 74, 84, 85, 96, 98, 101, 102, 112, 116, 119, 121, 123,
      ],
    };
  },

  /**
   * Parse the options
   * @param {object} options
   */
  _parseOptions: function (options) {
    if (typeof options["cordinatesContainerElementId"] !== undefined) {
      this._cordinatesContainerElementId =
        options["cordinatesContainerElementId"];
    }
    if (typeof options["statusContainerElementId"] !== undefined) {
      this._statusContainerElementId = options["statusContainerElementId"];
    }
    if (typeof options["isMobile"] !== undefined) {
      this.isMobile = options["isMobile"];
    }
    if (typeof options["coverageDataUrl"] !== undefined) {
      this.coverageDataUrl = options["coverageDataUrl"];
    }
    if (typeof options["coveragePercentile"] !== undefined) {
      this.coveragePercentile = options["coveragePercentile"];
    }
    if (typeof options["time"] !== undefined) {
      this._time = options["time"];
    }
    if (typeof options["timetravel"] !== undefined) {
      this._timetravel = options["timetravel"];
    }
    if (typeof options["center"] !== undefined) {
      this._center = options["center"];
    }
    if (typeof options["zoom"] !== undefined) {
      this._zoom = options["zoom"];
    }
    if (typeof options["maptype"] !== undefined) {
      this._maptype = options["maptype"];
    }
    if (typeof options["mid"] !== undefined) {
      this._mid = options["mid"];
    }
    if (
      typeof options["filters"] !== undefined &&
      options["filters"] !== null
    ) {
      for (var i in options["filters"]) {
        if (options["filters"][i] !== null && options["filters"][i] != "") {
          this._filters[i] = options["filters"][i];
        }
      }
    }
    if (
      typeof options["disableLocationChangeOnFilterResponse"] !== undefined &&
      options["disableLocationChangeOnFilterResponse"]
    ) {
      this._doNotChangeLocationOnFilterResponse = true;
    }
    if (
      typeof options["defaultMinZoomForMarkerLabel"] !== undefined &&
      options["defaultMinZoomForMarkerLabel"] != null
    ) {
      this.settings.defaultMinZoomForMarkerLabel =
        options["defaultMinZoomForMarkerLabel"];
    }
    if (
      typeof options["defaultMinZoomForMarkerPrevPosition"] !== undefined &&
      options["defaultMinZoomForMarkerPrevPosition"] != null
    ) {
      this.settings.defaultMinZoomForMarkerPrevPosition =
        options["defaultMinZoomForMarkerPrevPosition"];
    }
    if (
      typeof options["defaultMinZoomForMarkerTail"] !== undefined &&
      options["defaultMinZoomForMarkerTail"] != null
    ) {
      this.settings.defaultMinZoomForMarkerTail =
        options["defaultMinZoomForMarkerTail"];
    }
    if (
      typeof options["defaultMinZoomForMarkers"] !== undefined &&
      options["defaultMinZoomForMarkers"] != null
    ) {
      this.settings.defaultMinZoomForMarkers =
        options["defaultMinZoomForMarkers"];
    }

    if (typeof options["animate"] !== undefined && options["animate"] != null) {
      this.settings.animate = options["animate"];
    }

    if (typeof options["host"] !== undefined && options["host"] != null) {
      this.settings.host = options["host"];
      this.settings.baseUrl = this._getMapBaseUrl(options["host"]);
    } else {
      this.settings.baseUrl = this._getMapBaseUrl();
    }

    if (
      typeof options["defaultTimeLength"] !== undefined &&
      options["defaultTimeLength"] != null
    ) {
      this.settings.defaultTimeLength = options["defaultTimeLength"];
    }

    if (
      typeof options["symbolsToScale"] !== undefined &&
      options["symbolsToScale"] !== null
    ) {
      this.settings.symbolsToScale = options["symbolsToScale"];
    }

    this._initDefaultLocation(options);
  },

  /**
   * Initialize default location
   * @param {object} options
   */
  _initDefaultLocation: function (options) {
    if (
      typeof options["defaultLatitude"] !== "undefined" &&
      typeof options["defaultLongitude"] !== "undefined"
    ) {
      this._defaultLatitude = options["defaultLatitude"];
      this._defaultLongitude = options["defaultLongitude"];
    } else {
      this._defaultLatitude = 0;
      this._defaultLongitude = 0;
    }
  },

  /**
   * Init time
   * @return null
   */
  _initTime: function () {
    var filterMode = false;
    if (
      "sid" in this._filters ||
      "sidlist" in this._filters ||
      "sname" in this._filters ||
      "snamelist" in this._filters
    ) {
      filterMode = true;
    }

    if (this._time != null && this._isValidTime(this._time, filterMode)) {
      this.setTimeLength(this._time, false);
    } else {
      this.setTimeLength(this.settings.defaultTimeLength, false);
    }

    now = new Date();
    if (
      this._timetravel != null &&
      this._timetravel >= 0 &&
      this._timetravel <= now.getTime() / 1000
    ) {
      this.setTimeTravelTimestamp(this._timetravel, false);
    }

    this._updateMinZoomLevels();
  },

  /**
   * Init map
   * @param {object} options
   * @return null
   */
  _mapInit: function (options) {
    if (
      "sid" in this._filters ||
      "sidlist" in this._filters ||
      "sname" in this._filters ||
      "snamelist" in this._filters
    ) {
      // To avoid flicker we wait with sending feed requests until we get the filter response
      this._waitForFilterResponse = true;
      if (window.location.href.indexOf("/center/") >= 0) {
        this._doNotChangeLocationOnFilterResponseTmp = true;
      }
    }

    var tdMapOptions = this._getMapInitOptions(options);
    var me = this;

    $(document).ready(function () {
      me._map = new trackdirect.models.Map(me._mapElementId, tdMapOptions);
      me._markerCreator = new trackdirect.MarkerCreator(me._map);

      if (
        typeof options["useImperialUnit"] !== "undefined" &&
        options["useImperialUnit"] == true
      ) {
        me.enableImperialUnits();
      }

      me._emitEventListeners("map-created");
    });
  },

  /**
   * Returns the map init options
   * @param {array} options
   * @return string
   */
  _getMapInitOptions: function (options) {
    var center = this._getMapInitCenter();
    var tdMapOptions = {
      zoom: this._getMapInitZoom(),
      maptype: this._getMapInitMapType(),
      cordinatesContainer: this._cordinatesContainerElementId,
      defaultLatitude: this._defaultLatitude,
      defaultLongitude: this._defaultLongitude,
      initCenter: center,
      mid: this._getMapInitMid(),
    };

    if ("supportedMapTypes" in options) {
      tdMapOptions["supportedMapTypes"] = options["supportedMapTypes"];
    }

    if ("mapboxGLStyle" in options) {
      tdMapOptions["mapboxGLStyle"] = options["mapboxGLStyle"];
    }

    if ("mapboxGLAccessToken" in options) {
      tdMapOptions["mapboxGLAccessToken"] = options["mapboxGLAccessToken"];
    }

    if ("mapboxGLAttribution" in options) {
      tdMapOptions["mapboxGLAttribution"] = options["mapboxGLAttribution"];
    }

    return tdMapOptions;
  },

  /**
   * Returns the map init center
   * @return string
   */
  _getMapInitCenter: function () {
    if (this._center != null) {
      var centerParts = this._center.split(",");
      if (
        centerParts.length == 2 &&
        this._isValidLatitude(centerParts[0]) &&
        this._isValidLongitude(centerParts[1])
      ) {
        return {
          lat: parseFloat(centerParts[0]),
          lng: parseFloat(centerParts[1]),
        };
      }
    }
    return null;
  },

  /**
   * Returns the map init zoom
   * @return string
   */
  _getMapInitZoom: function () {
    var zoom = null;
    if (this._zoom != null && this._isValidZoom(this._zoom)) {
      zoom = this._zoom;
    }
    return zoom;
  },

  /**
   * Returns the map init mid value
   * @return string
   */
  _getMapInitMid: function () {
    var mid = null;
    if (this._mid != null) {
      mid = this._mid;
    }
    return mid;
  },

  /**
   * Returns the map init map type
   * @return string
   */
  _getMapInitMapType: function () {
    var maptype = null;
    if (this._maptype != null) {
      maptype = this._maptype;
    }
    return maptype;
  },

  /**
   * Init filter url request, returnes true if filter request is sent otherwise false
   * @return boolean
   */
  _initFilterUrlRequest: function () {
    if ("sid" in this._filters) {
      stationId = this._filters["sid"];
      if (isNumeric(stationId)) {
        this.filterOnStationId(stationId);
      }
    } else if ("sname" in this._filters) {
      stationName = this._filters["sname"];
      if (stationName != "") {
        this.filterOnStationName(stationName);
      }
    } else if ("sidlist" in this._filters) {
      stationIdArray = this._filters["sidlist"].split(",");
      var isValid = true;
      for (var i = 0; i < stationIdArray.length; i++) {
        if (!isNumeric(stationIdArray[i])) {
          isValid = false;
        }
      }
      if (isValid) {
        this.filterOnStationId(stationIdArray);
      }
    } else if ("snamelist" in this._filters) {
      stationNameArray = this._filters["snamelist"].split(",");
      var isValid = true;
      for (var i = 0; i < stationNameArray.length; i++) {
        if (
          typeof stationNameArray[i] == "undefined" ||
          stationNameArray[i] == ""
        ) {
          isValid = false;
        }
      }
      if (isValid) {
        this.filterOnStationName(stationNameArray);
      }
    } else {
      return false;
    }

    // This timeout is just to be safe, if we get a bad station request we should at least show regular aprs data after a while
    var me = this;
    this._filterTimeoutId = window.setTimeout(function () {
      // Remember to clear _filterTimeoutId and _waitForFilterResponse when we have received a filter response
      if (me._waitForFilterResponse) {
        // We give up, we have not received any filter response, ask for everything instead
        me._waitForFilterResponse = false;
        trackdirect.services.callbackExecutor.add(
          me,
          me._sendPositionRequest,
          []
        );
      }
    }, 5000);

    return true;
  },

  /**
   * Returns true if parameter is a valid zoom
   * @param {int} time
   * @param {boolean} filteredMode
   * @return {boolean}
   */
  _isValidTime: function (time, filteredMode) {
    if (isNumeric(time)) {
      if (filteredMode && time <= 14400 && time > 0) {
        return true;
      } else if (filteredMode == false && time <= 1440 && time > 0) {
        return true;
      }
    }
    return false;
  },

  /**
   * Returns true if parameter is a valid zoom
   * @param {int} zoom
   * @return {boolean}
   */
  _isValidZoom: function (zoom) {
    if (isNumeric(zoom)) {
      if (zoom <= 21 && zoom >= 0) {
        return true;
      }
    }
    return false;
  },

  /**
   * Returns true if parameter is a valid latitude
   * @param {object} lat
   * @return {boolean}
   */
  _isValidLatitude: function (lat) {
    if (isNumeric(lat)) {
      if (lat <= 90 && lat >= -90) {
        return true;
      }
    }
    return false;
  },

  /**
   * Returns true if parameter is a valid longitude
   * @param {object} lng
   * @return {boolean}
   */
  _isValidLongitude: function (lng) {
    if (isNumeric(lng)) {
      if (lng <= 180 && lng >= -180) {
        return true;
      }
    }
    return false;
  },

  /**
   * Initializes the map listeners
   * @return null
   */
  _initMapListeners: function () {
    var me = this;
    this._map.addTdListener("change", function () {
      trackdirect.services.callbackExecutor.add(
        me,
        me._sendPositionRequest,
        []
      );
      trackdirect.services.mapAttributionModifier.update(me._map);
    });
    this._map.addTdListener("moving", function () {
      // This event will happen many times, but same message will never be sent twice (handled by both ws-part and queue)
      trackdirect.services.callbackExecutor.addIfUnique(
        me,
        me._sendIdleRequest,
        []
      );
    });
    this._map.addTdListener("station-tail-needed", function (stationId) {
      me._websocket.doSendCompleteStationRequest(
        stationId,
        me._map.state.getTimeLength() / 60,
        me.getTimeTravelTimestamp()
      );
    });
    this._map.addTdListener("station-information", function (stationId) {
      me.openStationInformationDialog(stationId);
    });
  },

  /**
   * Initializes the websocket listeners
   * @return null
   */
  _initWebsocketListeners: function () {
    this._initWebsocketStateChangeListener();
    this._initWebsocketAprsPacketListener();
    this._initWebsocketPayloadDoneListener();
    this._initWebsocketFilterResponseListener();
    this._initWebsocketServerTimestampResponseListener();
    this._initWebsocketResetListener();
  },

  /**
   * Initializes websocket state change listener
   * @return null
   */
  _initWebsocketStateChangeListener: function () {
    var me = this;
    this._websocket.addListener("state-change", function () {
      var callback = function () {
        me._handleWebsocketStateChange();
      };
      trackdirect.services.callbackExecutor.add(this, callback, []);
    });
  },

  /**
   * Initializes websocket new aprs packet listener
   * @return null
   */
  _initWebsocketAprsPacketListener: function () {
    var me = this;
    this._websocket.addListener("aprs-packet", function (packetData) {
      var packet = new trackdirect.models.Packet(packetData);

      var queueTimestamp = Math.floor(Date.now() / 1000);
      var callback = function () {
        var dequeueTimestamp = Math.floor(Date.now() / 1000);
        if (dequeueTimestamp - queueTimestamp > 5 || !this.settings.animate) {
          // More than 5 seconds has passed since queued or we do not want to animate
          me._handleAprsPacket(packet, false);
        } else {
          me._handleAprsPacket(packet, true);
        }
      };
      trackdirect.services.callbackExecutor.add(me, callback, []);
    });
  },

  /**
   * Initializes websocket payload done listener
   * @return null
   */
  _initWebsocketPayloadDoneListener: function () {
    var me = this;
    this._websocket.addListener("aprs-packet-payload-done", function () {
      var callback = function () {
        me._map.showNewMarkersInQueue(true);
      };
      trackdirect.services.callbackExecutor.add(this, callback, []);
    });
  },

  /**
   * Initializes websocket filter response listener
   * @return null
   */
  _initWebsocketFilterResponseListener: function () {
    var me = this;
    this._websocket.addListener("filter-response", function (data) {
      var callback = function () {
        me._handleFilterResponse(data);
      };
      trackdirect.services.callbackExecutor.add(this, callback, []);
    });
  },

  /**
   * Initializes websocket server timestamp response listener
   * @return null
   */
  _initWebsocketServerTimestampResponseListener: function () {
    var me = this;
    this._websocket.addListener("server-timestamp-response", function (data) {
      var callback = function () {
        me._map.state.setServerCurrentTimestamp(data.timestamp);
      };
      trackdirect.services.callbackExecutor.add(this, callback, []);

      // Just make sure we have not forgotten any markers in queue (should not be needed, but just to be safe)
      if (me._map.getNumberOfNewMarkersToShow() > 0) {
        var callback2 = function () {
          me._map.showNewMarkersInQueue(true);
        };
        trackdirect.services.callbackExecutor.addIfUnique(this, callback2, []);
      }
    });
  },

  /**
   * Initializes websocket reset listener
   * @return null
   */
  _initWebsocketResetListener: function () {
    var me = this;
    this._websocket.addListener("reset", function () {
      // Important that everything happens in order!!!
      trackdirect.services.callbackExecutor.add(
        me._map,
        me._map.resetAllMarkers,
        []
      );
    });
  },

  /**
   * Update min zoom level based on time settings
   * @return null
   */
  _updateMinZoomLevels: function () {
    if (this._map.state.getTimeLength() / 60 > 720) {
      trackdirect.settings.minZoomForMarkerPrevPosition =
        trackdirect.settings.defaultMinZoomForMarkerPrevPosition + 1;
      trackdirect.settings.minZoomForMarkerTail =
        trackdirect.settings.defaultMinZoomForMarkerTail + 1;
      trackdirect.settings.minZoomForMarkerLabel =
        trackdirect.settings.defaultMinZoomForMarkerLabel + 1;
      trackdirect.settings.minZoomForMarkers =
        trackdirect.settings.defaultMinZoomForMarkers;
    } else {
      trackdirect.settings.minZoomForMarkerPrevPosition =
        trackdirect.settings.defaultMinZoomForMarkerPrevPosition;
      trackdirect.settings.minZoomForMarkerTail =
        trackdirect.settings.defaultMinZoomForMarkerTail;
      trackdirect.settings.minZoomForMarkerLabel =
        trackdirect.settings.defaultMinZoomForMarkerLabel;
      trackdirect.settings.minZoomForMarkers =
        trackdirect.settings.defaultMinZoomForMarkers;
    }
  },

  /**
   * Handle time change request
   * @return null
   */
  _handleTimeChange: function () {
    this._updateMinZoomLevels();

    // A reset request will soon be sent by server, but if server takes time we do it now also so user will notice that something happens
    this._map.resetAllMarkers();

    this._websocket.clearLastSentPositionRequest();
    trackdirect.services.callbackExecutor.add(
      this,
      this._sendPositionRequest,
      []
    );
    this._emitEventListeners("mode-changed");
  },

  /**
   * Handle filter response
   * @param {array} data
   * @return null
   */
  _handleFilterResponse: function (data) {
    // We have received a filter response, reset timeout and stop waiting for response
    if (this._filterTimeoutId !== null) {
      clearTimeout(this._filterTimeoutId);
      this._filterTimeoutId = null;
    }

    if (data.length == 0) {
      this._handleEmptyFilterResponse();
    } else {
      this._handleNonEmptyFilterResponse(data);
    }
  },

  /**
   * Unmark all stations as filtered that has no packet in the specified array
   * @param {array} data
   * @return null
   */
  _unMarkMissingStationsAsFiltered: function (data) {
    var filterStationIds = this._map.state.getFilterStationIds();
    for (var key in filterStationIds) {
      var stationId = filterStationIds[key];
      var foundStation = false;
      for (var i = 0; i < data.length; i++) {
        var packetData = data[i];
        if (packetData.station_id == stationId && packetData["related"] == 0) {
          foundStation = true;
        }
      }
      if (!foundStation) {
        this._unMarkStationAsFiltered(stationId);
      }
    }
  },

  /**
   * Unmark station as a station that we are filtering on
   * @param {int} stationId
   * @return None
   */
  _unMarkStationAsFiltered: function (stationId) {
    var map = this._map;
    var index = map.state.filterStationIds.indexOf(stationId);
    if (index > -1) {
      map.state.filterStationIds.splice(index, 1);

      // If we for some reason have infoWindow open and doesn't close it, update link name
      var filterLinkElementClass = "filterStationLink" + stationId;
      $("." + filterLinkElementClass).html("Filter");

      // We only hide the marker since it may exist in a station transmit event
      for (var markerIdKey in map.markerCollection.getStationMarkerIdKeys(
        stationId
      )) {
        var marker = this._map.markerCollection.getMarker(markerIdKey);
        if (marker !== null) {
          marker.hideCompleteMarker();
        }
      }
    }
  },

  /**
   * Returns the number of uniqe stations in array (excluding packets marked as related)
   * @param {array} data
   * @return int
   */
  _getNumberOfUniqeStationsInArray: function (data) {
    var numberOfStationPackets = 0;
    for (var i = 0; i < data.length; i++) {
      var packetData = data[i];
      if (packetData["related"] == 0) {
        numberOfStationPackets++;
      }
    }
    return numberOfStationPackets;
  },

  /**
   * Track station in packet array (only if only one uniqe station exists)
   * @param {array} data
   * @param {boolean} onlyTrackRecentPackets
   * @return null
   */
  _trackStationInArray: function (data, onlyTrackRecentPackets) {
    if (this._getNumberOfUniqeStationsInArray(data) == 1) {
      for (var i = 0; i < data.length; i++) {
        var packet = new trackdirect.models.Packet(data[i]);
        if (packet["related"] == 0) {
          // If we filter on only one station, track it
          this.trackStation(
            packet.station_id,
            escapeHtml(packet.getStationName()),
            false,
            onlyTrackRecentPackets
          );
        }
      }
    }
  },

  /**
   * Add a packet from a filter response
   * @param {array} data
   * @return null
   */
  _addFilterResponsePacketsToMap: function (data) {
    // We add packet to map if it is so old that it will not be replaced by a newPositionRequest or if we will not call a newPositionRequest (if info window is open)
    var tryToShowPacket = this._isAnyPacketInArrayOlderThanCurrentLimit(data);
    for (var i = 0; i < data.length; i++) {
      var packet = new trackdirect.models.Packet(data[i]);
      if (packet["related"] == 0) {
        this._markStationAsFiltered(packet.station_id);
      }

      // This may look unnessecery since we will add it later again (by calling doSendNewPositionRequest),
      // but if latest packet is old it may not be received any more, so don't remove the following calls...
      var markerIdKey = this._markerCreator.addPacket(packet, tryToShowPacket);
      var marker = this._map.markerCollection.getMarker(markerIdKey);
      if (marker !== null) {
        marker.markToBeOverWritten();
      }
    }
  },

  /**
   * Mark station as a station that we are filtering on
   * @param {int} stationId
   * @return None
   */
  _markStationAsFiltered: function (stationId) {
    var map = this._map;
    if (map.state.filterStationIds.indexOf(stationId) == -1) {
      map.state.filterStationIds.push(stationId);
    }

    // If we for some reason have infoWindow open and doesn't close it, update link name
    var filterLinkElementClass = "filterStationLink" + stationId;
    $("." + filterLinkElementClass).html("Unfilter");

    // If we allready have markers for this station we should show them
    for (var markerIdKey in map.markerCollection.getStationMarkerIdKeys(
      stationId
    )) {
      var marker = this._map.markerCollection.getMarker(markerIdKey);
      if (marker !== null) {
        marker.showCompleteMarker();
      }
    }
  },

  /**
   * Handle non empty filter response
   * @param {array} data
   * @return null
   */
  _handleNonEmptyFilterResponse: function (data) {
    var isFilterModeNew = !this.isFilteredMode();
    this._map.activateFilteredMode();
    this._waitForFilterResponse = false;

    if (isFilterModeNew) {
      this._map.resetAllMarkers();

      this._emitEventListeners("mode-changed");
    } else {
      this._unMarkMissingStationsAsFiltered(data);
    }

    this._addFilterResponsePacketsToMap(data);

    var packets = [];
    for (var i = 0; i < data.length; i++) {
      packets.push(new trackdirect.models.Packet(data[i]));
    }
    this._emitEventListeners("filter-changed", packets);

    if (isFilterModeNew) {
      var onlyTrackRecentPackets = true;
      if (
        !this._doNotChangeLocationOnFilterResponse &&
        !this._doNotChangeLocationOnFilterResponseTmp
      ) {
        onlyTrackRecentPackets = false;
        this._setFilteredMapBounds(data);
      }
      this._doNotChangeLocationOnFilterResponseTmp = false;
      this._trackStationInArray(data, onlyTrackRecentPackets);
      this._emitEventListeners("filter-new");
    }
    trackdirect.services.callbackExecutor.add(
      this,
      this._requestFilteredUpdate,
      []
    );
  },

  /**
   * Request filtered update from server
   * @return null
   */
  _requestFilteredUpdate: function () {
    // request update from server (request is filtered), but if information dialog is open we wait until it closes
    this._websocket.clearLastSentPositionRequest();
    this._setWebsocketStateLoading(false);
    this._websocket.doSendNewPositionRequest(
      90,
      180,
      -90,
      -180,
      this._map.state.getTimeLength() / 60,
      this.getTimeTravelTimestamp(),
      false
    );
  },

  /**
   * Handle empty filter response
   * @param {array} data
   * @return null
   */
  _handleEmptyFilterResponse: function () {
    // Response indicate that user are not demanding anything, we will reset and restart everything
    this._deactivateFiltered(true);
    this._waitForFilterResponse = false;
  },

  /**
   * Returns true if any packet in array is older than current timelimit
   * @param {array} data
   * @return {boolean}
   */
  _isAnyPacketInArrayOlderThanCurrentLimit: function (data) {
    for (var i = 0; i < data.length; i++) {
      var packetData = data[i];
      if (packetData["related"] == 0) {
        // The 60 seconds is just a marginal
        if (packetData.timestamp < packetData.requested_timestamp + 60) {
          return true;
        }

        if (packetData["source"] == 0 || packetData["source_id"] == 0) {
          // packet seems to be simulated, we better treat it as a very old packet
          return true;
        }
      }
    }
    return false;
  },

  /**
   * Set map bounds after receiving a filter response
   * @param {array} data
   * @return {int}
   */
  _setFilteredMapBounds: function (data) {
    if (data.length == 1) {
      this._map.setCenter(
        {
          lat: parseFloat(data[0].latitude),
          lng: parseFloat(data[0].longitude),
        },
        12
      );
    } else {
      var positions = [];
      for (var i = 0; i < data.length; i++) {
        var packetData = data[i];
        if (packetData["related"] == 0) {
          positions.push({
            lat: parseFloat(packetData.latitude),
            lng: parseFloat(packetData.longitude),
          });
        }
      }

      this._map.fitBounds(positions);
      if (this._map.getZoom() > 12) {
        this._map.setZoom(12);
      }
    }
  },

  /**
   * Handle a received APRS packet!
   * @param {trackdirect.models.Packet} packet
   * @param {boolean} animate
   * @return null
   */
  _handleAprsPacket: function (packet, animate) {
    var markerIdKey = this._markerCreator.addPacket(packet, true);
    if (markerIdKey !== null) {
      var highlight = false;
      var autoRender = false;
      var marker = this._map.markerCollection.getMarker(markerIdKey);
      if (
        animate &&
        packet.db == 0 &&
        packet.station_name == packet.sender_name &&
        marker.shouldMarkerBeVisible() &&
        (this.isFilteredMode() || this._isPacketOnMap(packet))
      ) {
        highlight = true;

        var tdTransmitAnimation = new trackdirect.models.TransmitAnimation(
          marker,
          this._map
        );
        tdTransmitAnimation.show();
      }

      if (packet.realtime == 1 && animate) {
        autoRender = true;
      }
    }
  },

  /**
   * Returns linkified packet.raw
   * @param {trackdirect.models.Packet} packet
   * @return {string}
   */
  _linkifyPacketRaw: function (packet) {
    if (typeof packet.raw !== "undefined" && typeof packet.raw == "string") {
      var raw = escapeHtml(packet.raw);
      var stationNameReplacement =
        '<a href="#" onclick="trackdirect.focusOnMarkerId(' +
        packet.marker_id +
        '); return false;">' +
        escapeHtml(packet.sender_name) +
        "</a>";
      raw = raw.replaceAll(
        escapeHtml(packet.sender_name) + "&gt;",
        stationNameReplacement + "&gt;"
      );

      for (var i = 0; i < packet.station_id_path.length; i++) {
        var relatedStationId = packet.station_id_path[i];
        var relatedStationLatestPacket =
          this._map.markerCollection.getStationLatestPacket(relatedStationId);
        if (relatedStationLatestPacket !== null) {
          var relatedStationNameReplacement =
            '<a href="#" onclick="trackdirect.focusOnStation(' +
            relatedStationId +
            ', true); return false;">' +
            escapeHtml(relatedStationLatestPacket.sender_name) +
            "</a>";

          var relatedStationSenderName = escapeHtml(
            relatedStationLatestPacket.sender_name
          );
          raw = raw.replaceAll(
            "&gt;" + relatedStationSenderName + ":",
            "&gt;" + relatedStationNameReplacement + ":"
          );
          raw = raw.replaceAll(
            "&gt;" + relatedStationSenderName + ",",
            "&gt;" + relatedStationNameReplacement + ","
          );
          raw = raw.replaceAll(
            "&gt;" + relatedStationSenderName + "*",
            "&gt;" + relatedStationNameReplacement + "*"
          );

          raw = raw.replaceAll(
            "," + relatedStationSenderName + ":",
            "," + relatedStationNameReplacement + ":"
          );
          raw = raw.replaceAll(
            "," + relatedStationSenderName + ",",
            "," + relatedStationNameReplacement + ","
          );
          raw = raw.replaceAll(
            "," + relatedStationSenderName + "*",
            "," + relatedStationNameReplacement + "*"
          );
        }
      }

      // Before returning we also linkify any url
      raw = Autolinker.link(raw, { newWindow: true });
      return raw;
    }
    return "";
  },

  /**
   * Returns true if packet is on map, false otherwise
   * @param {trackdirect.models.Packet} packet
   * @return boolean
   */
  _isPacketOnMap: function (packet) {
    if (
      packet.latitude <= this._map.getNorthEastLat() &&
      packet.latitude >= this._map.getSouthWestLat()
    ) {
      if (
        packet.longitude <= this._map.getNorthEastLng() &&
        packet.longitude >= this._map.getSouthWestLng()
      ) {
        return true;
      }
    }
    return false;
  },

  /**
   * Modify website when websocket state has changed
   * @return null
   */
  _handleWebsocketStateChange: function () {
    switch (this._websocket.getState()) {
      case this._websocket.State.CONNECTING:
        this._setWebsocketStateConnecting();
        break;

      case this._websocket.State.CONNECTED:
        this._setWebsocketStateConnected();

        // Trigger map change event since we now have access to websocket
        trackdirect.services.callbackExecutor.add(
          this,
          this._sendPositionRequest,
          []
        );
        break;

      case this._websocket.State.CLOSED:
      case this._websocket.State.ERROR:
        this._setWebsocketStateError();
        break;

      case this._websocket.State.LOADING:
        this._setWebsocketStateLoading(true, false);
        break;

      case this._websocket.State.LOADING_DONE:
        this._setWebsocketStateLoadingDone();
        break;

      case this._websocket.State.LISTENING_APRSIS:
        this._setWebsocketStateAprsISConnected();
        break;

      case this._websocket.State.CONNECTING_APRSIS:
        this._setWebsocketStateAprsISConnecting();
        break;

      case this._websocket.State.IDLE:
        this._setWebsocketStateIdle();
        break;

      case this._websocket.State.INACTIVE:
        this._setWebsocketStateInactive();
        break;
    }
  },

  /**
   * Show that websocket is Connecting
   * @return null
   */
  _setWebsocketStateConnecting: function () {
    if (this._statusContainerElementId !== null) {
      $("#" + this._statusContainerElementId)
        .html("Connecting")
        .css("color", "blue");
    }
  },

  /**
   * Show that websocket is Connected
   * @return null
   */
  _setWebsocketStateConnected: function () {
    this._map.resetAllMarkers();

    if (this._statusContainerElementId !== null) {
      $("#" + this._statusContainerElementId)
        .html("Connected")
        .css("color", "green");
    }
  },

  /**
   * Show that websocket has a problem
   * @return null
   */
  _setWebsocketStateError: function () {
    if (this._statusContainerElementId !== null) {
      $("#" + this._statusContainerElementId)
        .html("Disconnected")
        .css("color", "red");
    }

    this._map.resetAllMarkers();
    this._deactivateFiltered(false);

    var me = this;
    if (
      confirm(
        "You have been disconnected, this can be caused by a network error, by the timeout limit or if maintenance occurs while you’re logged in. Do you want to reconnect?"
      )
    ) {
      me._websocket = new trackdirect.Websocket(me._wsServerUrl);
      me._initWebsocketListeners();
      trackdirect.services.callbackExecutor.add(
        me,
        me._sendPositionRequest,
        []
      );
    }
  },

  /**
   * Show that websocket is loading
   * @param {boolean} isStateConfirmed
   * @param {boolean} showOnMobile
   * @return null
   */
  _setWebsocketStateLoading: function (isStateConfirmed, showOnMobile) {
    isStateConfirmed =
      typeof isStateConfirmed !== "undefined" ? isStateConfirmed : true;
    showOnMobile = typeof showOnMobile !== "undefined" ? showOnMobile : true;

    if (this._statusContainerElementId !== null) {
      $("#" + this._statusContainerElementId)
        .html(
          'Loading <i class="fa fa-spinner fa-spin" style="font-size:14px"></i>'
        )
        .css("color", "green");
    }
  },

  /**
   * Show that websocket is done loading
   * @return null
   */
  _setWebsocketStateLoadingDone: function () {
    if (this._statusContainerElementId !== null) {
      $("#" + this._statusContainerElementId)
        .html("Complete")
        .css("color", "green");
    }
  },

  /**
   * Show that websocket is receiving packets from APRS-IS
   * @return null
   */
  _setWebsocketStateAprsISConnected: function () {
    // APRS-IS Connection is up for this area!
    if (this._statusContainerElementId !== null) {
      $("#" + this._statusContainerElementId)
        .html("Connected to APRS feed")
        .css("color", "green");
    }
  },

  /**
   * Show that websocket waiting for packets from APRS-IS
   * @return null
   */
  _setWebsocketStateAprsISConnecting: function () {
    // Waiting for APRS-IS Connection
    if (this._statusContainerElementId !== null) {
      $("#" + this._statusContainerElementId)
        .html("Waiting for APRS feed")
        .css("color", "green");
    }
  },

  /**
   * Show that websocket is IDLE
   * @return null
   */
  _setWebsocketStateIdle: function () {
    // We are zoomed out and not doing anything
    if (this._statusContainerElementId !== null) {
      $("#" + this._statusContainerElementId)
        .html("Idle")
        .css("color", "green");
    }
  },

  /**
   * Show that websocket is INACTIVE
   * @return null
   */
  _setWebsocketStateInactive: function () {
    if (this._statusContainerElementId !== null) {
      $("#" + this._statusContainerElementId)
        .html("Inactive")
        .css("color", "orange");
    }

    this._websocket.close();
    this._map.resetAllMarkers();
    var me = this;
    if (
      confirm(
        "No activity for a long time, map updates has been stopped. Do you want to reconnect?"
      )
    ) {
      me._websocket = new trackdirect.Websocket(me._wsServerUrl);
      me._initWebsocketListeners();
      trackdirect.services.callbackExecutor.add(
        me,
        me._sendPositionRequest,
        []
      );
    }
  },

  /**
   * Send a position request to server
   * @return null
   */
  _sendPositionRequest: function () {
    if (!this._waitForFilterResponse && this._map.isMapReady()) {
      if (!this.isFilteredMode()) {
        if (this._map.getZoom() < trackdirect.settings.minZoomForMarkers) {
          // Just stop connection to APRS-IS
          this._websocket.doSendNewPositionRequest(
            0,
            0,
            0,
            0,
            this._map.state.getTimeLength() / 60,
            this.getTimeTravelTimestamp(),
            false
          );
        } else if (
          this._map.getZoom() >= trackdirect.settings.minZoomForMarkerTail
        ) {
          // We need all details, send regular request
          this._websocket.doSendNewPositionRequest(
            this._map.getNorthEastLat(),
            this._map.getNorthEastLng(),
            this._map.getSouthWestLat(),
            this._map.getSouthWestLng(),
            this._map.state.getTimeLength() / 60,
            this.getTimeTravelTimestamp(),
            false
          );
        } else {
          // We only need markers, only request the last packet for each station (server my still send everything, but we do not force server to do that)
          this._websocket.doSendNewPositionRequest(
            this._map.getNorthEastLat(),
            this._map.getNorthEastLng(),
            this._map.getSouthWestLat(),
            this._map.getSouthWestLng(),
            this._map.state.getTimeLength() / 60,
            this.getTimeTravelTimestamp(),
            true
          );
        }
      } else {
        // We are filtering, request everything everywhere for our filter
        this._websocket.doSendNewPositionRequest(
          90,
          180,
          -90,
          -180,
          this._map.state.getTimeLength() / 60,
          this.getTimeTravelTimestamp(),
          false
        );
      }

      var data = {
        center: this._map.getCenterLiteral(),
        zoom: this._map.getZoom(),
      };
      this._emitEventListeners("position-request-sent", data);
    }
  },

  /**
   * Send a idle request to server if needed
   * @return null
   */
  _sendIdleRequest: function () {
    // The position 0,0,0,0 means that we request server to be IDLE
    if (this._websocket.isPositionRequestSent()) {
      this._websocket.doSendNewPositionRequest(
        0,
        0,
        0,
        0,
        this._map.state.getTimeLength() / 60,
        this.getTimeTravelTimestamp(),
        false
      );
    }
  },

  /**
   * Deactivate filtered mode is confirmed
   * @param {boolean} sendNewRequest
   * @return null
   */
  _deactivateFiltered: function (sendNewRequest) {
    // Reset Time travel
    this.setTimeTravelTimestamp(null);

    // clear everything
    this._map.resetAllMarkers();

    if (this._map.state.openInfoWindow !== null) {
      this._map.state.openInfoWindow.hide();
    }
    this._map.deactivateFilteredMode();

    // If we was tracking one station that we was filtering on, stop tracking it
    this.stopTrackStation();
    this.setTimeLength(this.settings.defaultTimeLength, false);

    this._emitEventListeners("filter-changed", []);
    this._emitEventListeners("filter-stopped");

    if (sendNewRequest) {
      trackdirect.services.callbackExecutor.add(
        this,
        this._sendPositionRequest,
        []
      );
    }

    this._emitEventListeners("mode-changed");
  },

  /**
   * Returns the website base URL
   * @param {string} host
   * @return string
   */
  _getMapBaseUrl: function (host) {
    host = typeof host !== "undefined" ? host : "";
    host = host.replace("http://", "");
    host = host.replace("https://", "");
    if (host == "") {
      host = window.location.host;
    }
    if (location.protocol === "https:") {
      return "https://" + host;
    } else {
      return "http://" + host;
    }
  },

  /**
   * Call all listeners that are listening on specified event
   * @param {string} event
   * @param {string} arg
   * @return null
   */
  _emitEventListeners: function (event, arg) {
    if (event in this._eventListeners) {
      for (var i = 0; i < this._eventListeners[event].length; i++) {
        this._eventListeners[event][i](arg);
      }
    }

    if (event in this._eventListenersOnce) {
      for (var i = 0; i < this._eventListenersOnce[event].length; i++) {
        this._eventListenersOnce[event][i](arg);
        this._eventListenersOnce[event].splice(i, 1);
        i--;
      }
    }

    if (event == "trackdirect-init-done") {
      this._trackdirectInitDone = true;
    }

    if (event == "map-created") {
      this._mapCreated = true;
    }
  },
};
