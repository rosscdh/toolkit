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

		/**
		 * calculatePermissions - given the current user profile and the lawyer profile allocate permissions
		 * @param  {Object} user   User object, representing the current user
		 * @param  {Object} lawyer User object, representing the lawyer who created this workspace
		 */
		function calculatePermissions( user, lawyer ) {
			var permissions = {
				'category': { 'post': false, 'put': false, 'delete': false },
				'matterItem': { 'post': false, 'put': false, 'delete': false },
			};

			if( user.url===lawyer.url ) {
				permissions.category = { 'post': true, 'put': true, 'delete': true };
			}

			if( user.user_class === "lawyer" ) {
				permissions.matterItem = { 'post': true, 'put': true, 'delete': true };
			}

			return permissions;
		}

		return {
			'data': function() {
				return user;
			},

			'setCurrent': function( userData, lawyerData ) {
				user.current = userData;

				if( user && user.current ) {
					user.current.permissions = calculatePermissions( userData, lawyerData );
				}

				if(Raven) {
					Raven.setUser(userData);
				}
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