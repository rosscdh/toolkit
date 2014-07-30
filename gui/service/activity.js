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
	'$http',
	'$resource',
	'API_BASE_URL',
	function( $q, $http, $resource, API_BASE_URL ) {


		var nextMatterActivityUrl, nextItemActivityUrl;

		/**
		 * Returns a key/value object containing $resource methods to access matter API end-points
		 *
		 * @name				activityResource
		 *
		 * @private
		 * @method				activityMatterResource
		 * @memberof			activityService
		 *
		 * @return {Function}   $resource
		 */
		function activityMatterResource() {
			return $resource( API_BASE_URL + 'matters/:matterSlug/activity', {}, {
				'list': { 'method': 'GET', 'headers': { 'Content-Type': 'application/json'}}
			});
		}

        /**
		 * Returns a key/value object containing $resource methods to access matter API end-points
		 *
		 * @name				activityResource
		 *
		 * @private
		 * @method				activityItemResource
		 * @memberof			activityService
		 *
		 * @return {Function}   $resource
		 */
		function activityItemResource() {
			return $resource( API_BASE_URL + 'matters/:matterSlug/items/:itemSlug/activity', {}, {
				'list': { 'method': 'GET', 'headers': { 'Content-Type': 'application/json'}}
			});
		}

		return {

			/**
			 * Requests a list of activity items for the matter from the API
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
			'matterstream': function(matterSlug, getMore) {
				var api = activityMatterResource();
				var deferred = $q.defer();

				if(getMore && nextMatterActivityUrl) {
					$http({'method': 'GET', 'url': nextMatterActivityUrl }).
					success(function(result, status, headers, config) {
						nextMatterActivityUrl = result.next;
						deferred.resolve( result.results );
					}).
					error(function(err, status, headers, config) {
						deferred.reject( err );
					});
				} else {
					api.list({'matterSlug': matterSlug},
						function success( result ) {
							nextMatterActivityUrl = result.next;
							deferred.resolve( result.results );
						},
						function error( err ) {
							deferred.reject( err );
						}
					);
				}


				return deferred.promise;
			},

            /**
			 * Requests a list of activity items for a checklist item from the API
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
			'itemstream': function(matterSlug, itemSlug, getMore) {
				var api = activityItemResource();
				var deferred = $q.defer();

				if(getMore && nextItemActivityUrl) {
					$http({'method': 'GET', 'url': nextItemActivityUrl }).
					success(function(result, status, headers, config) {
						nextItemActivityUrl = result.next;
						deferred.resolve( result.results );
					}).
					error(function(err, status, headers, config) {
						deferred.reject( err );
					});
				} else {
					api.list({'matterSlug': matterSlug, 'itemSlug': itemSlug},
						function success( result ) {
							nextItemActivityUrl = result.next;
							deferred.resolve( result.results );
						},
						function error( err ) {
							deferred.reject( err );
						}
					);
				}

				return deferred.promise;
			}
		};
	}]
);
