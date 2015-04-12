var Api318 = function (data) {
	'use strict';


	var PRIVATE = {},
		PUBLIC = this,
		W = window,
		D = document,
		LOCATION = W.location,
		HOSTNAME = LOCATION.hostname,
		PORT = LOCATION.port,
		CONNECTION;


	/**
	*
	* PRIVATE METHODS
	*
	**/
	PRIVATE.parse = function (str) {
		return JSON.parse(str);
	};

	PRIVATE.stringify = function (obj) {
		return JSON.stringify(obj);
	};

	PRIVATE.getURL = function () {
		var hostname = data.hostname ? data.hostname : HOSTNAME,
			port = data.port ? data.port : PORT;

		return 'ws://' + hostname + (((port != 80) && (port != 443)) ? ':' + port : '') + '/ws/' + data.userID;	
	};

	PRIVATE.getConnection = function(){

	}


	/**
	*
	* PUBLIC METHODS
	*
	**/
	PUBLIC.sendMessage = function (str) {
		var obj = {
				type: 'message',
				msg: String(str),
				mentions: String(str).match(/@[\w]*/g)
			};

		CONNECTION.send(PRIVATE.stringify(obj));
	};


	/**
	*
	* DEFINE URL AND SOCKET
	*
	**/
	PRIVATE.connection = null;

	CONNECTION = function(){
		if (!PRIVATE.connection){
			PRIVATE.connection = new WebSocket(PRIVATE.getURL());
		}
		return PRIVATE.connection
	}

	/**
	*
	* SEND GEOLOCATION
	*
	**/
	if (navigator.geolocation) {
		var lat,
			lon,
			geo;

		setInterval(function(){
			navigator.geolocation.getCurrentPosition(function (position) {
			  	lat = position.coords.latitude;
				lon = position.coords.longitude;
				geo = JSON.stringify({latitude: lat, longitude: lon, type: 'position'});

				CONNECTION.send(geo);
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
	CONNECTION.onmessage = function(evt) {
		console.log(evt);

      	if (data.onMsgCallback) {
      		data.onMsgCallback(evt);
    	}
    };

  CONNECTION.onclose = function(evt) {
    	console.log('Connection closed');
			PRIVATE.connection = null;
  };


  /**
	*
	* RETURN ALL PUBLIC METHODS
	*
	**/
	return PUBLIC;
};

// var t = new Api318({
// 	userID: 'fulano',
// 	host: '172.16.5.182',
// 	port: 8888,
//  onMsgCallback:
// });
