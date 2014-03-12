angular.module('toolkit-gui').factory('userService',[
	'$q',
	'$resource',
	'API_BASE_URL',
	function( $q, $resource, API_BASE_URL ) {

		var user = {
			'data': {
				'items': [
					{ 'name': 'Sam Jackson', 'img': 'https://fbcdn-profile-a.akamaihd.net/hprofile-ak-ash3/t1/c0.0.100.100/p100x100/1014416_10100118438650161_136799916_a.jpg' },
					{ 'name': 'Bob Jackson', 'img': 'https://fbcdn-profile-a.akamaihd.net/hprofile-ak-ash2/t1/c12.12.155.155/314032_10150303812474864_594285312_a.jpg' },
					{ 'name': 'Hugh Jackson', 'img': 'https://fbcdn-profile-a.akamaihd.net/hprofile-ak-frc3/t1/c42.26.328.328/s320x320/229934_10150955684263644_890325486_n.jpg' }
				]
			}
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

			'get': function( /*uid*/ ) {
				var api = userResource();
				// append/update users in user.data.items
				var deferred = $q.defer();

				api.get( {},
					function success( result ) {
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