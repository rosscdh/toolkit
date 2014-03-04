angular.module('toolkit-gui').factory('participantService', [
	'$q',
	'$resource',
	function($q, $resource) {

		function participantAPI() {
			return $resource('/api/v1/matters/:matterSlug/participant/:id', {}, {
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