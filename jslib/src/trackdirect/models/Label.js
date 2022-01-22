if (typeof google === "object" && typeof google.maps === "object") {
  /**
   * Class trackdirect.models.Label inherit google.maps.OverlayView
   * @see https://developers.google.com/maps/documentation/javascript/reference#OverlayView
   * @param {array} options
   * @param {trackdirect.models.Map} map
   */
  trackdirect.models.Label = function (options, map) {
    this._defaultMap = map;
    options.map = null;
    this.setValues(options);
    this.div_ = null;
  };
  trackdirect.models.Label.prototype = new google.maps.OverlayView();

  /**
   * show if it is not shown
   */
  trackdirect.models.Label.prototype.show = function () {
    if (typeof this.getMap() === "undefined" || this.getMap() === null) {
      this.setMap(this._defaultMap);
    }
  };

  /**
   * hide if it is visible
   */
  trackdirect.models.Label.prototype.hide = function () {
    if (this.getMap() !== null) {
      this.setMap(null);
    }
  };

  /**
   * Override onAdd
   */
  trackdirect.models.Label.prototype.onAdd = function () {
    if (this.div_ === null) {
      var jqSpan = $(document.createElement("span"));
      jqSpan.css("color", "#101010");
      jqSpan.css(
        "text-shadow",
        "1px 1px 1px #FFF, -1px -1px 1px #FFF, 1px -1px 1px #FFF, -1px 1px 1px #FFF, 1px 1px 1px #FFF"
      );
      jqSpan.css("position", "relative");
      jqSpan.css("top", "10px");
      jqSpan.css("white-space", "nowrap");
      jqSpan.css("font-family", "Helvetica");
      jqSpan.css("font-weight", "bold");
      jqSpan.css("font-size", "10px");
      jqSpan.css("padding", "0px");
      jqSpan.css("z-index", "1000");
      jqSpan.css("margin", "0");
      jqSpan.css("line-height", "10px");
      var span = (this.span_ = jqSpan[0]);
      span.innerHTML = this.get("text").toString();

      var div = (this.div_ = document.createElement("div"));
      div.appendChild(span);
      div.style.cssText = "position: absolute; display: none";
    }

    var pane = this.getPanes().overlayLayer;
    pane.appendChild(this.div_);

    // Ensures the label is redrawn if the text or position is changed.
    var me = this;
    this.listeners_ = [
      google.maps.event.addListener(this, "position_changed", function () {
        me.draw();
      }),
      google.maps.event.addListener(this, "text_changed", function () {
        me.draw();
      }),
    ];
  };

  /**
   * Override onRemove
   */
  trackdirect.models.Label.prototype.onRemove = function () {
    if (this.div_ !== null && this.div_.parentNode !== null) {
      this.div_.parentNode.removeChild(this.div_);

      // Label is removed from the map, stop updating its position/text.
      for (var i = 0, I = this.listeners_.length; i < I; ++i) {
        google.maps.event.removeListener(this.listeners_[i]);
      }
    }
  };

  /**
   * Draw the label
   */
  trackdirect.models.Label.prototype.draw = function () {
    var projection = this.getProjection();
    if (typeof this.get("position").lat === "function") {
      var latLng = new google.maps.LatLng({
        lat: this.get("position").lat(),
        lng: this.get("position").lng(),
      });
    } else {
      var latLng = new google.maps.LatLng({
        lat: this.get("position").lat,
        lng: this.get("position").lng,
      });
    }
    var position = projection.fromLatLngToDivPixel(latLng);

    var div = this.div_;
    var span = this.span_;
    span.innerHTML = this.get("text").toString();
    div.style.left = position.x + "px";
    div.style.top = position.y + "px";

    div.style.display = "block";
  };
} else if (typeof L === "object" && typeof L.Tooltip !== "undefined") {
  /**
   * Class trackdirect.models.Label
   * @param {array} options
   * @param {trackdirect.models.Map} map
   */
  trackdirect.models.Label = function (options, map) {
    this._defaultMap = map;

    // Call the parent constructor
    L.Tooltip.call(this, this._getBasicOptions(options));

    this.setContent(options.text);
    if (
      typeof options.position !== "undefined" &&
      typeof options.position.lat !== "undefined" &&
      typeof options.position.lng !== "undefined"
    ) {
      this.setLatLng(new L.LatLng(options.position.lat, options.position.lng));
    }
  };
  trackdirect.models.Label.prototype = new L.Tooltip();

  /**
   * show if it is not shown
   */
  trackdirect.models.Label.prototype.show = function () {
    if (!this._defaultMap.hasLayer(this)) {
      this.addTo(this._defaultMap);
    }
  };

  /**
   * hide if it is visible
   */
  trackdirect.models.Label.prototype.hide = function () {
    if (this._defaultMap.hasLayer(this)) {
      this._defaultMap.removeLayer(this);
    }
  };

  /**
   * Get a suitable leaflet options object
   * @return {object}
   */
  trackdirect.models.Label.prototype._getBasicOptions = function (options) {
    return {
      direction: "right",
      noWrap: true,
      offset: L.point(2, 10),
      className: "leaflet-marker-labeltext",
      permanent: true,
    };
  };
} else if (typeof L === "object") {
  /**
   * Class trackdirect.models.Label
   * @param {array} options
   * @param {trackdirect.models.Map} map
   */
  trackdirect.models.Label = function (options, map) {
    this._defaultMap = map;

    var position = null;
    if (
      typeof options.position !== "undefined" &&
      typeof options.position.lat !== "undefined" &&
      typeof options.position.lng !== "undefined"
    ) {
      position = [options.position.lat, options.position.lng];
    }

    // Call the parent constructor
    L.Marker.call(this, position, this._getBasicOptions(options));
  };
  trackdirect.models.Label.prototype = Object.create(L.Marker.prototype);
  trackdirect.models.Label.prototype.constructor = trackdirect.models.Label;

  /**
   * show if it is not shown
   */
  trackdirect.models.Label.prototype.show = function () {
    if (!this._defaultMap.hasLayer(this)) {
      this.addTo(this._defaultMap);
    }
  };

  /**
   * hide if it is visible
   */
  trackdirect.models.Label.prototype.hide = function () {
    if (this._defaultMap.hasLayer(this)) {
      this._defaultMap.removeLayer(this);
    }
  };

  /**
   * Get a suitable leaflet options object
   * @return {object}
   */
  trackdirect.models.Label.prototype._getBasicOptions = function (options) {
    var strlen = options.text.length;

    var myIcon = L.divIcon({
      iconSize: new L.Point(strlen * 10, 20),
      className: "leaflet-marker-labeltext",
      html: options.text,
      iconAnchor: new L.Point(-2, -10),
    });

    return {
      icon: myIcon,
      clickable: false,
      keyboard: false,
    };
  };
} else {
  // If no Label is supported we use a dummy class
  trackdirect.models.Label = function (options, map) {};
  trackdirect.models.Label.prototype.show = function () {};
  trackdirect.models.Label.prototype.hide = function () {};
}
