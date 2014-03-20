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
	function( $q, $resource, API_BASE_URL ) {

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
			return $resource( API_BASE_URL + 'matters/:matterSlug/items/:itemSlug/comment', {}, {
				'create': { 'method': 'POST', 'headers': { 'Content-Type': 'application/json'}}
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
			}


		};
	}]
);
