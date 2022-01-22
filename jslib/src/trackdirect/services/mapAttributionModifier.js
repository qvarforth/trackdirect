trackdirect.services.mapAttributionModifier = {
  _hereBaseAttributionData: null,
  _hereAerialAttributionData: null,
  _latestAttribution: null,
  _isHereInitialized: false,
  _eventListeners: {},
  _eventListenersOnce: {},

  /**
   * Update the map attribution
   * @param {trackdirect.models.Map} map
   */
  update: function (map) {
    if (this._isHereTileProvider(map)) {
      this.updateHereAttribution(map);
    } else if (this._latestAttribution != null) {
      // Just reset attribution to default
      this.setMapAttribution(map, "");
    }
  },

  /**
   * Update the HERE map attribution
   * @param {trackdirect.models.Map} map
   */
  updateHereAttribution: function (map) {
    this._loadHereAttributionData(map);
    var me = this;
    var base = this._getMapTileBase(map);
    if (base == "base") {
      this.addListener(
        "init-here-base",
        function () {
          var attribution = me._getHereAttributionString(map);
          me.setMapAttribution(map, attribution);
        },
        true
      );
    } else if (base == "aerial") {
      this.addListener(
        "init-here-aerial",
        function () {
          var attribution = me._getHereAttributionString(map);
          me.setMapAttribution(map, attribution);
        },
        true
      );
    }
  },

  /**
   * Set map attribution to specified string
   * @param {trackdirect.models.Map} map
   * @param {string} attribution
   */
  setMapAttribution: function (map, attribution) {
    if (this._latestAttribution != attribution) {
      map.attributionControl.removeAttribution(this._latestAttribution);
      if (attribution != "") {
        map.attributionControl.addAttribution(attribution);
      }
    }

    this._latestAttribution = attribution;
  },

  /**
   * Add new event listener
   * @param {string} event
   * @param {string} handler
   * @param {boolean} execOnce
   */
  addListener: function (event, handler, execOnce) {
    execOnce = typeof execOnce !== "undefined" ? execOnce : false;

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

    if (event == "init-here-base" && this._isHereBaseInitialized) {
      this._emitEventListeners("init-here-base");
    }

    if (event == "init-here-aerial" && this._isHereAerialInitialized) {
      this._emitEventListeners("init-here-aerial");
    }
  },

  /**
   * Returnes true if the map tile provider is here.com
   * @param {trackdirect.models.Map} map
   * @return {Boolean}
   */
  _isHereTileProvider: function (map) {
    var tileLayer = map.getLeafletTileLayer();
    if (
      tileLayer !== null &&
      typeof tileLayer._url !== "undefined" &&
      tileLayer._url.indexOf("here.com") >= 0
    ) {
      return true;
    }

    return false;
  },

  /**
   * Get map tile variant
   * @param {trackdirect.models.Map} map
   */
  _getMapTileOptions: function (map) {
    var tileLayer = map.getLeafletTileLayer();
    if (tileLayer !== null && typeof tileLayer.options !== "undefined") {
      return tileLayer.options;
    }

    return null;
  },

  /**
   * Get map tile variant
   * @param {trackdirect.models.Map} map
   */
  _getMapTileVariant: function (map) {
    var options = this._getMapTileOptions(map);
    if (options.variant !== "undefined") {
      return options.variant;
    }

    return null;
  },

  /**
   * Get map tile initial variant
   * @param {trackdirect.models.Map} map
   */
  _getMapTileInitialVariant: function (map) {
    var mapVariant = this._getMapTileVariant(map);
    var dotIndex = mapVariant.indexOf(".");
    if (dotIndex >= 0) {
      return mapVariant.substring(0, dotIndex);
    }
    return mapVariant;
  },

  /**
   * Get map tile base variant
   * @param {trackdirect.models.Map} map
   */
  _getMapTileBase: function (map) {
    var options = this._getMapTileOptions(map);
    if (options.base !== "undefined") {
      return options.base;
    }

    return null;
  },

  /**
   * Get HERE copyright string for the currnet map bounds
   * @param {trackdirect.models.Map} map
   */
  _getHereAttributionString: function (map) {
    var result = [];
    var mapBaseVariant = this._getMapTileInitialVariant(map);

    if (this._getMapTileBase(map) == "base") {
      var data = this._hereBaseAttributionData;
    } else if (this._getMapTileBase(map) == "aerial") {
      var data = this._hereAerialAttributionData;
    }

    if (data !== null && typeof data[mapBaseVariant] !== "undefined") {
      for (var i = 0, len = data[mapBaseVariant].length; i < len; i++) {
        var attributionArea = data[mapBaseVariant][i];

        if (
          parseInt(map.getZoom()) >= parseInt(attributionArea.minLevel) &&
          parseInt(map.getZoom()) <= parseInt(attributionArea.maxLevel)
        ) {
          if (
            typeof attributionArea.boxes === "undefined" ||
            this._isAnyBoxVisible(attributionArea.boxes, map)
          ) {
            var attributionText =
              '<span title="' +
              attributionArea.alt +
              '">' +
              attributionArea.label +
              "</span>";
            if (result.indexOf(attributionText) < 0) {
              result.push(attributionText);
            }
          }
        }
      }
    }
    return result.join(", ");
  },

  /**
   * Returnes true if any lat/lng box intersects with current map bounds
   * @param {Array} boxes
   * @param {trackdirect.models.Map} map
   */
  _isAnyBoxVisible: function (boxes, map) {
    if (typeof boxes !== "undefined" && Array.isArray(boxes)) {
      for (var i = 0, len = boxes.length; i < len; i++) {
        var box = boxes[i];
        if (Array.isArray(box) && box.length >= 4) {
          var boxBounds = L.latLngBounds(
            L.latLng(parseFloat(box[0]), parseFloat(box[1])),
            L.latLng(parseFloat(box[2]), parseFloat(box[3]))
          );
          if (boxBounds.isValid() && boxBounds.intersects(map.getBounds())) {
            return true;
          }
        }
      }
    }
    return false;
  },

  /**
   * Download HERE copyright data
   * @param {trackdirect.models.Map} map
   */
  _loadHereAttributionData: function (map) {
    var options = this._getMapTileOptions(map);
    var base = this._getMapTileBase(map);

    if (
      (this._hereBaseAttributionData === null && base == "base") ||
      (this._hereAerialAttributionData === null && base == "aerial")
    ) {
      var me = this;

      jQuery.ajax({
        url:
          "https://1." +
          base +
          ".maps.api.here.com/maptile/2.1/copyright/" +
          options.mapID +
          "?app_id=" +
          options.app_id +
          "&app_code=" +
          options.app_code,
        type: "GET",
        dataType: "json",
        timeout: 5000, // sets timeout to 5 seconds
        success: function (result) {
          if (base == "base") {
            me._hereBaseAttributionData = result;
            me._isHereBaseInitialized = true;
            me._emitEventListeners("init-here-base");
          } else if (base == "aerial") {
            me._hereAerialAttributionData = result;
            me._isHereAerialInitialized = true;
            me._emitEventListeners("init-here-aerial");
          }
        },
        error: function (xhr) {
          console.log("Failed to load map copyright data");
        },
      });
    }
  },

  /**
   * Call all listeners that are listening on specified event
   * @param {string} event
   * @param {string} arg
   */
  _emitEventListeners: function (event, arg) {
    if (event in this._eventListeners) {
      for (var i = 0; i < this._eventListeners[event].length; i++) {
        this._eventListeners[event][i](arg);
      }
    }

    if (event in this._eventListenersOnce) {
      var eventListenersOnce = this._eventListenersOnce[event].splice(0);
      this._eventListenersOnce[event] = [];
      for (var i = 0; i < eventListenersOnce.length; i++) {
        eventListenersOnce[i](arg);
      }
    }
  },
};
