trackdirect.services.symbolPathFinder = {
  /**
   * Returns icon http path
   *
   * - The default width and height is 24x24, if anything bigger is specified more space round the symbol will be added
   * - The deafult scale is 24x24, if anything else is specified the image will be scaled to that size
   *
   * @param {string} symbolTable
   * @param {string} symbol
   * @param {int} course
   * @param {int} width
   * @param {int} height
   * @param {int} scaleWidth
   * @param {int} scaleHeight
   * @return {string}
   */
  getFilePath: function (
    symbolTable,
    symbol,
    course,
    width,
    height,
    scaleWidth,
    scaleHeight
  ) {
    if (
      typeof symbol !== "undefined" &&
      typeof symbolTable !== "undefined" &&
      symbol !== null &&
      symbolTable !== null &&
      symbol.length >= 1 &&
      symbolTable.length >= 1
    ) {
      var symbolAsciiValue = symbol.charCodeAt(0);
      var symbolTableAsciiValue = symbolTable.charCodeAt(0);
    } else {
      var symbolAsciiValue = 125;
      var symbolTableAsciiValue = 47;
    }

    var sizeStrValue = "";
    if (width !== null && height !== null) {
      sizeStrValue = "-" + width + "x" + height;
    }

    var scaleStrValue = this._getIconFilePathScalePart(scaleWidth, scaleHeight);
    var courseStrValue = this._getIconFilePathCoursePart(course);
    var url =
      trackdirect.settings.markerSymbolBaseDir +
      "symbol-" +
      symbolAsciiValue +
      "-" +
      symbolTableAsciiValue +
      courseStrValue +
      sizeStrValue +
      scaleStrValue +
      ".png";

    return trackdirect.settings.baseUrl + url;
  },

  /**
   * Returns the course part of the icon http path
   *
   * @param {int} course
   * @return {string}
   */
  _getIconFilePathCoursePart: function (course) {
    var courseStrValue = "";
    if (course !== null) {
      var courseValue = Math.round(parseInt(course) / 10) * 10;
      while (courseValue > 360) {
        courseValue = courseValue - 360;
      }
      while (courseValue < 0) {
        courseValue = courseValue + 360;
      }
      courseStrValue = "-" + courseValue;
    }
    return courseStrValue;
  },

  /**
   * Returns the scale part of the icon http path
   * - The default scale is 24x24, if anything else is specified the image will be scaled to that size
   *
   * @param {int} scaleWidth
   * @param {int} scaleHeight
   * @return {string}
   */
  _getIconFilePathScalePart: function (scaleWidth, scaleHeight) {
    var scaleStrValue = "";
    if (scaleWidth !== null && scaleHeight !== null) {
      if (isHighDensity()) {
        scaleStrValue = "-scale" + scaleWidth * 2 + "x" + scaleHeight * 2;
      } else {
        scaleStrValue = "-scale" + scaleWidth + "x" + scaleHeight;
      }
    }
    return scaleStrValue;
  },
};
