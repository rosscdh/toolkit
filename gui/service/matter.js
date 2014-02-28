var matters;

angular.module('toolkit-gui').factory('matterService',[ '$q', '$resource', function( $q, $resource ) {

	var token = { 'value': 'xyz' };

	var matter = {
		'items': [],
		'selected': null
	};

	function matterResource() {
		return $resource('http://localhost:8000/api/v1/matters/:matterSlug/', {}, {
			'list': { 'method': 'GET', 'headers': { 'Content-Type': 'application/json'/*, 'token': token.value*/ }, 'isArray': true },
			'get': { 'method': 'GET', 'headers': { 'Content-Type': 'application/json'/*, 'token': token.value*/ } }
		});
	}

	return {
		'data': function() {
			return matter;
		},

		'selectMatter': function( objMAtter ) {
			matter.selected = objMAtter;
		},

		'list': function() {
			var api = matterResource();
			var deferred = $q.defer();

			api.list( {},
				function success( result ) {
					deferred.resolve( result );
				},
				function error( err ) {
					deferred.reject( err );
				}
			);

			return deferred.promise;
		},

		'get': function( matterSlug ) {
			var deferred = $q.defer();

			var api = matterResource();

			api.get( { 'matterSlug': matterSlug },
				function success( singleMatter ){
					deferred.resolve( singleMatter );
				},
				function error(err) {
					deferred.reject( err );
				}
			);

			return deferred.promise;
		}
	};
}]);

matters = {"count": 1, "next": null, "previous": null, "results": [{"name": "Ut wisi enim ad", "slug": "ut-wisi-enim-ad", "matter_code": "00000-ut-wisi-enim-ad", "client": null, "lawyer": "http://127.0.0.1:8000/api/v1/users/lee/", "participants": ["http://127.0.0.1:8000/api/v1/users/lee/"], "closing_groups": [], "categories": [], "items": [{"slug": "25dbcbbd145048a2b98dc569de06e502", "url": "/api/v1/items/25dbcbbd145048a2b98dc569de06e502/", "status": "New", "name": "Stet clita kasd gubergren", "description": "Ut wisi enim ad minim veniam, quis nostrud exerci tation ullamcorper suscipit lobortis nisl ut aliquip ex ea commodo consequat. Lorem ipsum dolor sit amet, consectetuer adipiscing elit, sed diam nonummy nibh euismod tincidunt ut laoreet dolore magna aliquam erat volutpat. Consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. Sanctus sea sed takimata ut vero voluptua. Lorem ipsum dolor sit amet, consectetur adipisici elit, sed eiusmod tempor incidunt ut labore et dolore magna aliqua.", "matter": "/api/v1/matters/ut-wisi-enim-ad/", "parent": null, "children": [], "closing_group": "", "latest_revision": null, "is_final": false, "is_complete": false, "date_due": null, "date_created": "2014-02-25T11:52:12.590Z", "date_modified": "2014-02-25T11:52:12.590Z"}], "comments": [], "activity": [], "current_user": {"url": "/api/v1/users/lee/", "username": "lee", "first_name": "", "last_name": "", "email": "lee@lawpal.com", "is_active": true}, "current_user_todo": [], "date_created": "2014-02-25T11:50:25.351Z", "date_modified": "2014-02-25T11:50:25.351Z"}]};