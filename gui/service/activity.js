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


		var nextUrl = {
			'matter': null,
			'item': null,
			'mostRecentRequestType': null
		};

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

			'hasMoreItems': function( activityListType ) {
				//
				return nextUrl[activityListType];
			},

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

				if(getMore && nextUrl.matter) {
					$http({'method': 'GET', 'url': nextUrl.matter }).
					success(function(result, status, headers, config) {
						nextUrl.matter = result.next;
						deferred.resolve( result.results );
					}).
					error(function(err, status, headers, config) {
						deferred.reject( err );
					});
				} else {
					api.list({'matterSlug': matterSlug},
						function success( result ) {
							nextUrl.matter = result.next;
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

				if(getMore && nextUrl.item) {
					$http({'method': 'GET', 'url': nextUrl.item }).
					success(function(result, status, headers, config) {
						nextUrl.item = result.next;
						deferred.resolve( result.results );
					}).
					error(function(err, status, headers, config) {
						deferred.reject( err );
					});
				} else {
					api.list({'matterSlug': matterSlug, 'itemSlug': itemSlug},
						function success( result ) {
							nextUrl.item = result.next;
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
