angular.module('toolkit-gui').factory('participantService', [
	'$q',
	'$resource',
	function() {

		function participantAPI() {
			return $resource('http://127.0.0.1:8000/api/v1/matters/:matterSlug/participant/:id', {}, {
				'list': { 'method': 'GET', 'headers': { 'Content-Type': 'application/json'/*, 'token': token.value*/ }, 'isArray': true },
				'get': { 'method': 'GET', 'headers': { 'Content-Type': 'application/json'/*, 'token': token.value*/ } },
				'invite': { 'method': 'POST', 'headers': { 'Content-Type': 'application/json'/*, 'token': token.value*/ } }
			});
		}
		var participants = {
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
			}
		};

		return participants;
	}
]);