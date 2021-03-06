var Api138 = function(data) {
  'use strict';


  var PRIVATE = {},
    PUBLIC = this,
    W = window,
    D = document,
    LOCATION = W.location,
    HOSTNAME = LOCATION.host,
    PORT = LOCATION.port,
    getConnection;


  /**
   *
   * PRIVATE METHODS
   *
   **/
  PRIVATE.getURL = function() {
    var hostname = data.host ? data.host : HOSTNAME
    return 'ws://' + hostname + '/ws/' + data.userID;
  };

  PRIVATE.con = null;


  /**
   *
   * PUBLIC METHODS
   *
   **/
  PUBLIC.sendMessage = function(str) {
    var obj = {
      type: 'message',
      msg: String(str),
      mentions: String(str).match(/@[\w]*/g)
    };

    getConnection().send(JSON.stringify(obj));
  };

  PUBLIC.timeAgo = function(timestamp) {
    return jQuery.timeago(timestamp * 1000);
  };

  PUBLIC.connection = function() {
    return CONNECTION;
  };


  /**
   *
   * DEFINE URL AND SOCKET
   *
   **/

  PRIVATE.con = null;
  getConnection = function() {
    if (!PRIVATE.con) {
      PRIVATE.con = new WebSocket(PRIVATE.getURL());
      PRIVATE.con.Origin = "http://" + (data.host ? data.host : HOSTNAME);
    }
    return PRIVATE.con;
  };

  /**
   *
   * SEND GEOLOCATION
   *
   **/
  if (navigator.geolocation) {
    setInterval(function() {
      navigator.geolocation.getCurrentPosition(function(position) {
        var lat = position.coords.latitude,
          lon = position.coords.longitude,
          geo = JSON.stringify({
            latitude: lat,
            longitude: lon,
            type: 'position'
          });
        getConnection().send(geo);
      });
    }, 5000);


  } else {
    alert('API Geolocation not found');
  }


  /**
   *
   * MESSAGES
   *
   **/
  getConnection().onmessage = function(evt) {
    if (data.onMsgCallback) {
      data.onMsgCallback(JSON.parse(evt.data));
    }
  };

  getConnection().onclose = function(evt) {
    localStorage.clear();
    console.log('Connection closed');
    PRIVATE.con = null;
  };


  /**
   *
   * RETURN ALL PUBLIC METHODS
   *
   **/
  return PUBLIC;
};
