var Storage138 = function (data) {
	'use strict';


	var PRIVATE = {},
		PUBLIC = this;


	/**
	*
	* PUBLIC METHODS
	*
	**/
	PUBLIC.setStorage = function (obj) {
		for (var key in obj) {
			localStorage.setItem(key, obj[key]);
		}
	};

	PUBLIC.getStorage = function (key) {
		return localStorage.getItem(key);
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
storage.setStorage({
	chave1: 'value1',
	chave2: 'value2',
	chave3: 'value3'
});

// get
console.log('get', storage.getStorage('chave1') );

// rescue all
console.log('getAll', storage.rescue());
*/