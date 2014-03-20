angular.module('toolkit-gui', [
    'ui.bootstrap',
    'ui.sortable',
    'ui.utils',
    'ez.confirm',
    'toaster',
    'ngRoute',
    'ngAnimate',
    'ngResource',
    'btford.markdown',
    'monospaced.elastic',
    'angularFileUpload'
]);

angular.module('toolkit-gui').config(function($routeProvider) {

    $routeProvider.
    when('/',{templateUrl: '/static/ng/partial/home/home.html'}).
	when('/checklist',{'templateUrl': '/static/ng/partial/checklist/checklist.html', 'controller': 'ChecklistCtrl'}).
	when('/closing',{templateUrl: '/static/ng/partial/closing/closing.html'}).
	when('/closing',{templateUrl: '/static/ng/partial/closing/closing.html'}).
	when('/invite',{templateUrl: '/static/ng/partial/participant-invite/participant-invite.html'}).
	when('/attachment/:id',{templateUrl: '/static/ng/partial/view-document/view-document.html'}).

    otherwise({redirectTo:'/'});
});


/**
 * Required to be compatible with the django CSRF protection
 *
 * @memberof			setup.js
 *
 */
angular.module('toolkit-gui').config(['$httpProvider', function($httpProvider) {
    $httpProvider.defaults.xsrfCookieName = 'csrftoken';
    $httpProvider.defaults.xsrfHeaderName = 'X-CSRFToken';    }
]);



/**
 * Overrides the default exceptionHandler and uses sentry for the exception messages
 *
 * @memberof			setup.js
 *
 */
angular.module('toolkit-gui').factory('$exceptionHandler', ['$window', '$log', 'SENTRY_PUBLIC_DSN', function ($window,   $log, SENTRY_PUBLIC_DSN) {
    if ($window.Raven) {
        $log.debug('Using the RavenJS exception handler.');
        $window.Raven.config(SENTRY_PUBLIC_DSN).install();

        return function (exception, cause) {
            $log.error.apply($log, arguments);
            $window.Raven.captureException(exception);
        };
    } else {
        $log.debug('Using the default logging exception handler.');
        return function (exception, cause) {
            $log.error.apply($log, arguments);
        };
    }
  }
]);


/**
 * Enables/Disables the debug log messages
 *
 * @memberof			setup.js
 *
 */
angular.module('toolkit-gui').config(function($logProvider, DEBUG_MODE){
  $logProvider.debugEnabled(DEBUG_MODE);
});



angular.module('toolkit-gui').run(function($rootScope) {
	$rootScope.safeApply = function(fn) {
		var phase = $rootScope.$$phase;
		if (phase === '$apply' || phase === '$digest') {
			if (fn && (typeof(fn) === 'function')) {
				fn();
			}
		} else {
			this.$apply(fn);
		}
	};

});
