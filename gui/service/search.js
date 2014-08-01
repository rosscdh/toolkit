angular.module('toolkit-gui').factory('searchService', [
	'$q',
	'$log', 
	'$resource',
	'API_BASE_URL',
	function($q, $log, $resource, API_BASE_URL) {

        function searchAPI() {
            return $resource( API_BASE_URL + 'matters/:matterSlug/search', {}, {
				'get': { 'method': 'GET', 'headers': { 'Content-Type': 'application/json'/*, 'token': token.value*/ } },
			});
        }

		var data = {
			'term': null,
			'results': []
		};

		var search = {
			'filter': function( matterSlug, term ) {
				var deferred = $q.defer();
				var results = []; var reg;
				data.term = term;

				if( term && term.length > 0 ) {
					// perform search
					var api = searchAPI();

					api.get({'matterSlug': matterSlug},
						function success( response ) {
							alert(response)
							$log.debug(response);

							var results = response;

							// reg = new RegExp( term, "i");
							// results = jQuery.grep( results, function( item ) {
							// 	return item.name.match(reg) && item.name.match(reg).length || item.description.match(reg) && item.description.match(reg).length;
							// });

							data.results = results;
							deferred.resolve( results );
						},
						function error( err ) {
							data.results = [];
							deferred.reject( err );
						}
					);
				}
				return deferred.promise
			},
			'data': function() {
				return data;
			}
		};

		return search;
	}
]);