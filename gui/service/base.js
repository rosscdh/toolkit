

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

