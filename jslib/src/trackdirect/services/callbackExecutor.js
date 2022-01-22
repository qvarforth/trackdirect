trackdirect.services.callbackExecutor = {
  /** @type {object} */
  settings: {
    minTimeBeforeSleep: 30, // in ms
  },

  /** @type {boolean} */
  _running: false,

  /** @type {int} */
  _lastSleepTimestamp: 0,

  /** @type {object} */
  _lastAddedUniqueCallback: null,

  /** @type {array} */
  _lowPriorityQueue: [],
  _normalPriorityQueue: [],
  _highPriorityQueue: [],

  /**
   * Add a call to the execution queue
   * @param {object} thisObj
   * @param {function} callback
   * @param {array} argsArray
   * @return {trackdirect.services.callbackExecutor}
   */
  add: function (thisObj, callback, argsArray) {
    var callBackString = callback.toString() + ":" + argsArray.toString();
    this._lastAddedUniqueCallback = callBackString;

    this._normalPriorityQueue.push(function () {
      callback.apply(thisObj, argsArray);
      trackdirect.services.callbackExecutor._next();
    });

    this.start();
    return this;
  },

  /**
   * Add a call to the execution queue if it is unique
   * @param {object} thisObj
   * @param {function} callback
   * @param {array} argsArray
   * @return {trackdirect.services.callbackExecutor}
   */
  addIfUnique: function (thisObj, callback, argsArray) {
    var callBackString = callback.toString() + ":" + argsArray.toString();
    if (this._lastAddedUniqueCallback == callBackString) {
      return this;
    }
    this._lastAddedUniqueCallback = callBackString;

    this._normalPriorityQueue.push(function () {
      callback.apply(thisObj, argsArray);
      trackdirect.services.callbackExecutor._next();
    });

    this.start();
    return this;
  },

  /**
   * Add a call to the execution queue, and give it priority over regular calls
   * @param {object} thisObj
   * @param {function} callback
   * @param {array} argsArray
   * @return {trackdirect.services.callbackExecutor}
   */
  addWithPriority: function (thisObj, callback, argsArray) {
    this._highPriorityQueue.push(function () {
      callback.apply(thisObj, argsArray);
      trackdirect.services.callbackExecutor._next();
    });

    this.start();
    return this;
  },

  /**
   * Add a call to the execution queue, and give it lower priority than regular calls
   * @param {object} thisObj
   * @param {function} callback
   * @param {array} argsArray
   * @return {trackdirect.services.callbackExecutor}
   */
  addWithLowPriority: function (thisObj, callback, argsArray) {
    this._lowPriorityQueue.push(function () {
      callback.apply(thisObj, argsArray);
      trackdirect.services.callbackExecutor._next();
    });

    this.start();
    return this;
  },

  /**
   * Start the execution
   * @return {trackdirect.services.callbackExecutor}
   */
  start: function () {
    if (!this._running) {
      this._next();
    }
    return this;
  },

  /**
   * Execute the first call in queue when ready
   */
  _next: function () {
    var secondsSinceLastSleep = Date.now() - this._lastSleepTimestamp;
    if (secondsSinceLastSleep > this.settings.minTimeBeforeSleep) {
      // Sleep 1ms after some ms, to avoid browser freeze
      // We also count recursive calls since last sleep to avoid the error: Maximum call stack size exceeded
      this._lastSleepTimestamp = Date.now();
      var me = this;
      setTimeout(function () {
        me._dequeue();
      }, 1);
    } else {
      this._dequeue();
    }
  },

  /**
   * Execute the first call in queue
   */
  _dequeue: function () {
    var shift = this._highPriorityQueue.shift();
    if (shift) {
      this._running = true;
      shift();
      return;
    }

    shift = this._normalPriorityQueue.shift();
    if (shift) {
      this._running = true;
      shift();
      return;
    }

    shift = this._lowPriorityQueue.shift();
    if (shift) {
      this._running = true;
      shift();
      return;
    }

    this._running = false;
  },
};
