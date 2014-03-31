

angular.module('toolkit-gui')
// register the interceptor as a service
    .factory('myHttpInterceptor', ['$q', '$exceptionHandler', '$rootScope', '$log', function ($q, $exceptionHandler, $rootScope, $log, $location) {
        return {

            'request': function(config) {
                var timestamp = new Date().getTime();

                var contenttype = config.headers["Content-Type"];
                if(contenttype === "application/json"){
                    if(config.url.indexOf('?') < 0) {
                        config.url += '?t=' + timestamp;
                    } else {
                        config.url += '&t=' + timestamp;
                    }
                }

                return config || $q.when(config);
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

