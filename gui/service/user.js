angular.module('toolkit-gui').factory('userService',[
	'$q',
	'$resource',
	'API_BASE_URL',
	function( $q, $resource, API_BASE_URL ) {
		'use strict';
		var user = {
			'data': {
				'items': []
			},
			'current': {}
		};

		function userResource() {
			// get API resource
			return $resource( API_BASE_URL + '/api/matter/:mid/user/:id', {}, {
					'get': { 'method': 'GET', 'headers': { 'Content-Type': 'application/json'/*, 'token': token.value*/ }, 'isArray': true },
					'list': { 'method': 'GET', 'headers': { 'Content-Type': 'application/json'/*, 'token': token.value*/ } }
				});
		}

		return {
			'data': function() {
				return user;
			},

			'setCurrent': function( userData ) {
				user.current = userData;

				//debugger;
				if(Raven) {
					Raven.setUser(userData);
				}

				//user.current.user_class='customer';
			},

			'get': function( /*uid*/ ) {
				var api = userResource();
				// append/update users in user.data.items
				var deferred = $q.defer();

				api.get( {},
					function success( /*result*/ ) {
						deferred.resolve();
					},
					function error( /*err*/ ) {
						deferred.reject();
					}
				);

				return deferred.promise;
			},

			'list': function( /**/ ) {
				// Retrieve a list of users
			},

			'invite': function( /*details*/ ) {
				// Send invitation
			}
		};
	}
]);