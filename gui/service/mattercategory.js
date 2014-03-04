var category;
var matter;

angular.module('toolkit-gui').factory('matterCategoryService',[ '$q', '$resource', '$rootScope', function( $q, $resource, $rootScope) {

	var token = { 'value': 'xyz' };

	function matterCategoryResource() {
		return $resource( $rootScope.API_BASE_URL + 'matters/:matterSlug/category/:categorySlug', {'matterSlug':matter.slug}, {
			'create': { 'method': 'POST', params:{'categorySlug':'@slug'}, 'headers': { 'Content-Type': 'application/json'/*, 'token': token.value*/ }},
            'update': { 'method': 'PATCH', params:{'categorySlug':'@slug'},'headers': { 'Content-Type': 'application/json'/*, 'token': token.value*/ }},
            'delete': { 'method': 'DELETE', 'headers': { 'Content-Type': 'application/json'/*, 'token': token.value*/ }}
		});
	}

	return {
		'data': function() {
			return category;
		},

        'selectMatter': function( objMatter ) {
			matter = objMatter;
		},


        'create': function ( categoryName ) {
            var deferred = $q.defer();

			var api = matterCategoryResource();

            var matterCategory = {
                "status": "New",
                "name": categoryName
            };

			api.create({'slug': categoryName},
				function success(category){
					deferred.resolve(category);
				},
				function error(err) {
					deferred.reject( err );
				}
			);

			return deferred.promise;
        },

        'update': function ( category ) {
            var deferred = $q.defer();

			var api = matterCategoryResource();

			api.update(category,
				function success(category){
					deferred.resolve(category);
				},
				function error(err) {
					deferred.reject( err );
				}
			);

			return deferred.promise;
        },

        'delete': function ( category ) {
            var deferred = $q.defer();

			var api = matterCategoryResource();

			api.delete({'categorySlug': category.slug},
				function success(){
					deferred.resolve();
				},
				function error(err) {
					deferred.reject( err );
				}
			);

			return deferred.promise;
        }

	};
}]);