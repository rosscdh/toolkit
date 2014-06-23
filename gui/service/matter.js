var matters;

angular.module('toolkit-gui')
/**
 * @class matterService
 * @classdesc 		                      Responsible for managing and requesting the API to invite participants into a matter
 * @param  {Function} $q                  Contains the scope of this controller
 * @param  {Function} $resource           Provides access to close and cancel methods
 * @param  {Function} anon                Controller function
 */
.factory('matterService',[
	'$q',
	'$resource',
	'API_BASE_URL',
	function( $q, $resource, API_BASE_URL ) {
		/**
		 * TBC: this variable will contain the JWT token requied to make authenticated requests
		 * @memberof matterService
		 * @type {Object}
		 * @private
		 */
		var token = { 'value': 'xyz' };

		/**
		 * Contains a list of checklist items and the selected item.
		 * This variable can be used by any controller to access the array of items and the selected item
		 *
		 * @example
		 * matterService.data().selected;
		 * 
		 * @memberof matterService
		 * @type {Object}
		 * @private
		 */
		var matter = {
			'items': [],
			'selected': null,
			'statusFilter': null,
			'itemFilter': null,
			'selectedStatusFilter': null
		};

		/**
		 * Returns a key/value object containing $resource methods to access matter API end-points
		 *
		 * @name				matterResource
		 * 
		 * @private
		 * @method				matterResource
		 * @memberof			matterService
		 *
		 * @return {Function}   $resource
		 */
		function matterResource() {
			return $resource( API_BASE_URL + 'matters/:matterSlug/:action', {}, {
				'list': { 'method': 'GET', 'headers': { 'Content-Type': 'application/json'/*, 'token': token.value*/ } },
				'get': { 'method': 'GET', 'headers': { 'Content-Type': 'application/json'/*, 'token': token.value*/ } },
				'sort': { 'method': 'PATCH', 'params': {'action': 'sort'}, 'headers': { 'Content-Type': 'application/json'/*, 'token': token.value*/ } },
				'revisionstatus': { 'method': 'POST', 'params': {'action': 'revision_label'}, 'headers': { 'Content-Type': 'application/json'/*, 'token': token.value*/ } }
			});
		}

		return {
			/**
			 * Returns object containing 'checklist items' and matter.
			 * This data lives beyond the life of a single view.
			 *
			 * @name				data
			 *
			 * @example
		 	 * matterService.data()
			 * 
			 * @public
			 * @method				data
			 * @memberof			matterService
			 *
			 * @return {Object}     { 'items': [], 'selected': {} }
		 	 */
			'data': function() {
				return matter;
			},

			/**
			 * Sets the selected matter to one passed in.
			 *
			 * @name				selectMatter
			 *
			 * @example
		 	 * matterService.selectMatter( mySelectedMatter );
			 * 
			 * @public
			 * @method				selectMatter
			 * @memberof			matterService
		 	 */
			'selectMatter': function( objMatter ) {
				matter.selected = objMatter;
			},

			/**
			 * Requests a list of matters from the API
			 *
			 * @name				list
			 *
			 * @example
		 	 * matterService.list( mySelectedMatter );
			 * 
			 * @public
			 * @method				list
			 * @memberof			matterService
			 *
			 * @return {Promise}    Array of matters
		 	 */
			'list': function() {
				var api = matterResource();
				var deferred = $q.defer();

				api.list( {},
					function success( result ) {
						deferred.resolve( result.results );
					},
					function error( err ) {
						deferred.reject( err );
					}
				);

				return deferred.promise;
			},

			/**
			 * Requests a list of matters from the API
			 *
			 * @name				get
			 * @param {String}      matterSlug    Used by the API as a unique identifier for a specific matter
			 *
			 * @example
		 	 * matterService.get( 'matter-one' );
			 * 
			 * @public
			 * @method				get
			 * @memberof			matterService
			 *
			 * @return {Promise}    Array of matters
		 	 */
			'get': function( matterSlug ) {
				var deferred = $q.defer();

				var api = matterResource();

				api.get( { 'matterSlug': matterSlug },
					function success( singleMatter ){
						matter.items = singleMatter.items;
						deferred.resolve( singleMatter );
					},
					function error(err) {
						deferred.reject( err );
					}
				);

				return deferred.promise;
			},

			/**
			 * Incepts request of the API to save checklist and category order
			 *
			 * @name				saveSortOrder
			 * @param {Object}      matterSlug     Used by the API as a unique identifier for a specific matter
			 *
			 * @example
		 	 * matterService.saveSortOrder( { 'items': [] } );
			 * 
			 * @public
			 * @method				saveSortOrder
			 * @memberof			matterService
			 *
			 * @return {Promise}    Array of matters
		 	 */
	        'saveSortOrder': function ( matterSlug, APIUpdate ) {
	            var deferred = $q.defer();

				var api = matterResource();

				api.sort({'matterSlug': matterSlug },APIUpdate,
					function success(){
						deferred.resolve();
					},
					function error(err) {
						deferred.reject( err );
					}
				);

				return deferred.promise;
	        },


             /**
			 * Incepts request of the API to save the revision status
			 *
			 * @name				saveRevisionStatus
			 * @param {Object}      matterSlug     Used by the API as a unique identifier for a specific matter
			 * @param {Object}      APIUpdate      Object
			 *
			 * @example
		 	 * matterService.saveSortOrder( 'mymatter', { } );
			 *
			 * @public
			 * @method				saveRevisionStatus
			 * @memberof			matterService
			 *
			 * @return {Promise}
		 	 */
            'saveRevisionStatus': function ( matterSlug, APIUpdate ) {
	            var deferred = $q.defer();

				var api = matterResource();

				api.revisionstatus({'matterSlug': matterSlug }, APIUpdate,
					function success(){
						deferred.resolve();
					},
					function error(err) {
						deferred.reject( err );
					}
				);

				return deferred.promise;
	        },



	        /**
	         * This function is used to maintain the array of checklist items (used for search)
	         * @param  {Object} item Typically new item as recieved from API
	         */
	        'insertItem': function( item ) {
	        	matter.items.push( item );
	        }
		};
	}]
);

matters = {"count": 1, "next": null, "previous": null, "results": [{"name": "Ut wisi enim ad", "slug": "ut-wisi-enim-ad", "matter_code": "00000-ut-wisi-enim-ad", "client": null, "lawyer": "http://127.0.0.1:8000/api/v1/users/lee/", "participants": ["http://127.0.0.1:8000/api/v1/users/lee/"], "closing_groups": [], "categories": [], "items": [{"slug": "25dbcbbd145048a2b98dc569de06e502", "url": "/api/v1/items/25dbcbbd145048a2b98dc569de06e502/", "status": "New", "name": "Stet clita kasd gubergren", "description": "Ut wisi enim ad minim veniam, quis nostrud exerci tation ullamcorper suscipit lobortis nisl ut aliquip ex ea commodo consequat. Lorem ipsum dolor sit amet, consectetuer adipiscing elit, sed diam nonummy nibh euismod tincidunt ut laoreet dolore magna aliquam erat volutpat. Consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. Sanctus sea sed takimata ut vero voluptua. Lorem ipsum dolor sit amet, consectetur adipisici elit, sed eiusmod tempor incidunt ut labore et dolore magna aliqua.", "matter": "/api/v1/matters/ut-wisi-enim-ad/", "parent": null, "children": [], "closing_group": "", "latest_revision": null, "is_final": false, "is_complete": false, "date_due": null, "date_created": "2014-02-25T11:52:12.590Z", "date_modified": "2014-02-25T11:52:12.590Z"}], "comments": [], "activity": [], "current_user": {"url": "/api/v1/users/lee/", "username": "lee", "first_name": "", "last_name": "", "email": "lee@lawpal.com", "is_active": true}, "current_user_todo": [], "date_created": "2014-02-25T11:50:25.351Z", "date_modified": "2014-02-25T11:50:25.351Z"}]};