if (!Date.now) {
  Date.now = function () {
    return new Date().getTime();
  };
}

function escapeRegExp(str) {
  return str.replace(/[\-\[\]\/\{\}\(\)\*\+\?\.\\\^\$\|]/g, "\\$&");
}

String.prototype.replaceAll = function (search, replacement) {
  var target = this;
  return target.replace(new RegExp(escapeRegExp(search), "gi"), replacement);
};

function isNumeric(n) {
  return !isNaN(parseFloat(n)) && isFinite(n);
}

Number.prototype.mod = function (n) {
  return ((this % n) + n) % n;
};

function isDate(str) {
  var d = new Date(str);
  var now = new Date();
  if (Object.prototype.toString.call(d) === "[object Date]") {
    if (isNaN(d.getTime())) {
      return false;
    } else {
      if (d.getTime() > 0) {
        return true;
      } else {
        return false;
      }
    }
  } else {
    return false;
  }
}

if (!Array.prototype.fill) {
  Array.prototype.fill = function (value) {
    // Steps 1-2.
    if (this == null) {
      throw new TypeError("this is null or not defined");
    }

    var O = Object(this);

    // Steps 3-5.
    var len = O.length >>> 0;

    // Steps 6-7.
    var start = arguments[1];
    var relativeStart = start >> 0;

    // Step 8.
    var k =
      relativeStart < 0
        ? Math.max(len + relativeStart, 0)
        : Math.min(relativeStart, len);

    // Steps 9-10.
    var end = arguments[2];
    var relativeEnd = end === undefined ? len : end >> 0;

    // Step 11.
    var final =
      relativeEnd < 0
        ? Math.max(len + relativeEnd, 0)
        : Math.min(relativeEnd, len);

    // Step 12.
    while (k < final) {
      O[k] = value;
      k++;
    }

    // Step 13.
    return O;
  };
}

if (!Array.prototype.indexOf) {
  Array.prototype.indexOf = function (elt /*, from*/) {
    var len = this.length;
    var from = Number(arguments[1]) || 0;
    from = from < 0 ? Math.ceil(from) : Math.floor(from);

    if (from < 0) from += len;

    for (; from < len; from++) {
      if (from in this && this[from] === elt) return from;
    }
    return -1;
  };
}

if (typeof String.prototype.endsWith !== "function") {
  String.prototype.endsWith = function (suffix) {
    return this.indexOf(suffix, this.length - suffix.length) !== -1;
  };
}

if (!String.prototype.trim) {
  (function () {
    // Make sure we trim BOM and NBSP
    var rtrim = /^[\s\uFEFF\xA0]+|[\s\uFEFF\xA0]+$/g;
    String.prototype.trim = function () {
      return this.replace(rtrim, "");
    };
  })();
}

if (!Object.keys) {
  Object.keys = function (obj) {
    var keys = [],
      k;
    for (k in obj) {
      if (Object.prototype.hasOwnProperty.call(obj, k)) {
        keys.push(k);
      }
    }
    return keys;
  };
}

if (!Date.prototype.toISOString) {
  (function () {
    function pad(number) {
      var r = String(number);
      if (r.length === 1) {
        r = "0" + r;
      }
      return r;
    }

    Date.prototype.toISOString = function () {
      return (
        this.getUTCFullYear() +
        "-" +
        pad(this.getUTCMonth() + 1) +
        "-" +
        pad(this.getUTCDate()) +
        "T" +
        pad(this.getUTCHours()) +
        ":" +
        pad(this.getUTCMinutes()) +
        ":" +
        pad(this.getUTCSeconds()) +
        "." +
        String((this.getUTCMilliseconds() / 1000).toFixed(3)).slice(2, 5) +
        "Z"
      );
    };
  })();
}

// Returnes true if we are in a iframe
function inIframe() {
  try {
    return window.self !== window.top;
  } catch (e) {
    return true;
  }
}

/**
 * Returnes true if screen has high density
 * @return boolean
 */
function isHighDensity() {
  return (
    (window.matchMedia &&
      (window.matchMedia(
        "only screen and (min-resolution: 124dpi), only screen and (min-resolution: 1.3dppx), only screen and (min-resolution: 48.8dpcm)"
      ).matches ||
        window.matchMedia(
          "only screen and (-webkit-min-device-pixel-ratio: 1.3), only screen and (-o-min-device-pixel-ratio: 2.6/2), only screen and (min--moz-device-pixel-ratio: 1.3), only screen and (min-device-pixel-ratio: 1.3)"
        ).matches)) ||
    (window.devicePixelRatio && window.devicePixelRatio > 1.3)
  );
}

/**
 * htmlspecialchars equivalent
 * @param {string} text
 * @return string
 */
function escapeHtml(text) {
  if (typeof text === "undefined" || text == null) {
    return null;
  }

  var map = {
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    '"': "&quot;",
    "'": "&#039;",
  };
  return text.replace(/[&<>"']/g, function (m) {
    return map[m];
  });
}
