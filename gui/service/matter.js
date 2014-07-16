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
			'selectedStatusFilter': null,
			'categories': []
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
	        },

			/*
			 * Given an array of items select the first item if one is not already selected
			 * @param	{Object}	existingItem	the existing selected item, which may be undefined or null or an object
			 * @param	{Array}		items			array of items to select from
			 * @param	{Object}	category		category object, which contains the item and the category
			 *
			 * @return	{Object}					either the selected object or null
			 */
			'selectFirstitem': function( existingItem, items, category ) {
				if(typeof(existingItem)==='object' && existingItem!== null) {
					return existingItem;
				} else if( angular.isArray(items) && items.length > 0 ) {
					return { 'item': items[0], 'category': category };
				} else {
					return null;
				}
			},

			/**
			 * Requests the checklist API to add a checklist item
			 *
			 * @name				getItemBySlug
			 *
			 * @param  {Object} category	Category object contains category name (String)
			 * @private
			 * @method				getItemBySlug
			 * @memberof			matterService
			 */
			'getItemBySlug': function (itemSlug) {
				var selectedMatter = matter.selected;

				if (selectedMatter) {
					var items = jQuery.grep( selectedMatter.items, function(item) {
						return item.slug === itemSlug;
					});

					if (items.length > 0){
						return items[0];
					}
				}
				return null;
			},
			/**
			 * matterTemplate - returns the specific item template as provided by API
			 * @param  {String} templateName name of template
			 * @return {String}              template string as provided by API
			 */
			'matterTemplate': function( templateName ) {
				var templates = matter.selected._meta.templates;
				var template = '';

				if(templates) {
					template = templates[templateName]||'';
				}

				return template;
			}
		};
	}]
);