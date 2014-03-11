angular.module('toolkit-gui').factory('participantService', [
	'$q',
	'$resource',
	function($q, $resource) {

        function userAPI() {
            return $resource('/api/v1/users/:username', {}, {
				'get': { 'method': 'GET', 'headers': { 'Content-Type': 'application/json'/*, 'token': token.value*/ } }
			});
        }

		function participantAPI() {
			return $resource('/api/v1/matters/:matterSlug/participant', {}, {
				'list': { 'method': 'GET', 'headers': { 'Content-Type': 'application/json'/*, 'token': token.value*/ }, 'isArray': true },
				'get': { 'method': 'GET', 'headers': { 'Content-Type': 'application/json'/*, 'token': token.value*/ } },
				'invite': { 'method': 'POST', 'headers': { 'Content-Type': 'application/json'/*, 'token': token.value*/ } },
				'revoke': { 'method': 'DELETE', 'headers': { 'Content-Type': 'application/json'/*, 'token': token.value*/ } }
			});
		}

		var participants = {
            'getByURL': function(participanturl) {
                var deferred = $q.defer();

				var api = $resource(participanturl, {}, {
                    'get': { 'method': 'GET', 'headers': { 'Content-Type': 'application/json' }}
                });

				api.get({},
					function success( response ) {
						deferred.resolve( response );
					},
					function error( err ) {
						deferred.reject( err );
					}
				);

				return deferred.promise;
            },

            'getByUsername': function(username) {
                var deferred = $q.defer();

				var api = userAPI();

				api.get({'username': username},
					function success( response ) {
						deferred.resolve( response );
					},
					function error( err ) {
						deferred.reject( err );
					}
				);

				return deferred.promise;
            },

			'invite': function( matterSlug, details ) {
				var deferred = $q.defer();
				var api = participantAPI();

				api.invite( { 'matterSlug': matterSlug }, details,
					function success( response ) {
						deferred.resolve( response );
					},
					function error( err ) {
						deferred.reject( err );
					}
				);

				return deferred.promise;
			},

			'revoke': function( matterSlug, details ) {
				var deferred = $q.defer();
				var api = participantAPI();

				api.revoke( { 'matterSlug': matterSlug }, details,
					function success( response ) {
						deferred.resolve( response );
					},
					function error( err ) {
						deferred.reject( err );
					}
				);

				return deferred.promise;
			}
		};

		return participants;
	}
]);