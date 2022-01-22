/**
 * Class trackdirect.Websocket
 * @param {string} wsServerUrl
 */
trackdirect.Websocket = function (wsServerUrl) {
  this._wsServerUrl = wsServerUrl;
  this._init();

  this._state = this.State.CONNECTING;
  this._emitEventListeners("state-change");

  // Call the parent constructor
  this._instance = new WebSocket(this._wsServerUrl);

  var me = this;
  this._instance.onopen = function (evt) {
    me._onOpen(evt);
  };
  this._instance.onclose = function (evt) {
    me._onClose(evt);
  };
  this._instance.onmessage = function (evt) {
    me._onMessage(evt);
  };
  this._instance.onerror = function (evt) {
    me._onError(evt);
  };
};

/**
 * Init object
 */
trackdirect.Websocket.prototype._init = function () {
  this._instance = null;
  this._eventListeners = {};
  this._lastSentPositionRequest = "";
  this._state = 0;
  this._lastMessageTimestamp = null;
  this._queue = [];
  this._running = false;
  this._sendPositionRequestIntervalId = null;

  this.State = {
    CONNECTING: 0, // Not connected!
    CONNECTED: 1,
    CLOSING: 2, // Not connected!
    CLOSED: 3, // Not connected!
    ERROR: 4, // Not connected!
    LOADING: 5, // Loading history from database
    LOADING_DONE: 6,
    LISTENING_APRSIS: 7, // Listening on APRS-IS Feed
    CONNECTING_APRSIS: 8,
    IDLE: 9,
    INACTIVE: 10,
  };
};

/**
 * Send data
 * @param {string} data
 */
trackdirect.Websocket.prototype.send = function (data) {
  this._instance.send(data);
};

/**
 * Close websocket connection
 */
trackdirect.Websocket.prototype.close = function () {
  this._instance.close();
};

/**
 * Get current state of websocket connection
 * @return {int}
 */
trackdirect.Websocket.prototype.getState = function () {
  return this._state;
};

/**
 * Clear the last sent filter cache
 */
trackdirect.Websocket.prototype.clearLastSentPositionRequest = function () {
  this._lastSentPositionRequest = "";
};

/**
 * Clear the last sent filter cache
 */
trackdirect.Websocket.prototype.isPositionRequestSent = function () {
  if (this._lastSentPositionRequest != "") {
    return true;
  } else {
    return false;
  }
};

/**
 * Send new filter request
 * @param {array} list
 * @param {int} historyMinutes
 * @return {boolean}
 */
trackdirect.Websocket.prototype.doSendFilterRequest = function (
  list,
  historyMinutes,
  referenceTime
) {
  var request = {};
  request.payload_request_type = 4;
  request.list = list;
  request.minutes = historyMinutes;
  if (referenceTime != "") {
    request.time = parseInt(referenceTime, 10);
  } else {
    request.time = null;
  }
  return this._addToSendQueue(request);
};

/**
 * Send new filter request by names
 * @param {array} list
 * @param {int} historyMinutes
 * @return {boolean}
 */
trackdirect.Websocket.prototype.doSendFilterRequestByName = function (
  namelist,
  historyMinutes,
  referenceTime
) {
  var request = {};
  request.payload_request_type = 8;
  request.namelist = namelist;
  request.minutes = historyMinutes;
  if (referenceTime != "") {
    request.time = parseInt(referenceTime, 10);
  } else {
    request.time = null;
  }
  return this._addToSendQueue(request);
};

/**
 * Send station request
 * @param {int} stationId
 * @param {int} historyMinutes
 * @param {string} referenceTime
 * @return {boolean}
 */
trackdirect.Websocket.prototype.doSendCompleteStationRequest = function (
  stationId,
  historyMinutes,
  referenceTime
) {
  var request = {};
  request.payload_request_type = 7;
  request.station_id = stationId;
  request.minutes = historyMinutes;
  if (referenceTime != "") {
    request.time = parseInt(referenceTime, 10);
  } else {
    request.time = null;
  }
  return this._addToSendQueue(request);
};

/**
 * Send new stop filter request
 * @param {int} stationId
 * @return {boolean}
 */
trackdirect.Websocket.prototype.doSendStopFilterRequest = function (stationId) {
  var request = {};
  request.payload_request_type = 6;
  request.station_id = stationId;
  return this._addToSendQueue(request);
};

/**
 * Send new position request
 * @param {float} neLat
 * @param {float} neLng
 * @param {float} swLat
 * @param {float} swLng
 * @param {int} historyMinutes
 * @param {string} referenceTime
 * @param {boolean} onlyRequestLatestPacket
 * @return {boolean}
 */
trackdirect.Websocket.prototype.doSendNewPositionRequest = function (
  neLat,
  neLng,
  swLat,
  swLng,
  historyMinutes,
  referenceTime,
  onlyRequestLatestPacket
) {
  var request = {};
  request.payload_request_type = 1;
  request.neLat = neLat;
  request.neLng = neLng;
  request.swLat = swLat;
  request.swLng = swLng;
  request.minutes = historyMinutes;
  if (referenceTime != "") {
    request.time = parseInt(referenceTime, 10);
  } else {
    request.time = null;
  }


  if (onlyRequestLatestPacket) {
    request.onlyLatestPacket = 1;
  } else {
    request.onlyLatestPacket = 0;
  }

  var requestStr = JSON.stringify(request);
  if (requestStr != this._lastSentPositionRequest) {
    this._lastSentPositionRequest = requestStr;

    if (this._sendPositionRequestIntervalId !== null) {
      clearInterval(this._sendPositionRequestIntervalId);
    }

    if (this._addToSendQueue(request)) {
      var me = this;
      this._sendPositionRequestIntervalId = window.setInterval(function () {
        // Real-time update functionality may discard packets during high load,
        // so it is good to send an extra update request now and then
        request.payload_request_type = 11;
        if (me._lastSentPositionRequest == requestStr) {
          me._addToSendQueue(request);
        }
      }, 60 * 1000);
      return true;
    }
    return false;
  } else {
    // No need to send this request...
    return true;
  }
};

/**
 * Add new event listener
 * @param {string} event
 * @param {string} handler
 */
trackdirect.Websocket.prototype.addListener = function (event, handler) {
  if (!(event in this._eventListeners)) {
    this._eventListeners[event] = [];
  }
  this._eventListeners[event].push(handler);
};

/**
 * On open
 * @param {string} evt
 */
trackdirect.Websocket.prototype._onOpen = function (evt) {
  // We still consider this to be "connecting", first when server says it ready we consider us connected
  this._state = this.State.CONNECTING;
  this._emitEventListeners("state-change");
};

/**
 * On close
 * @param {string} evt
 */
trackdirect.Websocket.prototype._onClose = function (evt) {
  this._state = this.State.CLOSED;
  this._emitEventListeners("state-change");
};

/**
 * On error
 * @param {string} evt
 */
trackdirect.Websocket.prototype._onError = function (evt) {
  this._state = this.State.ERROR;
  this._emitEventListeners("state-change");
};

/**
 * On message
 * @param {string} evt
 */
trackdirect.Websocket.prototype._onMessage = function (evt) {
  this._lastMessageTimestamp = Math.floor(Date.now() / 1000);

  // We skip try-catch since it affects performance
  var packet = JSON.parse(evt.data);

  // Add to queue to make sure packets are handled in order
  trackdirect.services.callbackExecutor.add(this, this._handleMessage, [
    packet,
  ]);
};

/**
 * Handle message
 * @param {object} packet
 */
trackdirect.Websocket.prototype._handleMessage = function (packet) {
  switch (packet.payload_response_type) {
    case 1:
      this._emitEventListeners("aprs-packet", packet.data);
      this._emitEventListeners("aprs-packet-payload-done");
      break;

    case 2:
      for (
        i = 0;
        typeof packet.data !== "undefined" && i < packet.data.length;
        i++
      ) {
        this._emitEventListeners("aprs-packet", packet.data[i]);
      }
      this._emitEventListeners("aprs-packet-payload-done");
      break;

    case 5:
      this._emitEventListeners("filter-response", packet.data);
      this._emitEventListeners("aprs-packet-payload-done");
      break;

    case 41:
      this._emitEventListeners("server-timestamp-response", packet.data);
      break;

    case 31:
      this._state = this.State.LISTENING_APRSIS;
      this._emitEventListeners("state-change");
      break;

    case 32:
      this._state = this.State.LOADING;
      this._emitEventListeners("state-change");
      break;

    case 33:
      this._state = this.State.IDLE;
      this._emitEventListeners("state-change");
      break;

    case 34:
      this._state = this.State.CONNECTING_APRSIS;
      this._emitEventListeners("state-change");
      break;

    case 35:
      this._state = this.State.LOADING_DONE;
      this._emitEventListeners("state-change");
      break;

    case 36:
      this._state = this.State.INACTIVE;
      this._emitEventListeners("state-change");
      this.clearLastSentPositionRequest();
      break;

    case 40:
      this._emitEventListeners("reset");
      break;

    case 42:
      this.clearLastSentPositionRequest();
      this._state = this.State.CONNECTED;
      this._emitEventListeners("state-change");
      break;
  }

  return true;
};

/**
 * Add object to send queue
 * @param {object} request
 * @return {boolean}
 */
trackdirect.Websocket.prototype._addToSendQueue = function (request) {
  if (this.readyState > 1) {
    return false;
  }

  var currentTs = Math.floor(Date.now() / 1000);
  if (
    this._lastMessageTimestamp !== null &&
    this._lastMessageTimestamp < currentTs - 60
  ) {
    // We havn't heard anything from server in 60s, server should send a message every 10s,
    // we better close the connection and force user of this class to reconnect
    this.close(); // This should trigger the onClose event which should reset the map
    return false;
  }

  var me = this;
  this._queue.push(function () {
    var data = JSON.stringify(request);
    if (data != null) {
      me.send(data);
    }
    me._dequeue();
  });
  this._start();
  return true;
};

/**
 * Start the execution
 */
trackdirect.Websocket.prototype._start = function () {
  if (!this._running) {
    this._dequeue();
  }
};

/**
 * Execute the first call in queue
 * @return {function}
 */
trackdirect.Websocket.prototype._dequeue = function () {
  this._running = true;
  var me = this;
  setTimeout(function () {
    if (me._instance.readyState === 1) {
      // Open
      var shift = me._queue.shift();
      if (shift) {
        shift();
      } else {
        me._running = false;
      }
      return;
    } else if (me._instance.readyState > 1) {
      // Closed (or closing)
      me._running = false;
      return;
    } else {
      // Probably on the way to open, just wait
      me._dequeue();
    }
  }, 5); // wait 5 milisecond for the connection...
};

/**
 * Call all listeners that are listening on specified event
 * @param {string} event
 * @param {string} arg
 */
trackdirect.Websocket.prototype._emitEventListeners = function (event, arg) {
  if (
    typeof this._eventListeners !== "undefined" &&
    event in this._eventListeners
  ) {
    for (var i = 0; i < this._eventListeners[event].length; i++) {
      this._eventListeners[event][i](arg);
    }
  }
};
