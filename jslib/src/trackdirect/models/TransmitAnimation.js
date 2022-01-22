/**
 * Class trackdirect.models.TransmitAnimation inherits google.maps.Marker
 * @see https://developers.google.com/maps/documentation/javascript/reference#Marker
 * @param {trackdirect.models.Marker} marker
 * @param {trackdirect.models.Map} map
 */
trackdirect.models.TransmitAnimation = function (marker, map) {
  this._map = map;
  this._marker = marker;
  this.init();
};

/**
 * Show transmit animation
 */
trackdirect.models.TransmitAnimation.prototype.show = function () {
  this._startAnimation();
};

/**
 * Hide transmit animation
 */
trackdirect.models.TransmitAnimation.prototype.hide = function () {
  if (typeof google === "object" && typeof google.maps === "object") {
    this.iconMarkers[1].setMap(null);
    this.iconMarkers[2].setMap(null);
    this.iconMarkers[3].setMap(null);
  } else if (typeof L === "object") {
    this._map.removeLayer(this.iconMarkers[1]);
    this._map.removeLayer(this.iconMarkers[2]);
    this._map.removeLayer(this.iconMarkers[3]);
  }
  this.marker.transmitPolyLine.hide();
};

/**
 * Show packet send animation
 */
trackdirect.models.TransmitAnimation.prototype.init = function () {
  var newLatLng = this._marker.packet.getLatLngLiteral();
  this._marker.transmitPolyLine = new trackdirect.models.TransmitPolyline(
    this._marker.packet,
    this._map
  );
  this.iconMarkers = [];
  for (var i = 1; i <= 3; i++) {
    var icon = this._getIcon(i);
    if (typeof google === "object" && typeof google.maps === "object") {
      var iconMarker = new google.maps.Marker({
        position: newLatLng,
        zIndex: this._map.state.currentMarkerZindex,
        icon: icon,
        opacity: 0.6,
      });
    } else if (typeof L === "object") {
      var iconMarker = new L.Marker(newLatLng, {
        zIndexOffset: this._map.state.currentMarkerZindex,
        icon: icon,
        opacity: 0.6,
      });
    }
    this.iconMarkers[i] = iconMarker;
  }
};

/**
 * Get transmit icon
 * @param {int} index
 * @return {object}
 */
trackdirect.models.TransmitAnimation.prototype._getIcon = function (index) {
  if (typeof google === "object" && typeof google.maps === "object") {
    var icon = {
      url:
        trackdirect.settings.baseUrl +
        trackdirect.settings.imagesBaseDir +
        "transmit" +
        index +
        ".png",
      size: new google.maps.Size(60, 60),
      origin: new google.maps.Point(0, 0),
      anchor: new google.maps.Point(30, 30),
    };
  } else if (typeof L === "object") {
    var icon = L.icon({
      iconUrl:
        trackdirect.settings.baseUrl +
        trackdirect.settings.imagesBaseDir +
        "transmit" +
        index +
        ".png",
      iconSize: [60, 60],
      iconAnchor: [30, 30],
    });
  }
  return icon;
};

/**
 * Start the previously created activity animation
 * @param {object} marker
 * @param {array} iconMarkers
 */
trackdirect.models.TransmitAnimation.prototype._startAnimation = function () {
  var me = this;
  me._showIconMarker(1);

  window.setTimeout(function () {
    me._showIconMarker(2);
  }, 150);

  window.setTimeout(function () {
    me._showIconMarker(3);

    if (me._marker.transmitPolyLine !== null) {
      me._marker.transmitPolyLine.show();
    }
  }, 300);

  window.setTimeout(function () {
    me._hideIconMarker(1);
  }, 800);

  window.setTimeout(function () {
    me._hideIconMarker(2);
  }, 900);

  window.setTimeout(function () {
    me._hideIconMarker(3);

    if (me._marker.transmitPolyLine != null) {
      me._marker.transmitPolyLine.hide(4000);
    }
  }, 1000);
};

/**
 * Show icon marker with specified index
 * @param {int} index
 */
trackdirect.models.TransmitAnimation.prototype._showIconMarker = function (
  index
) {
  if (typeof google === "object" && typeof google.maps === "object") {
    this.iconMarkers[index].setMap(this._map);
  } else if (typeof L === "object") {
    this.iconMarkers[index].addTo(this._map);
  }
};

/**
 * Hide icon marker with specified index
 * @param {int} index
 */
trackdirect.models.TransmitAnimation.prototype._hideIconMarker = function (
  index
) {
  if (typeof google === "object" && typeof google.maps === "object") {
    this.iconMarkers[index].setMap(null);
  } else if (typeof L === "object") {
    this._map.removeLayer(this.iconMarkers[index]);
  }
};
