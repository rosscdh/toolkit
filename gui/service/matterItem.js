var item;

angular.module('toolkit-gui').factory('matterItemService',[ '$q', '$resource', function( $q, $resource ) {

	var token = { 'value': 'xyz' };

	function matterItemResource() {
		return $resource('http://localhost:8000/api/v1/matters/:matterSlug/items', {}, {
			'create': { 'method': 'PUT', 'headers': { 'Content-Type': 'application/json'/*, 'token': token.value*/ }},
            'delete': { 'method': 'DELETE', 'headers': { 'Content-Type': 'application/json'/*, 'token': token.value*/ }}
		});
	}

	return {
		'data': function() {
			return item;
		},

        'create': function ( itemName, categoryName ) {
            var deferred = $q.defer();

			var api = matterItemResource();

            var newItem = {
                'status': 'NEW',
                'name': itemName,
                'category': categoryName
            };

			api.create( newItem,
				function success(item){
					deferred.resolve(item);
				},
				function error(err) {
					deferred.reject( err );
				}
			);

			return deferred.promise;
        },

        'delete': function ( item ) {
            var deferred = $q.defer();

			var api = matterItemResource();

			api.delete( item,
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