angular.module('toolkit-gui')
/**
 * @class activityService
 * @classdesc 		                      Responsible for managing and requesting the API to invite participants into a matter
 * @param  {Function} $q                  Contains the scope of this controller
 * @param  {Function} $resource           Provides access to close and cancel methods
 * @param  {Function} anon                Controller function
 */
.factory('matterCommentService',[
	'$q',
	'$resource',
	'API_BASE_URL',
    '$log',
	function( $q, $resource, API_BASE_URL, $log ) {

		/**
		 * Returns a key/value object containing $resource methods to access comment API end-points
		 *
		 * @name				matterCommentResource
		 *
		 * @private
		 * @method				matterCommentResource
		 * @memberof			matterCommentService
		 *
		 * @return {Function}   $resource
		 */
		function matterCommentResource() {
			return $resource( API_BASE_URL + 'matters/:matterSlug/comment/:id', {}, {
				'list': { 'method': 'GET', 'headers': { 'Content-Type': 'application/json'}},
				'create': { 'method': 'POST', 'headers': { 'Content-Type': 'application/json'}},
				'delete': { 'method': 'DELETE', 'headers': { 'Content-Type': 'application/json'}},
				'update': { 'method': 'PATCH', 'headers': { 'Content-Type': 'application/json'}}
			});
		}

		return {


            /**
			 * List of Parent Comemnts
			 *
			 * @name				list
			 *
			 * @example
		 	 * matterCommentService.list( mySelectedMatter, myComment );
			 *
			 * @public
			 * @method				list
			 * @memberof			matterCommentService
			 *
			 * @return {Promise}
		 	 */
			'list': function(matterSlug) {
				var api = matterCommentResource();
				var deferred = $q.defer();

				api.list({'matterSlug': matterSlug}, {},
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
			 * Creates a new comment
			 *
			 * @name				create
			 *
			 * @example
		 	 * matterCommentService.create( mySelectedMatter, myComment );
			 *
			 * @public
			 * @method				create
			 * @memberof			matterCommentService
			 *
			 * @return {Promise}
		 	 */
			'create': function(matterSlug, comment) {
				var api = matterCommentResource();
				var deferred = $q.defer();

				api.create({'matterSlug': matterSlug}, {'comment': comment},
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
			 * Deletes the given comment
			 *
			 * @name				delete
			 *
			 * @example
		 	 * matterCommentService.delete( mySelectedMatter, commentId );
			 *
			 * @public
			 * @method				delete
			 * @memberof			matterCommentService
			 *
			 * @return {Promise}
		 	 */
			'delete': function(matterSlug, commentId) {
				var api = matterCommentResource();
				var deferred = $q.defer();

				api.delete({'matterSlug': matterSlug, 'id':commentId},
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
			 * Saves the given comment
			 *
			 * @name				delete
			 *
			 * @example
		 	 * matterCommentService.update( mySelectedMatter, commentId, comment );
			 *
			 * @public
			 * @method				update
			 * @memberof			matterCommentService
			 *
			 * @return {Promise}
		 	 */
			'update': function(matterSlug, commentId, comment) {
				var api = matterCommentResource();
				var deferred = $q.defer();

				api.update({'matterSlug': matterSlug, 'id':commentId}, {'comment': comment},
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
