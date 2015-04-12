var Storage138 = function (data) {
	'use strict';


	var PRIVATE = {},
		PUBLIC = this;


	/**
	*
	* PUBLIC METHODS
	*
	**/
	PUBLIC.setStorage = function (key, value) {
		localStorage.setItem(key, JSON.stringify(value));
	};

	PUBLIC.getStorage = function (key) {
		return JSON.parse(localStorage.getItem(key));
	};

	PUBLIC.rescue = function () {
		var obj = {};

		for (var i in localStorage) {
			obj[i] = localStorage[i];
		};

		return obj;
	};


	/**
	*
	* RETURN
	*
	**/
	return PUBLIC;
};

/*
## SAMPLE ##


// instance
var storage = new Storage138();

// set
storage.setStorage('user', {ps: 123, tt: 432});

// get
console.log('get', storage.getStorage('user') );

// // rescue all
console.log('getAll', storage.rescue());
*/