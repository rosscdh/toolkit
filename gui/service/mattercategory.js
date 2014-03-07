var category;
var matter;

angular.module('toolkit-gui').factory('matterCategoryService',[ '$q', '$resource', '$rootScope', function( $q, $resource, $rootScope) {

	var token = { 'value': 'xyz' };

	function matterCategoryResource() {
		return $resource( $rootScope.API_BASE_URL + 'matters/:matterSlug/category/:categorySlug', {'matterSlug':matter.slug}, {
			'create': { 'method': 'POST', params:{'categorySlug':'@categorySlug'}, 'headers': { 'Content-Type': 'application/json'/*, 'token': token.value*/ } , 'isArray': true},
            'update': { 'method': 'PATCH', params:{'categorySlug':'@categorySlug'},'headers': { 'Content-Type': 'application/json'/*, 'token': token.value*/ } , 'isArray': true},
            'delete': { 'method': 'DELETE', params:{'categorySlug':'@categorySlug'},'headers': { 'Content-Type': 'application/json'/*, 'token': token.value*/ }, 'isArray': true}
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

			api.create({'categorySlug': categoryName},
				function success(){
					deferred.resolve();
				},
				function error(err) {
					deferred.reject( err );
				}
			);

			return deferred.promise;
        },

        'update': function ( oldCategoryName, newCategoryName ) {
            var deferred = $q.defer();

			var api = matterCategoryResource();

			api.update({'categorySlug': oldCategoryName}, {'category': newCategoryName },
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

			api.delete({'categorySlug': category.name},
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