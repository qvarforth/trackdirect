/**
 * Class trackdirect.models.Packet
 * @param {object} data
 */
trackdirect.models.Packet = function (data) {
  this.init();
  for (var key in data) {
    this[key] = data[key];
  }
};

trackdirect.models.Packet.prototype.init = function () {
  this["altitude"] = null;
  this["comment"] = "";
  this["course"] = null;
  this["db"] = null;
  this["id"] = null;
  this["latest_phg_timestamp"] = null;
  this["latest_rng_timestamp"] = null;
  this["latitude"] = null;
  this["longitude"] = null;
  this["map_id"] = null;
  this["map_sector"] = null;
  this["marker_counter"] = null;
  this["marker_id"] = null;
  this["ogn"] = null;
  this["overwrite"] = null; // 1 if it should be overwritten by next packet from station
  this["is_moving"] = 1;
  this["packet_order_id"] = null;
  this["packet_tail_timestamp"] = null;
  this["packet_type_id"] = null;
  this["phg"] = null;
  this["posambiguity"] = 0;
  this["position_timestamp"] = null;
  this["raw"] = "";
  this["raw_path"] = "";
  this["realtime"] = 0; // 1 if not fetched from database
  this["related_map_sectors"] = [];
  this["reported_timestamp"] = null;
  this["rng"] = null;
  this["sender_id"] = null;
  this["sender_name"] = null;
  this["source_id"] = null;
  this["speed"] = null;
  this["station_id"] = null;
  this["station_id_path"] = [];
  this["station_location_path"] = [];
  this["station_name"] = null;
  this["station_name_path"] = [];
  this["symbol"] = null;
  this["symbol_table"] = null;
  this["telemetry"] = null;
  this["timestamp"] = null;
  this["weather"] = null;
};

/**
 * Returns the packet station name (including sender if needed)
 * @return {string}
 */
trackdirect.models.Packet.prototype.getStationName = function () {
  if (this.station_name == this.sender_name) {
    return escapeHtml(this.station_name);
  } else {
    return escapeHtml(this.station_name + " (" + this.sender_name + ")");
  }
};

/**
 * Returns the packet position
 * @return {LatLngLiteral}
 */
trackdirect.models.Packet.prototype.getLatLngLiteral = function () {
  return { lat: parseFloat(this.latitude), lng: parseFloat(this.longitude) };
};

/**
 * Returns true if packet map ID is considered to be visible
 * @return boolean
 */
trackdirect.models.Packet.prototype.hasConfirmedMapId = function () {
  if ([1, 2, 12].indexOf(this.map_id) >= 0) {
    return true;
  }
  return false;
};

/**
 * Returns OGN aircraft type name
 * @return {string}
 */
trackdirect.models.Packet.prototype.getOgnAircraftType = function () {
  if (typeof this.ogn !== "undefined" && this.ogn !== null) {
    if (
      typeof this.ogn.ogn_aircraft_type_id !== "undefined" &&
      this.ogn.ogn_aircraft_type_id != ""
    ) {
      if (this.ogn.ogn_aircraft_type_id == 1) {
        return "Glider";
      } else if (this.ogn.ogn_aircraft_type_id == 2) {
        return "Tow Plane";
      } else if (this.ogn.ogn_aircraft_type_id == 3) {
        return "Helicopter";
      } else if (this.ogn.ogn_aircraft_type_id == 4) {
        return "Parachute";
      } else if (this.ogn.ogn_aircraft_type_id == 5) {
        return "Drop Plane";
      } else if (this.ogn.ogn_aircraft_type_id == 6) {
        return "Hang Glider";
      } else if (this.ogn.ogn_aircraft_type_id == 7) {
        return "Para Glider";
      } else if (this.ogn.ogn_aircraft_type_id == 8) {
        return "Powered Aircraft";
      } else if (this.ogn.ogn_aircraft_type_id == 9) {
        return "Jet Aircraft";
      } else if (this.ogn.ogn_aircraft_type_id == 10) {
        return "UFO";
      } else if (this.ogn.ogn_aircraft_type_id == 11) {
        return "Balloon";
      } else if (this.ogn.ogn_aircraft_type_id == 12) {
        return "Airship";
      } else if (this.ogn.ogn_aircraft_type_id == 13) {
        return "UAV";
      } else if (this.ogn.ogn_aircraft_type_id == 14) {
        return "";
      } else if (this.ogn.ogn_aircraft_type_id == 15) {
        return "Static Object";
      }
    }
  }
  return null;
};

/**
 * Returns OGN device DB aircraft type name
 * @return {string}
 */
trackdirect.models.Packet.prototype.getOgnDdbAircraftType = function () {
  if (typeof this.ogn_device !== "undefined" && this.ogn_device !== null) {
    if (
      typeof this.ogn_device.ddb_aircraft_type !== "undefined" &&
      this.ogn_device.ddb_aircraft_type != ""
    ) {
      if (this.ogn_device.ddb_aircraft_type == 1) {
        return "Glider/Motoglider";
      } else if (this.ogn_device.ddb_aircraft_type == 2) {
        return "Plane";
      } else if (this.ogn_device.ddb_aircraft_type == 3) {
        return "Ultralight";
      } else if (this.ogn_device.ddb_aircraft_type == 4) {
        return "Helicopter";
      } else if (this.ogn_device.ddb_aircraft_type == 5) {
        return "Drone/UAV";
      } else if (this.ogn_device.ddb_aircraft_type == 6) {
        return "Other";
      }
    }
  }
  return null;
};

/**
 * Returns OGN address type name
 * @return {string}
 */
trackdirect.models.Packet.prototype.getOgnAddressType = function () {
  if (typeof this.ogn !== "undefined" && this.ogn !== null) {
    if (
      typeof this.ogn.ogn_address_type_id !== "undefined" &&
      this.ogn.ogn_address_type_id != ""
    ) {
      if (this.ogn.ogn_address_type_id == 1) {
        return "ICAO";
      } else if (this.ogn.ogn_address_type_id == 2) {
        return "FLARM";
      } else if (this.ogn.ogn_address_type_id == 3) {
        return "OGN";
      }
    }
  }
  return null;
};

/**
 * Returns OGN sender address
 * @return {string}
 */
trackdirect.models.Packet.prototype.getOgnSenderAddress = function () {
  if (typeof this.ogn !== "undefined" && this.ogn !== null) {
    if (
      typeof this.ogn.ogn_sender_address !== "undefined" &&
      this.ogn.ogn_sender_address != ""
    ) {
      return this.ogn.ogn_sender_address;
    }
  }
  return null;
};

/**
 * Returns OGN registration
 * @return {string}
 */
trackdirect.models.Packet.prototype.getOgnRegistration = function () {
  if (typeof this.ogn_device !== "undefined" && this.ogn_device !== null) {
    if (
      typeof this.ogn_device.registration !== "undefined" &&
      this.ogn_device.registration != ""
    ) {
      return this.ogn_device.registration;
    }
  }
  return null;
};

/**
 * Returns OGN CN
 * @return {string}
 */
trackdirect.models.Packet.prototype.getOgnCN = function () {
  if (typeof this.ogn_device !== "undefined" && this.ogn_device !== null) {
    if (typeof this.ogn_device.cn !== "undefined" && this.ogn_device.cn != "") {
      return this.ogn_device.cn;
    }
  }
  return null;
};

/**
 * Returns OGN summary
 * @return {string}
 */
trackdirect.models.Packet.prototype.getOgnSummary = function () {
  var senderAddress = this.getOgnSenderAddress();
  var aircraftType = this.getOgnAircraftType();
  var ddbAircraftType = this.getOgnDdbAircraftType();
  var addressType = this.getOgnAddressType();

  var summary = "";
  if (ddbAircraftType !== null) {
    summary += ddbAircraftType;
  } else if (aircraftType !== null) {
    summary += aircraftType;
  }
  if (senderAddress !== null) {
    if (summary != "") {
      summary += " ";
    }
    summary += senderAddress;

    if (addressType !== null) {
      summary += " (" + addressType + ")";
    }
  }
  return summary;
};

/**
 * Returns true if packet has direction support
 * @return boolean
 */
trackdirect.models.Packet.prototype.hasDirectionSupport = function () {
  if (
    this.course !== null &&
    this.speed !== null &&
    this.speed > 0 &&
    this.source_id == 1 &&
    this.packet_order_id == 1 &&
    this.is_moving == 1 &&
    this.hasConfirmedMapId()
  ) {
    var symbolCategory = 1;
    if (this.symbol_table.charCodeAt(0) == "92") {
      symbolCategory = 2;
    }

    if (
      symbolCategory == 1 &&
      trackdirect.settings.primarySymbolWithNoDirectionPolyline.indexOf(
        parseInt(this.symbol.charCodeAt(0))
      ) > -1
    ) {
      // This icon does not support direction polyline, avoid drawing anything since speed could be windspeed
      return false;
    }

    if (
      symbolCategory == 2 &&
      trackdirect.settings.alternativeSymbolWithNoDirectionPolyline.indexOf(
        parseInt(this.symbol.charCodeAt(0))
      ) > -1
    ) {
      // This icon does not support direction polyline, avoid drawing anything since speed could be windspeed
      return false;
    }
    return true;
  }
  return false;
};

/**
 * Get PGH string
 * @return string
 */
trackdirect.models.Packet.prototype.getPhg = function () {
  if (this.phg !== null) {
    if (this.phg == 0) {
      return null; // 0000 is considered not to be used (power == 0!)
    } else if (this.phg < 10) {
      return "000" + String(this.phg);
    } else if (this.phg < 100) {
      return "00" + String(this.phg);
    } else if (this.phg < 1000) {
      return "0" + String(this.phg);
    } else {
      return String(this.phg);
    }
  }
  return null;
};

/**
 * Get RNG range in meters
 * @return float
 */
trackdirect.models.Packet.prototype.getRNGRange = function () {
  if (this.rng !== null) {
    return this.rng;
  }
  return null;
};

/**
 * Get PGH range in meters
 * @return float
 */
trackdirect.models.Packet.prototype.getPHGRange = function () {
  if (this.getPhg() !== null) {
    var p = this.getPhgPower();
    var h = this.getPhgHaat(false);
    var g = this.getPhgGain();

    var gain = Math.pow(10, g / 10); //converts from DB to decimal
    var range = Math.sqrt(2 * h * Math.sqrt((p / 10) * (gain / 2)));
    return range / 0.000621371192; // convert to m and return
  }
  return null;
};

/**
 * Get PGH description
 * @return String
 */
trackdirect.models.Packet.prototype.getPHGDescription = function () {
  if (this.getPhg() !== null) {
    var power = this.getPhgPower();
    var haat = this.getPhgHaat();
    var gain = this.getPhgGain();
    var direction = this.getPhgDirection();

    var description = "";
    if (power !== null) {
      description += "Power " + power + "W";
    }

    if (haat !== null) {
      if (description.length > 0) {
        description += ", ";
      }
      description += "Height " + haat + "m";
    }

    if (gain !== null && direction !== null) {
      if (description.length > 0) {
        description += ", ";
      }
      description += "Gain " + gain + "dB " + direction;
    }
    return description;
  }
  return null;
};

/**
 * Get PGH power
 * @return int
 */
trackdirect.models.Packet.prototype.getPhgPower = function () {
  if (this.getPhg() !== null) {
    return Math.pow(parseInt(this.getPhg().substring(0, 1)), 2);
  }
  return null;
};

/**
 * Get PGH hight (above averange terrain)
 * @param {boolean} inMeters
 * @return int
 */
trackdirect.models.Packet.prototype.getPhgHaat = function (inMeters) {
  inMeters = typeof inMeters !== "undefined" ? inMeters : true;
  if (this.getPhg() != null) {
    value = parseInt(this.getPhg().substring(1, 2));

    var haat = 10;
    if (value == 1) {
      haat = 20;
    } else if (value > 1) {
      haat = 10 * Math.pow(value, 2);
    }

    if (inMeters) {
      return Math.round(haat * 0.3048, 0);
    } else {
      return haat;
    }
  }
  return null;
};

/**
 * Get PGH Gain
 * @return int
 */
trackdirect.models.Packet.prototype.getPhgGain = function () {
  if (this.getPhg() != null) {
    return parseInt(this.getPhg().substring(2, 3));
  }
  return null;
};

/**
 * Get PGH Direction
 * @return String
 */
trackdirect.models.Packet.prototype.getPhgDirection = function () {
  if (this.getPhg() != null) {
    switch (parseInt(this.getPhg().substring(3, 4))) {
      case 0:
        return "omni";
        break;
      case 1:
        return "North East";
        break;
      case 2:
        return "East";
        break;
      case 3:
        return "South East";
        break;
      case 4:
        return "South";
        break;
      case 5:
        return "South West";
        break;
      case 6:
        return "West";
        break;
      case 7:
        return "North West";
        break;
      case 8:
        return "North";
        break;
    }
  }
  return null;
};

/**
 * Get PGH Direction Degree
 * @return int
 */
trackdirect.models.Packet.prototype.getPhgDirectionDegree = function () {
  if (this.getPhg() != null) {
    switch (parseInt(this.getPhg().substring(3, 4))) {
      case 0:
        return null;
        break;
      case 1:
        return 45;
        break;
      case 2:
        return 90;
        break;
      case 3:
        return 135;
        break;
      case 4:
        return 180;
        break;
      case 5:
        return 225;
        break;
      case 6:
        return 270;
        break;
      case 7:
        return 315;
        break;
      case 8:
        return 360;
        break;
    }
  }
  return null;
};

/**
 * Get distance between packet latest position for specified marker
 * @param {trackdirect.models.Marker} marker
 * @return {float}
 */
trackdirect.models.Packet.prototype.getMarkerDistance = function (marker) {
  var packetLatLng = {
    lat: parseFloat(this.latitude),
    lng: parseFloat(this.longitude),
  };
  var markerPacketLatLng = {
    lat: parseFloat(marker.packet.latitude),
    lng: parseFloat(marker.packet.longitude),
  };
  return trackdirect.services.distanceCalculator.getDistance(
    packetLatLng,
    markerPacketLatLng
  );
};

/**
 * Returns true if both packet has same symbol as marker latest packet
 * @param {trackdirect.models.Marker} marker
 * @return {boolean}
 */
trackdirect.models.Packet.prototype.hasSameSymbol = function (marker) {
  if (
    marker.packet.symbol == this.symbol &&
    marker.packet.symbol_table == this.symbol_table
  ) {
    return true;
  }
  return false;
};

/**
 * Returns linkified packet.raw_path
 * @return {string}
 */
trackdirect.models.Packet.prototype.getLinkifiedRawPath = function () {
  if (
    typeof this.raw_path !== "undefined" &&
    this.raw_path !== null &&
    this.raw_path !== ""
  ) {
    var rawPath = escapeHtml(this.raw_path);
    rawPath = "#" + rawPath + "#";
    for (var i = 0; i < this.station_id_path.length; i++) {
      var relatedStationId = this.station_id_path[i];
      if (
        typeof this.station_name_path !== "undefined" &&
        this.station_name_path !== null
      ) {
        var relatedStationName = escapeHtml(this.station_name_path[i]);
        var relatedStationNameReplacement =
          '<a href="#" onclick="' +
          " var relatedStationLatestPacket = trackdirect._map.markerCollection.getStationLatestPacket(" +
          relatedStationId +
          ");" +
          " if (relatedStationLatestPacket !== null) {" +
          "     trackdirect.focusOnStation(" +
          relatedStationId +
          ", true);" +
          " } else {" +
          "     alert('Can not go to " +
          relatedStationName +
          ", station has not been heard for a long time.');" +
          " }" +
          ' return false;">' +
          relatedStationName +
          "</a>";

        rawPath = rawPath.replaceAll(
          "#" + relatedStationName + ",",
          "#" + relatedStationNameReplacement + ","
        );
        rawPath = rawPath.replaceAll(
          "#" + relatedStationName + "*",
          "#" + relatedStationNameReplacement + "*"
        );
        rawPath = rawPath.replaceAll(
          "#" + relatedStationName + ":",
          "#" + relatedStationNameReplacement + ":"
        );
        rawPath = rawPath.replaceAll(
          "#" + relatedStationName + "#",
          "#" + relatedStationNameReplacement + "#"
        );
        rawPath = rawPath.replaceAll(
          "," + relatedStationName + ",",
          "," + relatedStationNameReplacement + ","
        );
        rawPath = rawPath.replaceAll(
          "," + relatedStationName + "*",
          "," + relatedStationNameReplacement + "*"
        );
        rawPath = rawPath.replaceAll(
          "," + relatedStationName + ":",
          "," + relatedStationNameReplacement + ":"
        );
        rawPath = rawPath.replaceAll(
          "," + relatedStationName + "#",
          "," + relatedStationNameReplacement + "#"
        );
      }
    }
    rawPath = rawPath.replace(/#+$/, "");
    rawPath = rawPath.replace(/^#+/, "");
    var rawPathArray = rawPath.split(",");
    if (rawPathArray.length > 0) {
      var rawPath =
        rawPathArray[0] +
        " via " +
        rawPathArray.join(",").replace(rawPathArray[0] + ",", "");
    }
    return rawPath;
  }
  return null;
};
