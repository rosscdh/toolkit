angular.module('toolkit-gui').factory('userService',[
	'$q',
	'$resource',
	'$rootScope',
	'API_BASE_URL',
	'PusherService',
	function( $q, $resource, $rootScope, API_BASE_URL, PusherService ) {
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

				if(Pusher) {
					// Send notification through rootscope
					PusherService.subscribe( userData.username, 'notifications.new', function(msg) {
						var base64string, snd;
						// HTML5 audio
						if( Audio ) {
							base64string = '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IafsRpUKwzakM1VMQU1FMy45OS41VVVV//MURBMALAUWAAgiAABgBkAAEMIBVVVV//MURBMAGADkAAQAAIBYCiQAGAAAVVVV//MUZBMAAAGkAAAAAAAAA0gAAAAAVVVV//MUZBYAAAGkAAAAAAAAA0gAAAAAVVVV//MUZBkAAAGkAAAAAAAAA0gAAAAAVVVV//MUZBwAAAGkAAAAAAAAA0gAAAAAVVVV//MUZB8AAAGkAAAAAAAAA0gAAAAAVVVV//MUZCIAAAGkAAAAAAAAA0gAAAAAVVVV//MUZCUAAAGkAAAAAAAAA0gAAAAAVVVV//MUZCgAAAGkAAAAAAAAA0gAAAAAVVVV//MUZCsAAAGkAAAAAAAAA0gAAAAAVVVV//MUZC4AAAGkAAAAAAAAA0gAAAAAVVVV//MUZDEAAAGkAAAAAAAAA0gAAAAAVVVV//MUZDQAAAGkAAAAAAAAA0gAAAAAVVVV//MUZDcAAAGkAAAAAAAAA0gAAAAAVVVV//MUZDoAAAGkAAAAAAAAA0gAAAAAVVVV//MUZD0AAAGkAAAAAAAAA0gAAAAAVVVV//MUZEAAAAGkAAAAAAAAA0gAAAAAVVVV//MUZEMAAAGkAAAAAAAAA0gAAAAAVVVV//MUZEYAAAGkAAAAAAAAA0gAAAAAVVVV//MUZEkAAAGkAAAAAAAAA0gAAAAAVVVV//MUZEwAAAGkAAAAAAAAA0gAAAAAVVVV//MUZE8AAAGkAAAAAAAAA0gAAAAAVVVV';
							snd = new Audio("data:audio/wav;base64," + base64string);
							snd.play();
						}
						$rootScope.$broadcast( 'notification', msg );
					});
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