angular.module('toolkit-gui')
// override the default exceptionHandler
.factory('$exceptionHandler', ['$window', '$log', 'SENTRY_PUBLIC_DSN', function ($window,   $log, SENTRY_PUBLIC_DSN) {
    if ($window.Raven) {
        console.log('Using the RavenJS exception handler.');
        $window.Raven.config(SENTRY_PUBLIC_DSN).install();

        return function (exception, cause) {
            $log.error.apply($log, arguments);
            $window.Raven.captureException(exception);
        };
    } else {
        console.log('Using the default logging exception handler.');
        return function (exception, cause) {
            $log.error.apply($log, arguments);
        };
    }
  }
])
// register the interceptor as a service
.factory('myHttpInterceptor', ['$q', '$exceptionHandler', function ($q, $exceptionHandler) {
    return {
        'responseError': function (rejection) {
            $exceptionHandler("API " + rejection.config.method + " call to URL " + rejection.config.url + " failed with status " + rejection.status);

            // to make it work: https://rahul.ag/angular-interceptor-401
            /*var status = response.status;
            if (status == 401) {
                //AuthFactory.clearUser();
                window.location = "/";
                return;
            }*/

            return $q.reject(rejection);
        }
    };
}])
.config(['$httpProvider', function($httpProvider) {
    $httpProvider.interceptors.push('myHttpInterceptor');
}]);

