angular.module('toolkit-gui')
/**
 * @class matterItemService
 * @classdesc 		                      Responsible for managing and requesting the API to invite participants into a matter
 * @param  {Function} $q                  Contains the scope of this controller
 * @param  {Function} $resource           Provides access to close and cancel methods
 * @param  {Function} anon                Controller function
 */
.factory('matterItemService',[
	'$q',
	'$resource',
	'$rootScope',
	function( $q, $resource, $rootScope) {
		/**
		 * TBC: this variable will contain the JWT token requied to make authenticated requests
		 * @memberof matterItemService
		 * @type {Object}
		 * @private
		 */
		var token = { 'value': 'xyz' };

		/**
		 * Selected matter item.
		 *
		 * @example
		 * matterService.data();
		 * 
		 * @memberof matterService
		 * @type {Object}
		 * @private
		 */
		var item;

		/**
		 * Selected matter.
		 * 
		 * @memberof matterService
		 * @type {Object}
		 * @private
		 */
		var matter;

		/**
		 * Returns a key/value object containing $resource methods to access matter API end-points
		 *
		 * @name				matterItemResource
		 * 
		 * @private
		 * @method				matterItemResource
		 * @memberof			matterItemService
		 *
		 * @return {Function}   $resource
		 */
		function matterItemResource() {
			return $resource( $rootScope.API_BASE_URL + 'matters/:matterSlug/items/:itemSlug', {'matterSlug':matter.slug}, {
				'create': { 'method': 'POST', 'headers': { 'Content-Type': 'application/json'/*, 'token': token.value*/ }},
				'update': { 'method': 'PATCH', params:{'itemSlug':'@slug'},'headers': { 'Content-Type': 'application/json'/*, 'token': token.value*/ }},
				'delete': { 'method': 'DELETE', 'headers': { 'Content-Type': 'application/json'/*, 'token': token.value*/ }}
			});
		}

		/**
		 * Returns a key/value object containing $resource methods to access matter API end-points
		 *
		 * @name				revisionItemResource
		 * 
		 * @private
		 * @method				revisionItemResource
		 * @memberof			matterItemService
		 *
		 * @return {Function}   $resource
		 */
		function revisionItemResource() {
			return $resource( $rootScope.API_BASE_URL + 'matters/:matterSlug/items/:itemSlug/revision/:version', {}, {
				'create': { 'method': 'POST', 'headers': { 'Content-Type': 'application/json'/*, 'token': token.value*/ }},
				'update': { 'method': 'PATCH', 'headers': { 'Content-Type': 'application/json'/*, 'token': token.value*/ }},
	            'delete': { 'method': 'DELETE', 'headers': { 'Content-Type': 'application/json'/*, 'token': token.value*/ }},
	            'get': { 'method': 'GET', 'headers': { 'Content-Type': 'application/json'/*, 'token': token.value*/ }}
			});
		}

		return {
			/**
			 * Returns object containing selected matter's data.
			 *
			 * @name				data
			 *
			 * @example
		 	 * matterItemService.data();
			 * 
			 * @public
			 * @method				data
			 * @memberof			matterItemService
			 *
			 * @return {Object}     { }
		 	 */
			'data': function() {
				return item;
			},

			/**
			 * Sets the selected matter to the one passed through.
			 * the selected matter is available across views.
			 *
			 * @name				data
			 *
			 * @example
		 	 * matterItemService.selectMatter( { ... } );
			 * 
			 * @public
			 * @method				data
			 * @memberof			matterItemService
		 	 */
			'selectMatter': function( objMatter ) {
				matter = objMatter;
			},

			/**
			 * Reqests that the API create a new matter checklist item
			 *
			 * @name				create
			 * @param {String} itemName Text string as provided by end user
			 * @param {String} categoryName Name of the catgeoy to place the new item within
			 *
			 * @example
		 	 * matterItemService.create( 'myItemName', 'ItemCategoryName' );
			 * 
			 * @public
			 * @method				create
			 * @memberof			matterItemService
			 *
			 * @return {Promise}    New item object as provided by API
		 	 */
			'create': function ( itemName, categoryName ) {
				var deferred = $q.defer();

				var api = matterItemResource();

				var matterItem = {
					"status": "New",
					"name": itemName,
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

			/**
			 * Reqests that the API update an existing matter checklist item
			 *
			 * @name				update
			 * @param {String}      itemName Text string as provided by end user
			 * @param {String}      categoryName Name of the catgeoy to place the new item within
			 *
			 * @example
		 	 * matterItemService.update( {...} );
			 * 
			 * @public
			 * @method				update
			 * @memberof			matterItemService
			 *
			 * @return {Promise}    Updated item object as provided by API
		 	 */
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

			/**
			 * Reqests that the API delete an existing matter checklist item
			 *
			 * @name				delete
			 * @param {Object}      matterItem    JSON representation of matter that is to be deleted
			 *
			 * @example
		 	 * matterItemService.delete( {...} );
			 * 
			 * @public
			 * @method				delete
			 * @memberof			matterItemService
			 *
			 * @return {Promise}    Updated item object as provided by API
		 	 */
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

			/**
			 * Reqests that the API delete an existing matter checklist item
			 *
			 * @name				uploadRevision
			 * @param {String}      matterSlug    Database slug, used as a unquie idenitfier for a matter.
			 * @param {String}      itemSlug      Database slug, used as a unquie identifier for a checklist item.
			 * @param {Object}      files         Details as provided by filerpicker.io
			 *
			 * @example
		 	 * matterItemService.uploadRevision( 'myItemName', 'ItemCategoryName', {} );
			 * 
			 * @public
			 * @method				uploadRevision
			 * @memberof			matterItemService
			 *
			 * @return {Promise}    Updated item object as provided by API
		 	 */
			'uploadRevision': function( matterSlug, itemSlug, files ) {
				var deferred = $q.defer();

				var api = revisionItemResource();

	            var fileurl = files[0].url;
	            var filename = files[0].filename;

				api.create({'matterSlug': matterSlug, 'itemSlug': itemSlug }, { 'executed_file': fileurl, 'name': filename },
					function success(revision){
						deferred.resolve(revision);
					},
					function error(err) {
						deferred.reject( err );
					}
				);

				return deferred.promise;
			},

			/**
			 * Reqests a revision update
			 *
			 * @name				updateRevision
			 * @param {String}      matterSlug    Database slug, used as a unquie idenitfier for a matter.
			 * @param {String}      itemSlug      Database slug, used as a unquie identifier for a checklist item.
			 * @param {Object}      files         Details as provided by filerpicker.io
			 *
			 * @example
		 	 * matterItemService.updateRevision( 'myItemName', 'ItemCategoryName', {} );
			 * 
			 * @public
			 * @method				updateRevision
			 * @memberof			matterItemService
			 *
			 * @return {Promise}    Updated item object as provided by API
		 	 */
	        'updateRevision': function ( matterSlug, itemSlug, revisionItem ) {
				var deferred = $q.defer();

				var api = revisionItemResource();

				api.update({'matterSlug': matterSlug, 'itemSlug': itemSlug }, revisionItem,
					function success(item){
						deferred.resolve(item);
					},
					function error(err) {
						deferred.reject( err );
					}
				);

				return deferred.promise;
			},

			/**
			 * Reqests the API to delete a specific revision.
			 *
			 * @name				deleteRevision
			 * @param {String}      matterSlug    Database slug, used as a unquie idenitfier for a matter.
			 * @param {String}      itemSlug      Database slug, used as a unquie identifier for a checklist item.
			 * @param {Object}      revisionItem  Revision object
			 *
			 * @example
		 	 * matterItemService.deleteRevision( 'myItemName', 'ItemCategoryName', {} );
			 * 
			 * @public
			 * @method				deleteRevision
			 * @memberof			matterItemService
			 *
			 * @return {Promise}    Updated item object as provided by API
		 	 */
	        'deleteRevision': function ( matterSlug, itemSlug, revisionItem  ) {
				var deferred = $q.defer();

				var api = revisionItemResource();

				api.delete({'matterSlug': matterSlug, 'itemSlug': itemSlug }, revisionItem,
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
			 * Load a revision from URL
			 *
			 * @name				loadRevisionByURL
			 * @param {String}      matterSlug    Database slug, used as a unquie idenitfier for a matter.
			 * @param {String}      itemSlug      Database slug, used as a unquie identifier for a checklist item.
			 * @param {String}      revisionSlug  Database slug, used as a unquie identifier for a revision.
			 *
			 * @example
		 	 * matterItemService.loadRevisionByURL( 'myMatterName', 'myItemName', 'v1' );
			 *
			 * @public
			 * @method				loadRevisionByURL
			 * @memberof			matterItemService
			 *
			 * @return {Promise}    Updated item object as provided by API
		 	 */
	        'loadRevision': function ( matterSlug, itemSlug, revisionSlug ) {
				var deferred = $q.defer();

				var api = revisionItemResource();

				api.get({'matterSlug': matterSlug, 'itemSlug': itemSlug, 'version':revisionSlug  },
					function success(revision){
						deferred.resolve(revision);
					},
					function error(err) {
						deferred.reject( err );
					}
				);

				return deferred.promise;
			}
		};
	}]
);