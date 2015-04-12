var Api138 = function(data) {
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
	PRIVATE.parse = function(str) {
		return JSON.parse(str);
	};

	PRIVATE.stringify = function(obj) {
		return JSON.stringify(obj);
	};

	PRIVATE.getURL = function() {
		var hostname = data.host ? data.host : HOSTNAME,
			port = data.port ? data.port : PORT;

		return 'ws://' + hostname + (((port != 80) && (port != 443)) ? ':' + port : '') + '/ws/' + data.userID;
	};


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

		CONNECTION.send(PRIVATE.stringify(obj));
	};

	PUBLIC.timeAgo = function (timestamp) {
		return jQuery.timeago(timestamp * 1000);
	}


	/**
	 *
	 * DEFINE URL AND SOCKET
	 *
	 **/


	CONNECTION = new WebSocket(PRIVATE.getURL());


	/**
	 *
	 * SEND GEOLOCATION
	 *
	 **/
	if (navigator.geolocation) {
		var lat,
			lon,
			geo;

		setInterval(function() {
			navigator.geolocation.getCurrentPosition(function(position) {
				lat = position.coords.latitude;
				lon = position.coords.longitude;
				geo = JSON.stringify({
					latitude: lat,
					longitude: lon,
					type: 'position'
				});

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
		if (data.onMsgCallback) {
			data.onMsgCallback(JSON.parse(evt.data));
		}
	};

	CONNECTION.onclose = function(evt) {
		console.log('Connection closed');
	};


	/**
	 *
	 * RETURN ALL PUBLIC METHODS
	 *
	 **/
	return PUBLIC;
};