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
	'$timeout',
	'matterService',
	'API_BASE_URL',
	function( $q, $resource, $rootScope, $upload, $timeout, matterService, API_BASE_URL) {
		'use strict';
		/**
		 * TBC: this variable will contain the JWT token required to make authenticated requests
		 * @memberof matterItemService
		 * @type {Object}
		 * @private
		 */
		//var token = { 'value': 'xyz' };

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
			return $resource( API_BASE_URL + 'matters/:matterSlug/items/:itemSlug/:document/:action', {}, {
				'create': { 'method': 'POST', 'headers': { 'Content-Type': 'application/json'/*, 'token': token.value*/ }},
				'update': { 'method': 'PATCH', 'headers': { 'Content-Type': 'application/json'/*, 'token': token.value*/ }},
				'delete': { 'method': 'DELETE', 'headers': { 'Content-Type': 'application/json'/*, 'token': token.value*/ }},
				'requestdocument': { 'method': 'PATCH', 'params':{'document':'request_document'},'headers': { 'Content-Type': 'application/json'/*, 'token': token.value*/ }},
				'remind': { 'method': 'POST', 'params':{'document':'request_document', 'action':'remind'},'headers': { 'Content-Type': 'application/json'/*, 'token': token.value*/ }}
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


		 /**
		 * Returns a key/value object containing $resource methods to access review API end-points
		 *
		 * @name				reviewerItemResource
		 *
		 * @private
		 * @method				reviewerItemResource
		 * @memberof			matterItemService
		 *
		 * @return {Function}   $resource
		 */
		function reviewerItemResource() {
			return $resource( API_BASE_URL + 'matters/:matterSlug/items/:itemSlug/revision/:type/:username:action', {}, {
				'request': { 'method': 'POST', 'params' : { 'type': 'reviewers' }, 'headers': { 'Content-Type': 'application/json'/*, 'token': token.value*/ }},
				'remind': { 'method': 'POST', 'params': { 'type': 'reviewers', 'action':'remind'}, 'headers': { 'Content-Type': 'application/json'/*, 'token': token.value*/ }},
				'delete': { 'method': 'DELETE', 'params' : { 'type': 'reviewer' }, 'headers': { 'Content-Type': 'application/json'/*, 'token': token.value*/ }}
			});
		}

		/**
		 * Returns a key/value object containing $resource methods to access signatory API end-points
		 *
		 * @name				signerItemResource
		 *
		 * @private
		 * @method				signerItemResource
		 * @memberof			matterItemService
		 *
		 * @return {Function}   $resource
		 */
		function signerItemResource() {
			return $resource( API_BASE_URL + 'matters/:matterSlug/items/:itemSlug/revision/:type/:username:action', {}, {
				'request': { 'method': 'POST', 'params' : { 'type': 'signers' }, 'headers': { 'Content-Type': 'application/json'}},
				'remind': { 'method': 'POST', 'params': { 'type': 'signers', 'action':'remind'}, 'headers': { 'Content-Type': 'application/json'/*, 'token': token.value*/ }},
				'delete': { 'method': 'DELETE', 'params' : { 'type': 'signer' }, 'headers': { 'Content-Type': 'application/json'}}
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
					'status': 0,
					'name': itemName,
					'category': categoryName,
					'matter': API_BASE_URL + 'matters/' + matterSlug,
					'parent': null,
					'children': [],
					'closing_group': null,
					'latest_revision': null,
					'is_final': false,
					'is_complete': false,
					'date_due': null
				};

				api.create({'matterSlug': matterSlug }, matterItem,
					function success(item){
						deferred.resolve(item);
						matterService.insertItem( item ); /* keep search results up to date */
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
			'uploadRevision': function( matterSlug, itemSlug, files, status ) {
				var deferred = $q.defer();

				var api = revisionItemResource();

				var fileurl = files[0].url;
				var filename = files[0].filename;

				api.create({'matterSlug': matterSlug, 'itemSlug': itemSlug }, { 'executed_file': fileurl, 'name': filename, 'status':status },
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
				var deferred = $q.defer(), /*files,*/ url;
				var uploadHandle;

				//var api = revisionItemResource();

				if( $files.length>0 ) {
					url = API_BASE_URL + 'matters/'+matterSlug+'/items/'+itemSlug+'/revision';
					var file = $files[0];

					uploadHandle = $upload.upload({
						'url': url, //upload.php script, node.js route, or servlet url
						'file': file,
						'fileFormDataName': 'executed_file',
					}).progress(function(evt) {
						console.log('percent: ' + parseInt(100.0 * evt.loaded / evt.total));

						deferred.notify(parseInt(100.0 * evt.loaded / evt.total));
					}).success(function(data/*, status, headers, config*/) {
						// file is uploaded successfully
						deferred.resolve(data);
						//console.log(data);
					}).error(function(){
						var err = new Error('Unable to upload file');
						if( uploadHandle.canceled ) {
							err = new Error('Upload canceled');
							err.title = 'Canceled';
							deferred.reject(err);
						} else {
							deferred.reject(err);
						}
						
					});
				} else {
					$timeout(
						function(){
							deferred.reject();
						},
					1);
				}

				deferred.promise.uploadHandle = uploadHandle;

				return deferred.promise;
			},

			/**
			 * Requests a revision update
			 *
			 * @name				updateRevision
			 * @param {String}      matterSlug    Database slug, used as a unique identifier for a matter.
			 * @param {String}      itemSlug      Database slug, used as a unique identifier for a checklist item.
			 * @param {Object}      revision      The revision object to update
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
			 * Requests the API to delete a specific revision.
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

			 /**
			 * Requests the API to delete the revision request.
			 *
			 * @name				deleteRevisionRequest
			 * @param {String}      matterSlug    Database slug, used as a unique identifier for a matter.
			 * @param {String}      itemSlug      Database slug, used as a unique identifier for a checklist item.
			 *
			 * @example
			 * matterItemService.deleteRevisionRequest( 'myMatterName', 'myItemName' );
			 *
			 * @public
			 * @method				deleteRevisionRequest
			 * @memberof			matterItemService
			 *
			 * @return {Promise}
			 */
			'deleteRevisionRequest': function ( matterSlug, itemSlug ) {
				var deferred = $q.defer();

				var api = matterItemResource();

				api.update({'matterSlug': matterSlug, 'itemSlug': itemSlug }, {'is_requested':false, 'responsible_party':null},
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
			'requestRevisionReview': function ( matterSlug, itemSlug, reviewer ) {
				var deferred = $q.defer();

				var api = reviewerItemResource();

				api.request({'matterSlug': matterSlug, 'itemSlug': itemSlug }, reviewer,
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
			'deleteRevisionReviewRequest': function ( matterSlug, itemSlug, review ) {
				var deferred = $q.defer();

				var api = reviewerItemResource();

				api.delete({'matterSlug': matterSlug, 'itemSlug': itemSlug, 'username': review.reviewer.username },
					function success(){
						deferred.resolve();
					},
					function error(err) {
						deferred.reject( err );
					}
				);

				return deferred.promise;
			},

			 'requestSigner': function ( matterSlug, itemSlug, signer ) {
				var deferred = $q.defer();

				var api = signerItemResource();

				api.request({'matterSlug': matterSlug, 'itemSlug': itemSlug }, signer,
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
			 * Requests the API to send a reminder to all signers who have not signed the current revision yet.
			 *
			 * @name				remindRevisionSigners
			 * @param {String}      matterSlug    Database slug, used as a unique identifier for a matter.
			 * @param {String}      itemSlug      Database slug, used as a unique identifier for a checklist item.
			 *
			 * @example
			 * matterItemService.remindRevisionSigners( 'myMatterName', 'myItemName' );
			 *
			 * @public
			 * @method				remindRevisionSigners
			 * @memberof			matterItemService
			 *
			 * @return {Promise}
			 */
			'remindRevisionSigners': function ( matterSlug, itemSlug ) {
				var deferred = $q.defer();

				var api = signerItemResource();

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
			'deleteSigningRequest': function ( signing ) {
				var deferred = $q.defer();

				var api = $resource( signing.url, {}, {
						'delete': { 'method': 'DELETE', 'headers': { 'Content-Type': 'application/json'} }
				});

				api.delete({},
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
			 * Requests a review update
			 *
			 * @name				updateRevisionReview
			 * @param {Object}      review        The review object to update
			 *
			 * @example
			 * matterItemService.updateRevisionReview( {} );
			 *
			 * @public
			 * @method				updateRevisionReview
			 * @memberof			matterItemService
			 *
			 * @return {Promise}    Updated item object as provided by API
			 */
			'updateRevisionReview': function ( review ) {
				var deferred = $q.defer(), api, updateFields;

				if( review.url ) {
					api = $resource(review.url, {}, {
						'update': { 'method': 'PATCH', 'headers': { 'Content-Type': 'application/json'/*, 'token': token.value*/ }}
					});

					updateFields = {
						'is_complete': review.is_complete
					};

					api.update({}, updateFields,
						function success(item){
							deferred.resolve(item);
						},
						function error(err) {
							deferred.reject( err );
						}
					);
				} else {
					// Invalid url provided
					$timeout( function(){
						deferred.reject( new Error('Unable to update revision') );
					}, 1);
				}

				return deferred.promise;
			}
		};
	}]
);