angular.module('toolkit-gui')
/**
 * @class activityService
 * @classdesc 		                      Responsible for managing and requesting the API to invite participants into a matter
 * @param  {Function} $q                  Contains the scope of this controller
 * @param  {Function} $resource           Provides access to close and cancel methods
 * @param  {Function} anon                Controller function
 */
.factory('commentService',[
	'$q',
	'$resource',
	'API_BASE_URL',
    '$log',
	function( $q, $resource, API_BASE_URL, $log ) {

		/**
		 * Returns a key/value object containing $resource methods to access comment API end-points
		 *
		 * @name				commentResource
		 *
		 * @private
		 * @method				commentResource
		 * @memberof			commentService
		 *
		 * @return {Function}   $resource
		 */
		function commentResource() {
			return $resource( API_BASE_URL + 'matters/:matterSlug/items/:itemSlug/comment/:id', {}, {
				'create': { 'method': 'POST', 'headers': { 'Content-Type': 'application/json'}},
				'delete': { 'method': 'DELETE', 'headers': { 'Content-Type': 'application/json'}}
			});
		}

		return {


            /**
			 * Creates a new comment
			 *
			 * @name				create
			 *
			 * @example
		 	 * commentService.create( mySelectedMatter, myItem, myComment );
			 *
			 * @public
			 * @method				create
			 * @memberof			commentService
			 *
			 * @return {Promise}
		 	 */
			'create': function(matterSlug, itemSlug, comment) {
				var api = commentResource();
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
		 	 * commentService.delete( mySelectedMatter, myItem, myComment );
			 *
			 * @public
			 * @method				delete
			 * @memberof			commentService
			 *
			 * @return {Promise}
		 	 */
			'delete': function(matterSlug, itemSlug, comment) {
				var api = commentResource();
				var deferred = $q.defer();
                $log.debug(comment);

				api.delete({'matterSlug': matterSlug, 'itemSlug': itemSlug, 'id':comment.id},
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
