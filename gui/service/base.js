

angular.module('toolkit-gui')
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

