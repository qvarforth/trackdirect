trackdirect.services.dateFormatter = {
  /**
   * Returns the timestamp in a humen readable form (based on browser locale settings)
   * @param {int} timestamp
   * @param {boolean} includeTimeZone
   * @param {boolean} includeTime
   * @param {boolean} useLocalTimeZone
   * @return {string}
   */
  getDateString: function (
    timestamp,
    includeTimeZone,
    includeTime,
    useLocalTimeZone
  ) {
    includeTimeZone =
      typeof includeTimeZone !== "undefined" ? includeTimeZone : true;
    includeTime = typeof includeTime !== "undefined" ? includeTime : true;
    useLocalTimeZone =
      typeof useLocalTimeZone !== "undefined" ? useLocalTimeZone : true;
    var date = new Date(timestamp * 1000);

    if (useLocalTimeZone) {
      var theMoment = moment(date);
    } else {
      var theMoment = moment.utc(date);
    }

    if (!theMoment.isValid()) {
      return timestamp;
    }

    if (includeTime) {
      if (includeTimeZone) {
        return theMoment.format("L LTSZ");
      } else {
        return theMoment.format("L LTS");
      }
    } else {
      return theMoment.format("L");
    }
  },

  /**
   * Get timestamp age as human readable string
   * @param {int} timestamp
   * @return {string}
   */
  getAgeString: function (timestamp) {
    // get total seconds between the times
    var delta = Math.abs(Math.floor(Date.now() / 1000) - timestamp);

    // calculate (and subtract) whole days
    var days = Math.floor(delta / 86400);
    delta -= days * 86400;

    // calculate (and subtract) whole hours
    var hours = Math.floor(delta / 3600) % 24;
    delta -= hours * 3600;

    // calculate (and subtract) whole minutes
    var minutes = Math.floor(delta / 60) % 60;
    delta -= minutes * 60;

    // what's left is seconds
    var seconds = Math.floor(delta % 60);

    var timeAgoList = [];
    if (days > 1) {
      timeAgoList.push(days + " days");
    } else if (days > 0) {
      timeAgoList.push(days + " day");
    }
    if (hours > 1) {
      timeAgoList.push(hours + " hours");
    } else if (hours > 0) {
      timeAgoList.push(hours + " hour");
    }
    if (minutes > 1) {
      timeAgoList.push(minutes + " minutes");
    } else if (minutes > 0) {
      timeAgoList.push(minutes + " minute");
    }
    if (seconds == 1) {
      timeAgoList.push(seconds + " second");
    } else {
      timeAgoList.push(seconds + " seconds");
    }

    if (timeAgoList.length > 1) {
      return (
        timeAgoList.slice(0, timeAgoList.length - 1).join(", ") +
        " and " +
        timeAgoList[timeAgoList.length - 1]
      );
    } else {
      return timeAgoList[timeAgoList.length - 1];
    }
  },
};
