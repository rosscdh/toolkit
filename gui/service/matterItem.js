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
	'$upload',
	'API_BASE_URL',
	function( $q, $resource, $rootScope, $upload, API_BASE_URL) {
		/**
		 * TBC: this variable will contain the JWT token required to make authenticated requests
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
			return $resource( API_BASE_URL + 'matters/:matterSlug/items/:itemSlug/:action', {}, {
				'create': { 'method': 'POST', 'headers': { 'Content-Type': 'application/json'/*, 'token': token.value*/ }},
				'update': { 'method': 'PATCH', 'headers': { 'Content-Type': 'application/json'/*, 'token': token.value*/ }},
				'delete': { 'method': 'DELETE', 'headers': { 'Content-Type': 'application/json'/*, 'token': token.value*/ }},
				'requestdocument': { 'method': 'PATCH', 'params':{'action':'request_document'},'headers': { 'Content-Type': 'application/json'/*, 'token': token.value*/ }},
				'remind': { 'method': 'POST', 'params':{'action':'remind'},'headers': { 'Content-Type': 'application/json'/*, 'token': token.value*/ }}
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
			return $resource( API_BASE_URL + 'matters/:matterSlug/items/:itemSlug/revision/:version', {}, {
				'create': { 'method': 'POST', 'headers': { 'Content-Type': 'application/json'/*, 'token': token.value*/ }},
				'update': { 'method': 'PATCH', 'headers': { 'Content-Type': 'application/json'/*, 'token': token.value*/ }},
				'delete': { 'method': 'DELETE', 'headers': { 'Content-Type': 'application/json'/*, 'token': token.value*/ }},
				'get': { 'method': 'GET', 'headers': { 'Content-Type': 'application/json'/*, 'token': token.value*/ }}
			});
		}


		function reviewerItemResource() {
			return $resource( API_BASE_URL + 'matters/:matterSlug/items/:itemSlug/revision/reviewers/:username:action', {}, {
				'request': { 'method': 'POST', 'headers': { 'Content-Type': 'application/json'/*, 'token': token.value*/ }},
				'remind': { 'method': 'POST', 'params': {'action':'remind'}, 'headers': { 'Content-Type': 'application/json'/*, 'token': token.value*/ }},
				'delete': { 'method': 'DELETE', 'headers': { 'Content-Type': 'application/json'/*, 'token': token.value*/ }}
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
			 * Reqests that the API create a new matter checklist item
			 *
			 * @param {String}      matterSlug    Database slug, used as a unique identifier for a matter.
			 * @param {String} matterSlug
			 * @param {String} itemName Text string as provided by end user
			 * @param {String} categoryName Name of the category to place the new item within
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
			'create': function ( matterSlug, itemName, categoryName ) {
				var deferred = $q.defer();

				var api = matterItemResource();

				var matterItem = {
					"status": 0,
					"name": itemName,
					"category": categoryName,
					"matter": API_BASE_URL + 'matters/' + matterSlug,
					"parent": null,
					"children": [],
					"closing_group": null,
					"latest_revision": null,
					"is_final": false,
					"is_complete": false,
					"date_due": null
				};

				api.create({'matterSlug': matterSlug }, matterItem,
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
			 * @param {String}      matterSlug    Database slug, used as a unique identifier for a matter.
			 * @param {String}      itemName Text string as provided by end user
			 * @param {String}      categoryName Name of the category to place the new item within
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
			'update': function ( matterSlug, matterItem ) {
				var deferred = $q.defer();

				var api = matterItemResource();

				 var updateFields = {
					'slug': matterItem.slug,
					'status': matterItem.status,
					'name': matterItem.name,
					'category': matterItem.category,
					'description': matterItem.description,
					'date_due': matterItem.date_due,
					'is_complete': matterItem.is_complete
				};

				api.update({'matterSlug': matterSlug, 'itemSlug': matterItem.slug }, updateFields,
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
			 * @param {String}      matterSlug    Database slug, used as a unique identifier for a matter.
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
			'delete': function ( matterSlug, matterItem ) {
				var deferred = $q.defer();

				var api = matterItemResource();

				api.delete({'matterSlug': matterSlug, 'itemSlug': matterItem.slug},
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
			 * @param {String}      matterSlug    Database slug, used as a unique identifier for a matter.
			 * @param {String}      itemSlug      Database slug, used as a unique identifier for a checklist item.
			 * @param {Object}      files         Details as provided by filepicker.io
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
			 * Upload a specific file into a checklist item revision
			 * @param  {String} matterSlug unique identifier for a specific matter
			 * @param  {String} itemSlug   Unique identifier for a specific checklist item within the matter
			 * @param  {Array} $files     Array of files (HTML5 files object)
			 * @return {Promise}
			 */
			'uploadRevisionFile': function( matterSlug, itemSlug, $files ) {
				var deferred = $q.defer(), files, url;

				var api = revisionItemResource();

				if( $files.length>0 ) {
					url = API_BASE_URL + 'matters/'+matterSlug+'/items/'+itemSlug+'/revision';
					var file = $files[0];

					$upload.upload({
						'url': url, //upload.php script, node.js route, or servlet url
						'file': file,
						'fileFormDataName': 'executed_file',
					}).progress(function(evt) {
						console.log('percent: ' + parseInt(100.0 * evt.loaded / evt.total));

						deferred.notify(parseInt(100.0 * evt.loaded / evt.total));
					}).success(function(data, status, headers, config) {
						// file is uploaded successfully
						deferred.resolve(data);
						console.log(data);
					});
				} else {
					setTimeout(
						function(){
							deferred.reject();
						},
					1);
				}

				return deferred.promise;
			},

			/**
			 * Requests a revision update
			 *
			 * @name				updateRevision
			 * @param {String}      matterSlug    Database slug, used as a unique identifier for a matter.
			 * @param {String}      itemSlug      Database slug, used as a unique identifier for a checklist item.
			 * @param {Object}      files         Details as provided by filepicker.io
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

				var updateFields = {
					'status': revisionItem.status,
					'description': revisionItem.description
				};

				api.update({'matterSlug': matterSlug, 'itemSlug': itemSlug }, updateFields,
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
			 * @param {String}      matterSlug    Database slug, used as a unique identifier for a matter.
			 * @param {String}      itemSlug      Database slug, used as a unique identifier for a checklist item.
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
			 * Requests the API to send a revision request to given participant.
			 *
			 * @name				requestRevision
			 * @param {String}      matterSlug    Database slug, used as a unique identifier for a matter.
			 * @param {String}      itemSlug      Database slug, used as a unique identifier for a checklist item.
			 * @param {Object}      participant   Dictionary consisting of email, message, username
			 *
			 * @example
		 	 * matterItemService.requestRevision( 'myMatterName', 'myItemName', {} );
			 *
			 * @public
			 * @method				requestRevision
			 * @memberof			matterItemService
			 *
			 * @return {Promise}
		 	 */
	        'requestRevision': function ( matterSlug, itemSlug, participant  ) {
				var deferred = $q.defer();

				var api = matterItemResource();

				api.requestdocument({'matterSlug': matterSlug, 'itemSlug': itemSlug }, participant,
					function success(response){
						deferred.resolve(response);
					},
					function error(err) {
						deferred.reject( err );
					}
				);

				return deferred.promise;
			},

             /**
			 * Requests the API to send a reminder to the responsible participant to upload the requested document.
			 *
			 * @name				remindRevisionRequest
			 * @param {String}      matterSlug    Database slug, used as a unique identifier for a matter.
			 * @param {String}      itemSlug      Database slug, used as a unique identifier for a checklist item.
			 *
			 * @example
			 * matterItemService.remindRevisionRequest( 'myMatterName', 'myItemName' );
			 *
			 * @public
			 * @method				remindRevisionRequest
			 * @memberof			matterItemService
			 *
			 * @return {Promise}
			 */
            'remindRevisionRequest': function ( matterSlug, itemSlug ) {
				var deferred = $q.defer();

				var api = matterItemResource();

				api.remind({'matterSlug': matterSlug, 'itemSlug': itemSlug }, {},
					function success(){
						deferred.resolve();
					},
					function error(err) {
						deferred.reject( err );
					}
				);

				return deferred.promise;
			},

            'deleteRevisionRequest': function ( matterSlug, itemSlug ) {
                //not implemented
                return null;
            },

            /**
			/**
			 * Load a revision from URL
			 *
			 * @name				loadRevisionByURL
			 * @param {String}      matterSlug    Database slug, used as a unique identifier for a matter.
			 * @param {String}      itemSlug      Database slug, used as a unique identifier for a checklist item.
			 * @param {String}      revisionSlug  Database slug, used as a unique identifier for a revision.
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
			},

			/**
			 * Requests the API to send a revision review request to given participant
			 *
			 * @name				requestRevisionReview
			 * @param {String}      matterSlug    Database slug, used as a unique identifier for a matter.
			 * @param {String}      itemSlug      Database slug, used as a unique identifier for a checklist item.
			 * @param {String}      participant   User object.
			 *
			 * @example
			 * matterItemService.loadRevisionByURL( 'myMatterName', 'myItemName', {} );
			 *
			 * @public
			 * @method				requestRevisionReview
			 * @memberof			matterItemService
			 *
			 * @return {Promise}    Updated item object as provided by API
			 */
			'requestRevisionReview': function ( matterSlug, itemSlug, participant ) {
				var deferred = $q.defer();

				var api = reviewerItemResource();
                console.log(participant);

				api.request({'matterSlug': matterSlug, 'itemSlug': itemSlug }, {'username': participant.username},
					function success(response){
						deferred.resolve(response);
					},
					function error(err) {
						deferred.reject( err );
					}
				);

				return deferred.promise;
			},


            /**
			 * Requests the API to send a reminder to all reviewer who have not reviewed the current revision yet.
			 *
			 * @name				remindRevisionReview
			 * @param {String}      matterSlug    Database slug, used as a unique identifier for a matter.
			 * @param {String}      itemSlug      Database slug, used as a unique identifier for a checklist item.
			 *
			 * @example
			 * matterItemService.remindRevisionReview( 'myMatterName', 'myItemName' );
			 *
			 * @public
			 * @method				remindRevisionReview
			 * @memberof			matterItemService
			 *
			 * @return {Promise}
			 */
            'remindRevisionReview': function ( matterSlug, itemSlug ) {
				var deferred = $q.defer();

				var api = reviewerItemResource();

				api.remind({'matterSlug': matterSlug, 'itemSlug': itemSlug }, {},
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
			 * Delete the review request for a specific user.
			 *
			 * @name				deleteRevisionReview
			 * @param {String}      matterSlug    Database slug, used as a unique identifier for a matter.
			 * @param {String}      itemSlug      Database slug, used as a unique identifier for a checklist item.
			 * @param {String}      participant   User object.
			 *
			 * @example
			 * matterItemService.deleteRevisionReview( 'myMatterName', 'myItemName', {} );
			 *
			 * @public
			 * @method				deleteRevisionReview
			 * @memberof			matterItemService
			 *
			 * @return {Promise}
			 */
			'deleteRevisionReviewRequest': function ( matterSlug, itemSlug, participant ) {
				var deferred = $q.defer();

				var api = reviewerItemResource();

				api.delete({'matterSlug': matterSlug, 'itemSlug': itemSlug, 'username': participant.username },
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
	}]
);