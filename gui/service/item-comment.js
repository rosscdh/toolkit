angular.module('toolkit-gui')
/**
 * @class activityService
 * @classdesc 		                      Responsible for managing and requesting the API to invite participants into a matter
 * @param  {Function} $q                  Contains the scope of this controller
 * @param  {Function} $resource           Provides access to close and cancel methods
 * @param  {Function} anon                Controller function
 */
.factory('itemCommentService',[
	'$q',
	'$resource',
	'API_BASE_URL',
    '$log',
	function( $q, $resource, API_BASE_URL, $log ) {

		/**
		 * Returns a key/value object containing $resource methods to access comment API end-points
		 *
		 * @name				itemCommentResource
		 *
		 * @private
		 * @method				itemCommentResource
		 * @memberof			itemCommentService
		 *
		 * @return {Function}   $resource
		 */
		function itemCommentResource() {
			return $resource( API_BASE_URL + 'matters/:matterSlug/items/:itemSlug/comment/:id', {}, {
				'create': { 'method': 'POST', 'headers': { 'Content-Type': 'application/json'}},
				'delete': { 'method': 'DELETE', 'headers': { 'Content-Type': 'application/json'}},
				'update': { 'method': 'PATCH', 'headers': { 'Content-Type': 'application/json'}}
			});
		}

		return {


            /**
			 * Creates a new comment
			 *
			 * @name				create
			 *
			 * @example
		 	 * itemCommentService.create( mySelectedMatter, myItem, myComment );
			 *
			 * @public
			 * @method				create
			 * @memberof			itemCommentService
			 *
			 * @return {Promise}
		 	 */
			'create': function(matterSlug, itemSlug, comment) {
				var api = itemCommentResource();
				var deferred = $q.defer();

				api.create({'matterSlug': matterSlug, 'itemSlug': itemSlug}, {'comment': comment},
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
		 	 * itemCommentService.delete( mySelectedMatter, myItem, commentId );
			 *
			 * @public
			 * @method				delete
			 * @memberof			itemCommentService
			 *
			 * @return {Promise}
		 	 */
			'delete': function(matterSlug, itemSlug, commentId) {
				var api = itemCommentResource();
				var deferred = $q.defer();

				api.delete({'matterSlug': matterSlug, 'itemSlug': itemSlug, 'id':commentId},
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
		 	 * itemCommentService.update( mySelectedMatter, myItem, commentId, comment );
			 *
			 * @public
			 * @method				update
			 * @memberof			itemCommentService
			 *
			 * @return {Promise}
		 	 */
			'update': function(matterSlug, itemSlug, commentId, comment) {
				var api = itemCommentResource();
				var deferred = $q.defer();

				api.update({'matterSlug': matterSlug, 'itemSlug': itemSlug, 'id':commentId}, {'comment': comment},
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
