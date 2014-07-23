angular.module('toolkit-gui')
/**
 * @class activityService
 * @classdesc 		                      Responsible for managing and requesting the API to invite participants into a matter
 * @param  {Function} $q                  Contains the scope of this controller
 * @param  {Function} $resource           Provides access to close and cancel methods
 * @param  {Function} anon                Controller function
 */
.factory('taskService',[
	'$q',
	'$resource',
	'API_BASE_URL',
    '$log',
	function( $q, $resource, API_BASE_URL, $log ) {

		/**
		 * Returns a key/value object containing $resource methods to access task API end-points
		 *
		 * @name				taskResource
		 *
		 * @private
		 * @method				taskResource
		 * @memberof			taskService
		 *
		 * @return {Function}   $resource
		 */
		function taskResource() {
			return $resource( API_BASE_URL + 'matters/:matterSlug/items/:itemSlug/tasks/:taskSlug', {}, {
				// @dennis "query" should be "retrieve" to conform to the rest_framework conventions?
				'query': { 'method': 'GET', 'headers': { 'Content-Type': 'application/json'}},
				'create': { 'method': 'POST', 'headers': { 'Content-Type': 'application/json'}},
				'delete': { 'method': 'DELETE', 'headers': { 'Content-Type': 'application/json'}},
				'update': { 'method': 'PATCH', 'headers': { 'Content-Type': 'application/json'}}
			});
		}

		return {


            /**
			 * Loads all tasks from the given item
			 *
			 * @name				query
			 *
			 * @example
			 * taskService.query.query( mySelectedMatter, myItem, myTask );
			 *
			 * @public
			 * @method				query
			 * @memberof			taskService
			 *
			 * @return {Promise}
		 	 */
			'query': function(matterSlug, itemSlug) {
				var api = taskResource();
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
			 * Creates a new task
			 *
			 * @name				create
			 *
			 * @example
			 * taskService.create.create( mySelectedMatter, myItem, myTask );
			 *
			 * @public
			 * @method				create
			 * @memberof			taskService
			 *
			 * @return {Promise}
		 	 */
			'create': function(matterSlug, itemSlug, task) {
				var api = taskResource();
				var deferred = $q.defer();

				api.create({'matterSlug': matterSlug, 'itemSlug': itemSlug}, task,
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
			 * Deletes the given task
			 *
			 * @name				delete
			 *
			 * @example
			 * taskService.delete( mySelectedMatter, myItem, taskId );
			 *
			 * @public
			 * @method				delete
			 * @memberof			taskService
			 *
			 * @return {Promise}
		 	 */
			'delete': function(matterSlug, itemSlug, taskSlug) {
				var api = taskResource();
				var deferred = $q.defer();

				api.delete({'matterSlug': matterSlug, 'itemSlug': itemSlug, 'taskSlug':taskSlug},
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
			 * Saves the given task
			 *
			 * @name				delete
			 *
			 * @example
			 * taskService.update( mySelectedMatter, myItem, taskId, task );
			 *
			 * @public
			 * @method				update
			 * @memberof			taskService
			 *
			 * @return {Promise}
		 	 */
			'update': function(matterSlug, itemSlug, taskSlug, task) {
				var api = taskResource();
				var deferred = $q.defer();

				api.update({'matterSlug': matterSlug, 'itemSlug': itemSlug, 'taskSlug': taskSlug}, task ,
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
