angular.module('toolkit-gui')
/**
 * @class activityService
 * @classdesc 		                      Responsible for managing and requesting the API to invite participants into a matter
 * @param  {Function} $q                  Contains the scope of this controller
 * @param  {Function} $resource           Provides access to close and cancel methods
 * @param  {Function} anon                Controller function
 */
.factory('attachmentService',[
	'$q',
	'$resource',
	'API_BASE_URL',
	'$upload',
    '$log',
	function( $q, $resource, API_BASE_URL, $upload, $log ) {

		/**
		 * Returns a key/value object containing $resource methods to access attachment API end-points
		 *
		 * @name				attachmentResource
		 *
		 * @private
		 * @method				attachmentResource
		 * @memberof			attachmentService
		 *
		 * @return {Function}   $resource
		 */
		function attachmentResource() {
			return $resource( API_BASE_URL + 'matters/:matterSlug/items/:itemSlug/attachment/:id', {}, {
				'query': { 'method': 'GET', 'headers': { 'Content-Type': 'application/json'}},
				'create': { 'method': 'POST', 'headers': { 'Content-Type': 'application/json'}},
				'delete': { 'method': 'DELETE', 'headers': { 'Content-Type': 'application/json'}},
				'update': { 'method': 'PATCH', 'headers': { 'Content-Type': 'application/json'}}
			});
		}

		return {
        
              /**
			 * Loads all attachments from the given item
			 *
			 * @name				query
			 *
			 * @example
			 * attachmentService.query.query( mySelectedMatter, myItem, myAttachment );
			 *
			 * @public
			 * @method				query
			 * @memberof			attachmentService
			 *
			 * @return {Promise}
		 	 */
			'query': function(matterSlug, itemSlug) {
				var api = attachmentResource();
				var deferred = $q.defer();

				api.query({'matterSlug': matterSlug, 'itemSlug': itemSlug}, {},
					function success(response) {
						deferred.resolve(response.results);
					},
					function error( err ) {
						deferred.reject( err );
					}
				);

				return deferred.promise;
			},


            /**
			 * Creates a new attachment
			 *
			 * @name				create
			 *
			 * @example
			 * attachmentService.create.create( mySelectedMatter, myItem, myAttachment );
			 *
			 * @public
			 * @method				create
			 * @memberof			attachmentService
			 *
			 * @return {Promise}
		 	 */
			'createOld': function(matterSlug, itemSlug, attachment) {
				var api = attachmentResource();
				var deferred = $q.defer();

				api.create({'matterSlug': matterSlug, 'itemSlug': itemSlug}, {'attachment': attachment},
					function success() {
						deferred.resolve();
					},
					function error( err ) {
						deferred.reject( err );
					}
				);

				return deferred.promise;
			},

            /**
			 * Upload a specific attachment into a checklist item revision
			 * @param  {String} matterSlug unique identifier for a specific matter
			 * @param  {String} itemSlug   Unique identifier for a specific checklist item within the matter
			 * @param  {Array} $files     Array of files (HTML5 files object)
			 * @return {Promise}
			 */
			'uploadFile': function( matterSlug, itemSlug, $files ) {
				var deferred = $q.defer(), /*files,*/ url;
				var uploadHandle;

				//var api = revisionItemResource();

				if( $files.length>0 ) {
					url = API_BASE_URL + 'matters/'+matterSlug+'/items/'+itemSlug+'/attachment';
					var file = $files[0];

					uploadHandle = $upload.upload({
						'url': url, //upload.php script, node.js route, or servlet url
						'file': file,
						'fileFormDataName': 'file'
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
			 * Deletes the given attachment
			 *
			 * @name				delete
			 *
			 * @example
			 * attachmentService.delete( mySelectedMatter, myItem, attachmentId );
			 *
			 * @public
			 * @method				delete
			 * @memberof			attachmentService
			 *
			 * @return {Promise}
		 	 */
			'delete': function(matterSlug, itemSlug, attachmentId) {
				var api = attachmentResource();
				var deferred = $q.defer();

				api.delete({'matterSlug': matterSlug, 'itemSlug': itemSlug, 'id':attachmentId},
					function success() {
						deferred.resolve();
					},
					function error( err ) {
						deferred.reject( err );
					}
				);

				return deferred.promise;
			},

             /**
			 * Saves the given attachment
			 *
			 * @name				delete
			 *
			 * @example
			 * attachmentService.update( mySelectedMatter, myItem, attachmentId, attachment );
			 *
			 * @public
			 * @method				update
			 * @memberof			attachmentService
			 *
			 * @return {Promise}
		 	 */
			'update': function(matterSlug, itemSlug, attachmentId, attachment) {
				var api = attachmentResource();
				var deferred = $q.defer();

				api.update({'matterSlug': matterSlug, 'itemSlug': itemSlug, 'id':attachmentId}, {'attachment': attachment},
					function success() {
						deferred.resolve();
					},
					function error( err ) {
						deferred.reject( err );
					}
				);

				return deferred.promise;
			}

		};
	}]
);
