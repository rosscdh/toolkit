

angular.module('toolkit-gui')
// register the interceptor as a service
    .factory('myHttpInterceptor', ['$q', '$exceptionHandler', '$rootScope', '$log', function ($q, $exceptionHandler, $rootScope, $log) {
        return {
            'response': function (response) {
                return response || $q.when(response);
            },

            'responseError': function (rejection) {
                $exceptionHandler("API " + rejection.config.method + " call to URL " + rejection.config.url + " failed with status " + rejection.status);

                var status = rejection.status;
                if (status === 403) {
                    $log.debug("Authentication failed");
                    $rootScope.$broadcast('authenticationRequired', true);

                    return;
                }

                return $q.reject(rejection);
            }
        };
    }])
    .config(['$httpProvider', function ($httpProvider) {
        $httpProvider.interceptors.push('myHttpInterceptor');
    }]);


angular.module('toolkit-gui')
/**
 * @class baseService
 * @classdesc                             Responsible for managing and requesting the API.
 * @param  {Function} $q                  Contains the scope of this controller
 * @param  {Function} $resource           Provides access to close and cancel methods
 * @param  {Function} anon                Controller function
 */
.factory('baseService',[
    '$q',
    '$resource',
    '$log',
    function( $q, $resource, $log ) {

        return {

            'loadObjectByUrl': function (url ) {
                var deferred = $q.defer();

                if(url) {
                    var api = $resource( url, {}, {
                        'get': { 'method': 'GET', 'headers': { 'Content-Type': 'application/json'/*, 'token': token.value*/ } }
                    });

                    api.get({},
                        function success(obj){
                            deferred.resolve(obj);
                        },
                        function error(err) {
                            deferred.reject( err );
                        }
                    );
                } else {
                    setTimeout(function(){
                        deferred.reject( new Error('Invalid url provided') );
                    },1);
                }

                return deferred.promise;
            }
        };
     }]
);