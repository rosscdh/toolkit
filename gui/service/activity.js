angular.module('toolkit-gui')
/**
 * @class activityService
 * @classdesc 		                      Responsible for managing and requesting the API to invite participants into a matter
 * @param  {Function} $q                  Contains the scope of this controller
 * @param  {Function} $resource           Provides access to close and cancel methods
 * @param  {Function} anon                Controller function
 */
.factory('activityService',[
	'$q',
	'$resource',
	'API_BASE_URL',
	function( $q, $resource, API_BASE_URL ) {

		/**
		 * Returns a key/value object containing $resource methods to access matter API end-points
		 *
		 * @name				activityResource
		 *
		 * @private
		 * @method				activityResource
		 * @memberof			activityService
		 *
		 * @return {Function}   $resource
		 */
		function activityResource() {
			return $resource( API_BASE_URL + 'matters/:matterSlug/activity', {}, {
				'list': { 'method': 'GET', 'headers': { 'Content-Type': 'application/json'}}
			});
		}

		return {

			/**
			 * Requests a list of activity items from the API
			 *
			 * @name				list
			 *
			 * @example
		 	 * activityService.list( mySelectedMatter );
			 *
			 * @public
			 * @method				list
			 * @memberof			matterService
			 *
			 * @return {Promise}    Array of matters
		 	 */
			'list': function(matterSlug) {
				var api = activityResource();
				var deferred = $q.defer();

				api.list({'matterSlug': matterSlug},
					function success( result ) {
						deferred.resolve( result.results );
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
