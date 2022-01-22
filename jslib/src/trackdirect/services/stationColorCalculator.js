trackdirect.services.stationColorCalculator = {
  _colors: [
    "#3333ff", // blue       (#2A2AFF)
    "#9900cc", // purple     (#7002A7)
    "#006600", // green      (#005500)
    "#cc0000", // red        (#A70202)
  ],
  _stationColorId: {},

  /**
   * Get html (hex) color for specified packet
   * @param {object} packet
   * @return {string}
   */
  getColor: function (packet) {
    var colorId = this.getColorId(packet);
    return this._colors[colorId];
  },

  /**
   * Get kml color for specified packet
   * @param {object} packet
   * @return {string}
   */
  getKmlColor(packet) {
    var hex = this.getColor(packet);
    var result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
    if (result) {
      return "FF" + result[3] + result[2] + result[1];
    }
    return null;
  },

  /**
   * Get color ID for specified packet
   * Color will be selected by station/object name (this make sures that object with different senders still get the same color)
   * @param {object} packet
   * @return {int}
   */
  getColorId: function (packet) {
    if (packet.station_name in this._stationColorId) {
      // This station has allready got a color, use it
      colorId = this._stationColorId[packet.station_name];
      return colorId;
    } else {
      var hash = this._simplehashStr(packet.station_name);
      var colorId = hash % this._colors.length;
      this._stationColorId[packet.station_name] = colorId;
    }

    return colorId;
  },

  /**
   * Get simple hash from string (bad hash, but good for our usage)
   * @param {string} str
   * @return int
   */
  _simplehashStr: function (str) {
    var hash = 0;
    for (var i = 0; i < str.length; i++) {
      var charCode = str.charCodeAt(i);
      hash += charCode;
    }
    return hash;
  },
};
