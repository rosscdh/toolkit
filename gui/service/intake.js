angular.module('toolkit-gui')
.factory('intakeService', [
	'$timeout',
	'$resource',
	'$q',
	'API_BASE_URL',
	'smartRoutes',
	function($timeout, $resource, $q, API_BASE_URL, smartRoutes) {
	'use strict';

	var data = {
		'intakeList': null,
		'current': null
	};

	var schema = {
	  'type': 'array',
	  'title': 'Questions',
	  'format': 'tabs',
	  'items': {
		'title': 'Question',
		'headerTemplate': '{{i}} - {{self.name}}',
		'oneOf': [
		  {
			  "title": "Step",
			  "type": "object",
			  "id": "question",
			  "properties": {
			    "name": {
			      "type": "string",
			      "description": "Question to ask",
			      "minLength": 4
			    },
			    "help": {
			      "type": "string",
			      "description": "Help text to assist your client understand",
			      "minLength": 4
			    },
			    "Document field name": {
			      "type": "string",
			      "enum": ['#owner-name', '#address-street']
			    }
			  }
		  }
		]
	  }
	};

	var intakeList = [
		{ 'name': 'Example form' , 'slug': 'example', 'documents': [], 'schema': schema }
	];

	function intakeAPI() {
		return $resource( API_BASE_URL + 'intake/:intakeSlug', {}, {
			'list': { 'method': 'GET', 'headers': { 'Content-Type': 'application/json'/*, 'token': token.value*/ }, 'isArray': true },
			'get': { 'method': 'GET', 'headers': { 'Content-Type': 'application/json'/*, 'token': token.value*/ } },
			'create': { 'method': 'POST', 'headers': { 'Content-Type': 'application/json'/*, 'token': token.value*/ } },
			'update': { 'method': 'PATCH', 'headers': { 'Content-Type': 'application/json'/*, 'token': token.value*/ } },
			'del': { 'method': 'DELETE', 'headers': { 'Content-Type': 'application/json'/*, 'token': token.value*/ } }
		});
	}

	function findCurrent(intakeList) {
		var routeParams = smartRoutes.params();

		if(routeParams.slug) {
			for(var i=0;i<intakeList.length;i++) {
				if(intakeList[i].slug===routeParams.slug) {
					data.current = intakeList[i];
				}
			}
		}
	}

	return {
		'data': function() {
			return data;
		},

		'setCurrent': function( intake ) {
			data.current = intake;
		},
		/**
		 * subscribe - angular wrapper for pusher
		 * @param  {String}   channelName name of channel to subscribe to
		 * @param  {String}   eventName   [description]
		 * @param  {Function} callback    [description]
		 * @private
		 * @method				eventCaptured
		 * @memberof			PusherService
		 */
		'list': function () {
			var api = intakeAPI();
			var deferred = $q.defer();

			$timeout(function(){
				deferred.resolve( intakeList );
				data.intakeList = intakeList;

				findCurrent(intakeList);
			}, 1);
			/*
			api.list({},
				function success( intakeList ) {
					deferred.resolve(intakeList);
				},
				function error(err) {
					deferred.reject(err);
				}
			);
			*/

			return deferred.promise;
		}
	};
}]);