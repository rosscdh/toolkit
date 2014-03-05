var item;
var matter;

angular.module('toolkit-gui').factory('matterItemService',[ '$q', '$resource', '$rootScope', function( $q, $resource, $rootScope) {

	var token = { 'value': 'xyz' };

	function matterItemResource() {
		return $resource( $rootScope.API_BASE_URL + 'matters/:matterSlug/items/:itemSlug', {'matterSlug':matter.slug}, {
			'create': { 'method': 'POST', 'headers': { 'Content-Type': 'application/json'/*, 'token': token.value*/ }},
            'update': { 'method': 'PATCH', params:{'itemSlug':'@slug'},'headers': { 'Content-Type': 'application/json'/*, 'token': token.value*/ }},
            'delete': { 'method': 'DELETE', 'headers': { 'Content-Type': 'application/json'/*, 'token': token.value*/ }}
		});
	}

	function revisionItemResource() {
		return $resource( $rootScope.API_BASE_URL + 'matters/:matterSlug/items/:itemSlug/revision/:version', {}, {
			'create': { 'method': 'POST', 'headers': { 'Content-Type': 'application/json'/*, 'token': token.value*/ }}
		});
	}

	return {
		'data': function() {
			return item;
		},

        'selectMatter': function( objMatter ) {
			matter = objMatter;
		},


        'create': function ( itemName, categoryName ) {
            var deferred = $q.defer();

			var api = matterItemResource();

            var matterItem = {
                "status": "New",
                "name": itemName,
                "description": itemName,
                "category": categoryName,
                "matter": $rootScope.API_BASE_URL + 'matters/' + matter.slug,
                "parent": null,
                "children": [],
                "closing_group": null,
                "latest_revision": null,
                "is_final": false,
                "is_complete": false,
                "date_due": null
            };

			api.create(matterItem,
				function success(item){
					deferred.resolve(item);
				},
				function error(err) {
					deferred.reject( err );
				}
			);

			return deferred.promise;
        },

        'update': function ( matterItem ) {
            var deferred = $q.defer();

			var api = matterItemResource();

			api.update(matterItem,
				function success(item){
					deferred.resolve(item);
				},
				function error(err) {
					deferred.reject( err );
				}
			);

			return deferred.promise;
        },

        'delete': function ( matterItem ) {
            var deferred = $q.defer();

			var api = matterItemResource();

			api.delete({'itemSlug': matterItem.slug},
				function success(){
					deferred.resolve();
				},
				function error(err) {
					deferred.reject( err );
				}
			);

			return deferred.promise;
        },

        'uploadRevision': function( matterSlug, itemSlug, fileDetails ) {
        	var deferred = $q.defer();

			var api = revisionItemResource();

			var formData = new FormData();
			formData.append("executed_file", fileDetails);

			api.create({'matterSlug': matterSlug, 'itemSlug': itemSlug }, { 'executed_file': fileDetails },
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