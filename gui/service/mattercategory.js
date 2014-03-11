var category;

angular.module('toolkit-gui')
/**
 * @class matterCategoryService
 * @classdesc 		                      Responsible for managing and requesting the API to invite participants into a matter
 * @param  {Function} $q                  Contains the scope of this controller
 * @param  {Function} $resource           Provides access to close and cancel methods
 * @param  {Function} $rootScope          Access to the root sccope
 * @param  {Function} anon                Controller function
 */
.factory('matterCategoryService',[
        '$q',
        '$resource',
        '$rootScope',
        function( $q, $resource, $rootScope) {
            var token = { 'value': 'xyz' };

            function matterCategoryResource() {
                return $resource( $rootScope.API_BASE_URL + 'matters/:matterSlug/category/:categorySlug', {}, {
                    'create': { 'method': 'POST', 'headers': { 'Content-Type': 'application/json'/*, 'token': token.value*/ }, 'isArray': true},
                    'update': { 'method': 'PATCH', params:{'categorySlug':'@categorySlug'},'headers': { 'Content-Type': 'application/json'/*, 'token': token.value*/ } , 'isArray': true},
                    'delete': { 'method': 'DELETE', params:{'categorySlug':'@categorySlug'},'headers': { 'Content-Type': 'application/json'/*, 'token': token.value*/ }, 'isArray': true}
                });
            }

            return {
                'data': function() {
                    return category;
                },

                'create': function ( matterSlug, categoryName ) {
                    var deferred = $q.defer();

                    var api = matterCategoryResource();

                    api.create({'matterSlug': matterSlug, 'categorySlug': categoryName}, {},
                        function success(){
                            deferred.resolve();
                        },
                        function error(err) {
                            deferred.reject( err );
                        }
                    );

                    return deferred.promise;
                },

                'update': function ( matterSlug, oldCategoryName, newCategoryName ) {
                    var deferred = $q.defer();

                    var api = matterCategoryResource();

                    api.update({'matterSlug': matterSlug, 'categorySlug': oldCategoryName}, {'category': newCategoryName },
                        function success(category){
                            deferred.resolve(category);
                        },
                        function error(err) {
                            deferred.reject( err );
                        }
                    );

                    return deferred.promise;
                },

                'delete': function ( matterSlug, category ) {
                    var deferred = $q.defer();

                    var api = matterCategoryResource();

                    api.delete({'matterSlug': matterSlug, 'categorySlug': category.name},
                        function success(){
                            deferred.resolve();
                        },
                        function error(err) {
                            deferred.reject( err );
                        }
                    );

                    return deferred.promise;
                }

            };
}]);