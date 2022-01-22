/**
 * Class trackdirect.MarkerCreator
 * @param {trackdirect.models.Map} map
 */
trackdirect.MarkerCreator = function (map) {
  this._map = map;

  // Station id for the packet sequence that is currenly being added to the map
  this._currentPacketSequenceStationId = null;
};

/**
 * Add new packet to map
 * @param {object} packet
 * @param {boolean} tryToShowPacket
 * @return {int} markerIdKey
 */
trackdirect.MarkerCreator.prototype.addPacket = function (
  packet,
  tryToShowPacket
) {
  if (this.isBadPacket(packet)) {
    return null;
  }
  var markerIdKey = this._map.markerCollection.getMarkerIdKey(packet.marker_id);

  if (this._map.markerCollection.isExistingMarker(markerIdKey)) {
    var marker = this._map.markerCollection.getMarker(markerIdKey);
    if (
      marker.packet.is_moving == 1 &&
      packet.is_moving != 1
    ) {
      // If server for some reason decides to change move-type we keep the original moving since we have started to plot it
      // Server should not do this...
      packet.is_moving = 1;
    }
  } else {
    if (packet.packet_order_id == 2) {
      // Something is wrong, a packet should not have order id 2 if no marker exists
      packet.packet_order_id = 3; // Force first packet
    }
  }

  markerIdKeyToOverwrite = this._getMarkerIdKeyToOverwrite(packet);
  if (markerIdKeyToOverwrite !== null) {
    this._overwriteMarker(markerIdKeyToOverwrite, markerIdKey);
  }

  if (this._map.markerCollection.isPacketReplacingMarker(packet)) {
    this._replaceMarker(markerIdKey);
  }

  this._setCurrentPacketSequenceStationId(packet);
  this._convertLostMarkersToGhost(packet);
  this._connectToPreviousMarker(packet);

  marker = this._createMarker(packet);

  // Add to map sector and show it if that should be done
  this._map.addMarkerToMapSectors(markerIdKey, packet, tryToShowPacket);

  if (packet.overwrite == 1) {
    marker.overwrite = true; // Mark it to be overwritten
  }
  return markerIdKey;
};

/**
 * Should packet overwrite any previous marker?
 * If so the markerIdKey will be returned otherwise null
 * @param {object} packet
 * @return {int}
 */
trackdirect.MarkerCreator.prototype._getMarkerIdKeyToOverwrite = function (
  packet
) {
  var markerIdKey = this._map.markerCollection.getMarkerIdKey(packet.marker_id);
  if (this._map.markerCollection.isExistingMarker(markerIdKey)) {
    // This marker exists on map, overwrite if it is marked to be overwritten
    var marker = this._map.markerCollection.getMarker(markerIdKey);
    if (marker.overwrite == true && packet.overwrite == 0) {
      return markerIdKey;
    }
  } else {
    // If packet is stationary and station has another marker allready, check if it may be the same thing
    // It may be the same thing but different marker id's if it is more than 24h between packets
    // (collector only connects packets that has less than 24h apart from eachother)
    var prevMarker = this._map.markerCollection.getStationLatestMarker(
      packet.station_id
    );
    if (prevMarker !== null) {
      if (
        packet.is_moving == 0 &&
        packet.station_id == prevMarker.packet.station_id &&
        packet.timestamp - prevMarker.packet.timestamp > 86400 &&
        Math.round(prevMarker.packet.latitude * 100000) ==
          Math.round(packet.latitude * 100000) &&
        Math.round(prevMarker.packet.longitude * 100000) ==
          Math.round(packet.longitude * 100000) &&
        prevMarker.packet.symbol == packet.symbol &&
        prevMarker.packet.symbol_table == packet.symbol_table
      ) {
        return prevMarker.markerIdKey;
      }
    }
  }
  return null;
};

/**
 * Replace marker
 * Replace is bit different from overwrite:
 * - replace is just replacing the latest position, used for stationary when a new packet for the same position is received
 * - overwrite is used when only the latest packet has been added to map and we now want to add the history
 * @param {int} markerIdKey
 * @return {null}
 */
trackdirect.MarkerCreator.prototype._replaceMarker = function (markerIdKey) {
  if (this._map.markerCollection.isExistingMarker(markerIdKey)) {
    var marker = this._map.markerCollection.getMarker(markerIdKey);
    if (this._map.state.isMarkerInfoWindowOpen(marker)) {
      this._map.state.openInfoWindowForMarkerIdKey = markerIdKey;
    }

    // We hide old marker since we will just overwrite the variable which will not remove it from map
    marker.hide(0, false, false);
    marker.stopDirectionPolyline();
  }
};

/**
 * Prepare marker to be overwritten
 * @param {int} prevMarkerIdKey
 * @param {int} newMarkerIdKey
 * @return {null}
 */
trackdirect.MarkerCreator.prototype._overwriteMarker = function (
  prevMarkerIdKey,
  newMarkerIdKey
) {
  var prevMarker = this._map.markerCollection.getMarker(prevMarkerIdKey);
  if (this._map.state.isMarkerInfoWindowOpen(prevMarker)) {
    this._map.state.openInfoWindowForMarkerIdKey = newMarkerIdKey;
  }

  var markerLabel = prevMarker.label;
  var markerPolyLine =
    this._map.markerCollection.getMarkerPolyline(prevMarkerIdKey);
  var markerDotMarkers =
    this._map.markerCollection.getDotMarkers(prevMarkerIdKey);
  var markerOriginDashedPolyline =
    this._map.markerCollection.getMarkerDashedPolyline(prevMarkerIdKey);

  clearTimeout(prevMarker.toOldTimerId);
  if (markerDotMarkers != null) {
    for (var i = 0; i < markerDotMarkers.length; i++) {
      clearTimeout(markerDotMarkers[i].toOldTimerId);
    }
  }

  this._map.markerCollection.resetMarker(prevMarkerIdKey);
  if (this._map.oms) {
    this._map.oms.removeMarker(prevMarker);
  }

  if (
    prevMarker != null &&
    typeof prevMarker.packet.latitude != "undefined" &&
    typeof prevMarker.packet.longitude != "undefined"
  ) {
    this._map.markerCollection.removePostionMarkerId(
      prevMarker.packet.latitude,
      prevMarker.packet.longitude,
      prevMarkerIdKey
    );
    this._map.showTopLabelOnPosition(
      prevMarker.packet.latitude,
      prevMarker.packet.longitude
    );
  }

  // Note that the marker needs to be hidden after it has been removed from array
  // (otherwise it may be shown again before it is removed)
  prevMarker.hide(0, false, false);
  if (markerPolyLine !== null) {
    markerPolyLine.hide();
  }
  if (markerDotMarkers != null) {
    for (var i = 0; i < markerDotMarkers.length; i++) {
      markerDotMarkers[i].hide();
    }
  }
  if (markerOriginDashedPolyline !== null) {
    markerOriginDashedPolyline.hide();

    // Remove dashed polyline from related marker also
    if (
      typeof markerOriginDashedPolyline.relatedMarkerIdKey !== "undefined" &&
      markerOriginDashedPolyline.relatedMarkerIdKey !== null
    ) {
      var prevMarker = this._map.markerCollection.getMarker(
        markerOriginDashedPolyline.relatedMarkerIdKey
      );
      if (
        prevMarker !== null &&
        typeof prevMarker._relatedMarkerOriginDashedPolyLine !== "undefined"
      ) {
        prevMarker._relatedMarkerOriginDashedPolyLine = null;
      }
    }
  }

  prevMarker.hidePHGCircle();
  prevMarker.hideRNGCircle();

  if (prevMarker.directionPolyLine !== null) {
    prevMarker.directionPolyLine.stop();
  }
};

/**
 * Remember the station that we are currently working, if we receive a series of packet for a station
 * @param {object} packet
 */
trackdirect.MarkerCreator.prototype._setCurrentPacketSequenceStationId =
  function (packet) {
    if (packet.packet_order_id == 3) {
      this._currentPacketSequenceStationId = packet.station_id;
    }

    if (
      packet.packet_order_id == 2 &&
      this._currentPacketSequenceStationId === null
    ) {
      // Looks like we marked the start-packet as bad...
      this._currentPacketSequenceStationId = packet.station_id;
      packet.packet_order_id = 3;
    }

    if (packet.packet_order_id == 1) {
      this._currentPacketSequenceStationId = null;
    }
  };

/**
 * Create a new marker!
 * @param {object} packet
 */
trackdirect.MarkerCreator.prototype._createMarker = function (packet) {
  var markerIdKey = this._map.markerCollection.getMarkerIdKey(packet.marker_id);
  var prevmarker = this._map.markerCollection.getMarker(markerIdKey);
  this._map.state.currentMarkerZindex += 1;

  if (packet.packet_order_id == 1 || packet.is_moving == 0) {
    if (prevmarker !== null) {
      if (
        prevmarker.packet.latitude != packet.latitude &&
        prevmarker.packet.longitude != packet.longitude
      ) {
        this._map.markerCollection.removePostionMarkerId(
          prevmarker.latitude,
          prevmarker.longitude,
          markerIdKey
        );
        this._map.showTopLabelOnPosition(
          prevmarker.latitude,
          prevmarker.longitude
        );
      }
    }
    var marker = new trackdirect.models.Marker(packet, false, this._map);
    this._addInfoWindowClickListener(marker, true);
  } else {
    var marker = new trackdirect.models.Marker(packet, true, this._map);
    this._map.markerCollection.addDotMarker(markerIdKey, marker);
    this._addInfoWindowClickListener(marker, false);
  }
  marker.markerIdKey = markerIdKey;

  if (prevmarker !== null) {
    if (!this._map.markerCollection.isPacketReplacingMarker(packet)) {
      // We need to extend the marker polyline since this is not the first dotmarker
      this._extendTail(prevmarker, marker);
    } else {
      // update marker for the latest polyline point
      this._replaceTailMarker(markerIdKey);
    }
  }

  if (packet.packet_order_id == 1) {
    if (packet.hasDirectionSupport() && packet.hasConfirmedMapId()) {
      marker.directionPolyLine = new trackdirect.models.DirectionPolyline(
        marker,
        this._map
      );
    }
  }

  this._map.markerCollection.setMarker(markerIdKey, marker);

  if (!marker.isDotMarker()) {
    this._createMarkerLabel(marker);
    this._map.showTopLabelOnPosition(packet.latitude, packet.longitude);
  }

  return marker;
};

/**
 * Add listener for InfoWindow
 * @param {object} marker
 * @param {boolean} useOmsIfExists
 */
trackdirect.MarkerCreator.prototype._addInfoWindowClickListener = function (
  marker,
  useOmsIfExists
) {
  var me = this;
  if (useOmsIfExists && this._map.oms) {
    me._map.oms.addMarker(marker);
  } else if (typeof google === "object" && typeof google.maps === "object") {
    marker.addListener("click", function () {
      me._map.openMarkerInfoWindow(marker, false);
    });
  } else if (typeof L === "object") {
    marker.on("click", function () {
      me._map.openMarkerInfoWindow(marker, false);
    });
  }
};

/**
 * Convert marker to dot marker
 * @param {int} markerIdKey
 * @param {object} packet
 */
trackdirect.MarkerCreator.prototype._convertToDotMarker = function (
  markerIdKey,
  packet
) {
  // Check that marker has not allready been converted to dot-marker
  var dotMarker = this._map.markerCollection.getMarker(markerIdKey);
  if (dotMarker != null && dotMarker.showAsMarker) {
    dotMarker.stopDirectionPolyline();

    if (this._map.state.isMarkerInfoWindowOpen(dotMarker)) {
      this._map.state.openInfoWindowForMarkerIdKey = markerIdKey;
    }

    if (!this._map.state.isFilterMode) {
      if (
        this._map.getZoom() < trackdirect.settings.minZoomForMarkerPrevPosition
      ) {
        dotMarker.hide();
      }
    }

    var icon = this._getDotMarkerIcon(packet);
    dotMarker.setOpacity(1.0);
    dotMarker.setIcon(icon);
    if (typeof google === "object" && typeof google.maps === "object") {
      dotMarker.setOptions({ anchorPoint: null });
    }
    this._map.markerCollection.addDotMarker(markerIdKey, dotMarker);

    // Remove from oms
    if (this._map.oms) {
      this._map.oms.removeMarker(dotMarker);

      // markers that is not handled by oms need to have their own clicklistener
      var me = this;
      if (typeof google === "object" && typeof google.maps === "object") {
        dotMarker.addListener("click", function () {
          me._map.openMarkerInfoWindow(dotMarker, false);
        });
      } else if (typeof L === "object") {
        dotMarker.on("click", function () {
          me._map.openMarkerInfoWindow(dotMarker, false);
        });
      }
    }

    // Allways hide label for marker that is converted to dot-marker (we are not sure if label will still be used)
    if (this._map.markerCollection.hasMarkerLabel(markerIdKey)) {
      var markerLabel = this._map.markerCollection.getMarkerLabel(markerIdKey);
      markerLabel.hide();
    }
    dotMarker.hasLabel = false;

    // Mark that marker has been converted to dot marker
    dotMarker.showAsMarker = false;
  }
};

/**
 * Get dot marker icon
 * @param {object} packet
 * @return {object}
 */
trackdirect.MarkerCreator.prototype._getDotMarkerIcon = function (packet) {
  var colorId = trackdirect.services.stationColorCalculator.getColorId(packet);
  if (typeof google === "object" && typeof google.maps === "object") {
    var icon = {
      url:
        trackdirect.settings.baseUrl +
        trackdirect.settings.imagesBaseDir +
        "dotColor" +
        colorId +
        ".png",
      size: new google.maps.Size(12, 12),
      origin: new google.maps.Point(0, 0),
      anchor: new google.maps.Point(6, 6),
    };
  } else if (typeof L === "object") {
    var icon = L.icon({
      iconUrl:
        trackdirect.settings.baseUrl +
        trackdirect.settings.imagesBaseDir +
        "dotColor" +
        colorId +
        ".png",
      iconSize: [12, 12],
      iconAnchor: [6, 6],
      popupAnchor: [-3, -12],
    });
  }
  return icon;
};

/**
 * Remove existing related marker origin dashed polyline if it should no longer be used
 * @param {object} prevMarker
 * @param {int} newMarkerIdKey
 */
trackdirect.MarkerCreator.prototype._removeExistingRelatedMarkerOriginDashedPolyLine =
  function (prevMarker, newMarkerIdKey) {
    // We only connect confirmed and moving previous markers with longer length than 1 packet
    if (
      typeof prevMarker._relatedMarkerOriginDashedPolyLine !== "undefined" &&
      prevMarker._relatedMarkerOriginDashedPolyLine !== null
    ) {
      //
      // Check if it should be overwritten!
      // (If this marker allready has a related-origin-dashed-polyline and the owner marker is alone we exclude it from path)
      //
      var ownerMarkerIdKey =
        prevMarker._relatedMarkerOriginDashedPolyLine.ownerMarkerIdKey;
      var ownerMarker = this._map.markerCollection.getMarker(ownerMarkerIdKey);
      var isConfirmedMapId = true;
      if (
        ownerMarker !== null &&
        ownerMarker.packet.map_id != 1 &&
        ownerMarker.packet.map_id != 2 &&
        ownerMarker.packet.map_id != 12
      ) {
        isConfirmedMapId = false;
      }

      if (
        ownerMarkerIdKey != newMarkerIdKey &&
        (!isConfirmedMapId ||
          !this._map.markerCollection.hasDotMarkers(ownerMarkerIdKey)) &&
        ownerMarker.showAsMarker
      ) {
        // overwrite it!
        this._map.markerCollection.resetMarkerDashedPolyline(
          prevMarker._relatedMarkerOriginDashedPolyLine.ownerMarkerIdKey
        );
        prevMarker._relatedMarkerOriginDashedPolyLine.hide();
        prevMarker._relatedMarkerOriginDashedPolyLine = null;
      }
    }
  };

/**
 * Create related marker origin dashed polyline if possible
 * @param {object} prevMarker
 * @param {object} packet
 * @param {int} newMarkerIdKey
 */
trackdirect.MarkerCreator.prototype._createMarkerOriginDashedPolyLine =
  function (prevMarker, packet, newMarkerIdKey) {
    if (
      this._map.state.getClientTimestamp(prevMarker.packet.timestamp) <=
      this._map.state.getOldestAllowedPacketTimestamp()
    ) {
      // previous marker is to old, no need to connect them
      return;
    }

    if (
      typeof prevMarker._relatedMarkerOriginDashedPolyLine === "undefined" ||
      prevMarker._relatedMarkerOriginDashedPolyLine === null
    ) {
      var color = trackdirect.services.stationColorCalculator.getColor(packet);
      var newDashedPolyline = new trackdirect.models.DashedTailPolyline(
        color,
        this._map
      );
      newDashedPolyline.setMarkerIdKey(newMarkerIdKey); // Add alias for owner
      newDashedPolyline.setRelatedMarkerIdKey(prevMarker.markerIdKey);
      newDashedPolyline.addPacket(prevMarker.packet);
      newDashedPolyline.addPacket(packet);

      this._map.markerCollection.setMarkerDashedPolyline(
        newMarkerIdKey,
        newDashedPolyline
      );
      prevMarker._relatedMarkerOriginDashedPolyLine = newDashedPolyline;

      this._map.addMarkerToMapSectorInterval(
        newMarkerIdKey,
        prevMarker.packet.getLatLngLiteral(),
        packet.getLatLngLiteral()
      );
    }
  };

/**
 * Looks for lost markers and converts them to ghost markers
 * @param {object} newPacket
 */
trackdirect.MarkerCreator.prototype._convertLostMarkersToGhost = function (
  newPacket
) {
  // Look for lost markers if this is a confirmed and moving marker
  if (
    newPacket.packet_order_id != 2 &&
    newPacket.hasConfirmedMapId() &&
    newPacket.is_moving == 1 &&
    this._map.markerCollection.isPacketReplacingMarker(newPacket) == false
  ) {
    if (this._map.markerCollection.hasNonRelatedMovingMarkerId(newPacket)) {
      // Loop over all markers for this station
      list = this._map.markerCollection.getStationMarkerIdKeys(
        newPacket.station_id
      );
      for (var markerIdKey in list) {
        var newMarkerIdKey = this._map.markerCollection.getMarkerIdKey(
          newPacket.marker_id
        );
        var marker = this._map.markerCollection.getMarker(markerIdKey);
        if (
          marker !== null &&
          markerIdKey !== newMarkerIdKey &&
          marker.packet.is_moving == 1 &&
          marker.packet.timestamp <= newPacket.timestamp &&
          marker.packet.hasConfirmedMapId() &&
          marker.isSingleMovingMarker()
        ) {
          // This marker is considered lost
          // This is the CLIENT PART of the adaptive speed filter
          // If we have a confirmed previous marker but it has no dot-markers, we convert it to a ghost marker

          // If marker has a dashed polyline (it is a origin of another marker), that dashed polyline should be removed
          // Actually this should not happen (or it may happen for OBJECTS)
          if (this._map.markerCollection.hasRelatedDashedPolyline(marker)) {
            masterMarkerIdKey =
              this._map.markerCollection.getMarkerMasterMarkerKeyId(
                markerIdKey
              );
            if (
              masterMarkerIdKey !== markerIdKey &&
              this._map.markerCollection.isExistingMarker(masterMarkerIdKey) !==
                null
            ) {
              // Another packet is connected to this one with a dashed polyline, this marker is probably an OBJECT sent by several senders
              continue;
            } else {
              // This on the other hand should never happen...
              // but if it does the dashed polyline should be removed
              this._map.markerCollection.resetMarkerDashedPolyline(
                marker._relatedMarkerOriginDashedPolyLine.ownerMarkerIdKey
              );
              marker._relatedMarkerOriginDashedPolyLine.hide();
              marker._relatedMarkerOriginDashedPolyLine = null;
            }
          }

          marker.packet.map_id = 9; // Abnormal position (not releted to any previous or any newer positions)
          marker.setOpacity(0.5);
          marker.hasLabel = false;
          marker.hideLabel();
          marker.stopDirectionPolyline();

          if (!this._map.state.isGhostMarkersVisible) {
            marker.hide();
          }
        }
      }
    }
  }
};

/**
 * Get the latest markerIdKey to connect new marker to, regular polyline if possible, otherwise dashed polyline
 * @param {object} newPacket
 * @param {int} newMarkerIdKey
 * @return {int}
 */
trackdirect.MarkerCreator.prototype._getLatestStationMarkerToConnectTo =
  function (newPacket, newMarkerIdKey) {
    if (
      this._map.markerCollection.getStationLatestMovingMarkerIdKey(
        newPacket.station_id
      ) === newMarkerIdKey
    ) {
      // This markerId is known and is the latest, just go on and use it
      return newMarkerIdKey;
    }

    var latestPrevMarkerIdKey = null;
    var latestPrevMarkerIdKeyTimestamp = null;
    // Loop over all markers for this station

    var list = this._map.markerCollection.getStationMarkerIdKeys(
      newPacket.station_id
    );
    for (var markerIdKey in list) {
      var marker = this._map.markerCollection.getMarker(markerIdKey);
      if (marker !== null) {
        if (markerIdKey === newMarkerIdKey) {
          return markerIdKey;
        } else if (
          marker.packet.hasConfirmedMapId() &&
          marker.packet.is_moving == 1 &&
          marker.overwrite !== true &&
          marker.isSingleMovingMarker() == false &&
          (latestPrevMarkerIdKeyTimestamp === null ||
            latestPrevMarkerIdKeyTimestamp < marker.packet.timestamp)
        ) {
          // We exclude single packet markers from the same station since they will allways be converted to ghost-markers by server when found
          // (This is not allways true when we speak about objects with different stations)
          latestPrevMarkerIdKey = markerIdKey;
          latestPrevMarkerIdKeyTimestamp = marker.packet.timestamp;
        }
      }
    }
    return latestPrevMarkerIdKey;
  };

/**
 * Convert all stations previous markers to dot markers since a new packet has been received
 * @param {object} newPacket
 */
trackdirect.MarkerCreator.prototype._connectToPreviousMarker = function (
  newPacket
) {
  var newMarkerIdKey = this._map.markerCollection.getMarkerIdKey(
    newPacket.marker_id
  );
  // Create dot-marker for old position (is needed even if marker is new since same station may have other markers)
  if (
    newPacket.packet_order_id != 2 &&
    newPacket.is_moving == 1 &&
    this._map.markerCollection.isPacketReplacingMarker(newPacket) == false
  ) {
    var latestPrevMarkerIdKey = this._getLatestStationMarkerToConnectTo(
      newPacket,
      newMarkerIdKey
    );
    var latestPrevMarker = this._map.markerCollection.getMarker(
      latestPrevMarkerIdKey
    );
    if (latestPrevMarker !== null) {
      // Since we will add a new packet for this station any direction polylines should be stopped
      if (newPacket.hasConfirmedMapId()) {
        latestPrevMarker.stopDirectionPolyline();
      }

      if (latestPrevMarkerIdKey == newMarkerIdKey) {
        if (
          this._map.markerCollection.hasDashedPolyline(latestPrevMarkerIdKey) &&
          newPacket.hasConfirmedMapId()
        ) {
          // If previous marker is connected to a prev marker by a origin dashed polyline,
          // we need to convert that marker to a dot-marker also (this happens when the prev marker is a mapId 7)
          // We don't do this until our new markerId gets a packet with mapId 1 (some never get it and will be abandoned)
          var dashedPolyline =
            this._map.markerCollection.getMarkerDashedPolyline(
              latestPrevMarkerIdKey
            );
          var latestPrevRelatedMarkerIdKey = dashedPolyline.relatedMarkerIdKey;
          this._convertToDotMarker(latestPrevRelatedMarkerIdKey, newPacket);
        }

        // We can use the new packet here since it will only be used to get the correct color
        this._convertToDotMarker(latestPrevMarkerIdKey, newPacket);
      } else {
        // Connect it with previous polyline with a dashed polyline
        // Remember that we should create a origin dashed polyline even if new packet has mapId 7 since it may be converted to 1 later
        // If it wont't be converted to a mapId 1 the origin dashed polyline will be removed when next packet with mapId 1 or is received for this station
        this._removeExistingRelatedMarkerOriginDashedPolyLine(
          latestPrevMarker,
          newMarkerIdKey
        );
        this._createMarkerOriginDashedPolyLine(
          latestPrevMarker,
          newPacket,
          newMarkerIdKey
        );

        if (newPacket.hasConfirmedMapId()) {
          // We only convert previous packet to a dot-marker if this marker has mapId 1 (or equal)
          // We can use the new packet here since it will only be used to get the correct color
          this._convertToDotMarker(latestPrevMarkerIdKey, newPacket);
        }
      }
    }
  }
};

/**
 * Create label for marker
 * @param {trackdirect.models.Marker} marker
 */
trackdirect.MarkerCreator.prototype._createMarkerLabel = function (marker) {
  var position = marker.packet.getLatLngLiteral();

  if (this._map.markerCollection.hasMarkerLabel(marker.markerIdKey)) {
    // Just move existing label
    this._map.markerCollection.setMarkerLabelPosition(
      marker.markerIdKey,
      position
    );
  } else if (marker.packet.packet_order_id == 1) {
    if (marker.packet.getOgnRegistration() != null) {
      labelText = marker.packet.getOgnRegistration();
      if (marker.packet.getOgnCN() !== null) {
        labelText += " [" + marker.packet.getOgnCN() + "]";
      }
    } else {
      if (marker.packet.station_name == marker.packet.sender_name) {
        labelText = escapeHtml(marker.packet.station_name);
      } else {
        labelText =
          escapeHtml(marker.packet.station_name) +
          ' <span style="font-weight: normal;">(' +
          escapeHtml(marker.packet.sender_name) +
          ")</span>";
      }

      // Add operator in comment to label
      if (marker.packet.comment) {
        var opIndex = marker.packet.comment.indexOf("OP:");
        if (opIndex > -1) {
          opStr = marker.packet.comment.substring(opIndex + 3).replace(/^\s+/, "") + " ";
          opStr = opStr.substring(0, opStr.indexOf(" "));
          if (opStr.length <= 10 && opStr.length > 0) {
            labelText +=
              ' <span style="font-weight: normal;">[' +
              escapeHtml(opStr) +
              "]</span>";
          }
        }
      }
    }

    var markerLabel = new trackdirect.models.Label(
      {
        position: position,
        text: labelText,
      },
      this._map
    );
    this._map.markerCollection.setMarkerLabel(marker.markerIdKey, markerLabel);
  }
};

/**
 * Extend marker tail polyline with another position
 * @param {trackdirect.models.Marker} prevmarker
 * @param {trackdirect.models.Marker} newmarker
 */
trackdirect.MarkerCreator.prototype._extendTail = function (
  prevmarker,
  newmarker
) {
  if (
    this._map.state.getClientTimestamp(newmarker.packet.timestamp) <=
    this._map.state.getOldestAllowedPacketTimestamp()
  ) {
    // received packet is allready to old...
    return;
  }

  if (this._map.markerCollection.hasPolyline(newmarker.markerIdKey)) {
    var polyline = this._map.markerCollection.getMarkerPolyline(
      newmarker.markerIdKey
    );
    polyline.addMarker(newmarker);
  } else {
    if (
      this._map.state.getClientTimestamp(
        this._map.markerCollection.getMarker(newmarker.markerIdKey).packet.timestamp
      ) <= this._map.state.getOldestAllowedPacketTimestamp()
    ) {
      // previous marker is to old, no need to connect them
      return;
    } else {
      var color = trackdirect.services.stationColorCalculator.getColor(
        newmarker.packet
      );
      var newTailPolyline = new trackdirect.models.TailPolyline(
        color,
        this._map
      );
      newTailPolyline.setMarkerIdKey(newmarker.markerIdKey);
      newTailPolyline.addMarker(prevmarker);
      newTailPolyline.addMarker(newmarker);
      this._map.markerCollection.setMarkerPolyline(
        newmarker.markerIdKey,
        newTailPolyline
      );
    }
  }
};

/**
 * Replace latest marker in marker tail polyline
 * @param {int} markerIdKey
 */
trackdirect.MarkerCreator.prototype._replaceTailMarker = function (
  markerIdKey
) {
  if (this._map.markerCollection.hasPolyline(markerIdKey)) {
    var marker = this._map.markerCollection.getMarker(markerIdKey);
    var polylines = this._map.markerCollection.getMarkerPolyline(markerIdKey);
    var latestIndex = polylines.getPath().length - 1;
    if (latestIndex >= 0) {
      polylines.getPathItem(latestIndex).marker = marker;
    }
  }
};

/**
 * Return true if packet is bad (if it should not be added to map)
 * @param {trackdirect.models.Packet} markerCollection
 * @return {boolean}
 */
trackdirect.MarkerCreator.prototype.isBadPacket = function (packet) {
  if (
    typeof packet.latitude === "undefined" ||
    typeof packet.longitude === "undefined" ||
    packet.marker_id == null
  ) {
    return true;
  }
  var markerIdKey = this._map.markerCollection.getMarkerIdKey(packet.marker_id);
  if (this._map.markerCollection.isExistingMarker(markerIdKey)) {
    var marker = this._map.markerCollection.getMarker(markerIdKey);
    if (
      packet.packet_order_id == 1 &&
      this._currentPacketSequenceStationId == packet.station_id
    ) {
      // This is the last packet in an ongoing serie, do not mark this packet as bad
      return false;
    }
    if (packet.db == 0) {
      if (this._map.markerCollection.isDuplicate(packet)) {
        return true; // We think this is a duplicate
      }
    }
    if (
      packet.db == 1 &&
      marker.packet.db == 1 &&
      marker.packet.source === 0 &&
      packet.id === marker.packet.id
    ) {
      // For some reason we got the same packet again, duplicate!
      // (this may happen when filtering on a station with only non confirmed packets)
      return true;
    }

    if (marker.overwrite == true && packet.overwrite == 0) {
      return false;
    } else {
      if (marker.packet.timestamp >= packet.timestamp) {
        // It's important that we do not allow two packets with the same timestamp since they may be the same packet, which can cause wierd problems
        return true;
      }

      if (
        marker.packet.reported_timestamp !== null &&
        packet.reported_timestamp !== null &&
        Math.abs(marker.packet.reported_timestamp - packet.reported_timestamp) < 600
      ) {
        if (marker.packet.reported_timestamp > packet.reported_timestamp) {
          return true;
        }
      }
    }
  }

  if (packet.is_moving == 1) {
    var list = this._map.markerCollection.getStationMarkerIdKeys(
      packet.station_id
    );
    for (var relatedMarkerIdKey in list) {
      var relatedMarker =
        this._map.markerCollection.getMarker(relatedMarkerIdKey);
      // Do not add packet to map if other packet with earlier timestamp exists
      if (
        relatedMarker !== null &&
        relatedMarker.overwrite == false &&
        relatedMarker.packet.timestamp > packet.timestamp
      ) {
        return true;
      }
    }
  }

  return false;
};
