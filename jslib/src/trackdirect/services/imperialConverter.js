trackdirect.services.imperialConverter = {
  /**
   * Convert km to miles (or km/h to mph)
   * @param {float} value
   * @return float
   */
  convertKilometerToMile: function (value) {
    return value * 0.621371192;
  },

  /**
   * Convert meter per second to miles per second
   * @param {float} value
   * @return float
   */
  convertMpsToMph: function (value) {
    return value * 2.23693629;
  },

  /**
   * Convert meter to feet
   * @param {float} value
   * @return float
   */
  convertMeterToFeet: function (value) {
    return value * 3.2808399;
  },

  /**
   * Convert meter to yard
   * @param {float} value
   * @return float
   */
  convertMeterToYard: function (value) {
    return value * 1.0936133;
  },

  /**
   * Convert mm to inches
   * @param {float} value
   * @return float
   */
  convertMmToInch: function (value) {
    return value * 0.0393700787;
  },

  /**
   * Convert celcius to fahrenheit
   * @param {float} value
   * @return float
   */
  convertCelciusToFahrenheit: function (value) {
    return value * (9 / 5) + 32;
  },

  /**
   * Convert hPa/mbar to mmhg
   * @param {float} value
   * @return float
   */
  convertMbarToMmhg: function (value) {
    return value * 0.75006375541921;
  },
};
