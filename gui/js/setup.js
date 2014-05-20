angular.module('toolkit-gui', [
    'ui.bootstrap',
    'ui.sortable',
    'ui.utils',
    'ez.confirm',
    'toaster',
    'ngRoute',
    'ui.router',
    'ngAnimate',
    'ngResource',
    'ngSanitize',
    'btford.markdown',
    'monospaced.elastic',
    'angularFileUpload',
    'ngCookies',
    'ngIntercom'
]);

angular.module('toolkit-gui').config(function($stateProvider, $urlRouterProvider) {
    /*
    $routeProvider.
    when('/',{templateUrl: '/static/ng/partial/home/home.html'}).
	when('/checklist',{'templateUrl': '/static/ng/partial/checklist/checklist.html', 'controller': 'ChecklistCtrl'}).
    when('/checklist/:itemSlug',{'templateUrl': '/static/ng/partial/checklist/checklist.html', 'controller': 'ChecklistCtrl'}).
	when('/closing',{templateUrl: '/static/ng/partial/closing/closing.html'}).
	when('/closing',{templateUrl: '/static/ng/partial/closing/closing.html'}).
	when('/invite',{templateUrl: '/static/ng/partial/participant-invite/participant-invite.html'}).
	when('/attachment/:id',{templateUrl: '/static/ng/partial/view-document/view-document.html'}).

    otherwise({redirectTo:'/'});
    */
   
   $stateProvider
    .state('checklist', {
      'url': "/checklist",
      'controller': 'ChecklistCtrl',
      'templateUrl': '/static/ng/partial/checklist/checklist.html'
    })
    .state('checklist.item', {
      'url': "/:itemSlug",
      'templateUrl': '/static/ng/partial/checklist/includes/itemdetails.html',
      'controller': function($scope) {}
    })
    .state('checklist.item.revision', {
      'url': "/revision/:revisionSlug",
      'controller': function($scope) {}
    })
    .state('checklist.item.revision.review', {
      'url': "/review/:reviewSlug",
      'controller': function($scope) {}
    });

    /*
    $routeSegmentProvider.within('checklist').segment('itemInfo', {
    'templateUrl': '/static/ng/partial/checklist/includes/itemdetails.html'});
    */
   
    $urlRouterProvider.otherwise('/checklist'); 
});

/**
 * Pusher API key
 */
//angular.module('toolkit-gui').constant('pusher_api_key','60281f610bbf5370aeaa');


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


/**
 * Setup intercom.io
 *
 * @memberof			setup.js
 *
 */

// angular.module('toolkit-gui')
//     .config(function (IntercomServiceProvider) {
//         IntercomServiceProvider
//             .asyncLoading(true)
//             // manually set url since there is no local server running
//             .scriptUrl('https://static.intercomcdn.com/intercom.v1.js');
//     });
// /*
//     .run(['Intercom','$log', 'INTERCOM_API_KEY',function (Intercom, $log, INTERCOM_API_KEY) {
//         $log.debug('booting');
//         Intercom.boot({
//             email: "john.doe@example.com",
//             created_at: 1234567890,
//             app_id: INTERCOM_API_KEY
//         });
//     }]);*/



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
