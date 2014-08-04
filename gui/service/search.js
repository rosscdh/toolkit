angular.module('toolkit-gui').factory('searchService', [
    '$q',
    '$log',
    '$resource',
    'API_BASE_URL',
    'Fuse',
    function ($q, $log, $resource, API_BASE_URL, Fuse) {

        function searchAPI() {
            return $resource(API_BASE_URL + 'matters/:matterSlug/search', {}, {
                'get': { 'method': 'GET', 'headers': { 'Content-Type': 'application/json' }, 'isArray': true }
            });
        }

        var data = {
            'results': null
        };

        // function filterByTerm(term) {
        //     var reg = new RegExp( term, "i");
        //     var filteredResults = jQuery.grep( data.results, function( item ) {
        //      	return (item.name && item.name.match(reg) && item.name.match(reg).length) || (item.description && item.description.match(reg) && item.description.match(reg).length);
        //     });

        //     return filteredResults;
        // }
        function filterByFuseTerm(term) {
            if ( data.results.length > 0 ) {
                var fuseSearchService = new Fuse(data.results, { keys: ["name", "description", "file_type"], threshold: 0.35 });
                var results = fuseSearchService.search(term);
                return results;
            } else {
                return data.results;
            }
        }

        var search = {
            'filter': function (matterSlug, term) {
                var deferred = $q.defer();
                var results = [];
                var reg;

                if (term && term.length > 0) {
                    if (data.results) {
                        var filteredItems = filterByFuseTerm(term);
                        deferred.resolve(filteredItems);
                    } else {
                        // perform search
                        var api = searchAPI();

                        api.get({'matterSlug': matterSlug},
                            function success(response) {
                                data.results = response;
                                var filteredItems = filterByFuseTerm(term);
                                deferred.resolve(filteredItems);
                            },
                            function error(err) {
                                data.results = [];
                                deferred.reject(err);
                            }
                        );
                    }
                }

                return deferred.promise;
            },
            'data': function () {
                return data;
            }
        };

        return search;
    }
]);