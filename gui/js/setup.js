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
    'ngIntercom',
    'oc.lazyLoad'
]);

angular.module('toolkit-gui').config(function($stateProvider, $urlRouterProvider) {

   $stateProvider
    /**
     * Matter: Checklist
     */
    .state('checklist', {
      'url': '/checklist',
      'controller': 'ChecklistCtrl',
      'templateUrl': '/static/ng/partial/checklist/checklist.html'
    })
    .state('checklist.item', {
      'url': '/:itemSlug',
      'templateUrl': '/static/ng/partial/checklist/includes/itemdetails.html',
      'controller': function($scope) {}
    })
    .state('checklist.item.revision', {
      'url': '/revision/:revisionSlug',
      'controller': function($scope) {}
    })
    .state('checklist.item.revision.review', {
      'url': '/review/:reviewSlug',
      'controller': function($scope) {}
    })
    /**
     * Matter: Discussion
     */
    .state('discussion', {
      'url': '/discussion',
      'controller': 'DiscussionCtrl',
      'templateUrl': '/static/ng/partial/discussion/discussion.html'
    })
    .state('discussion.thread', {
      'url': '/:threadSlug',
      'controller': function($scope) {},
      'templateUrl': '/static/ng/partial/discussion/includes/thread.html'
    })
    /**
     * Intake Forms
     */
    .state('intake', {
      'url': '/intake',
      'templateUrl': '/static/ng/partial/intake/intake.html',
      /* // Additional views to load
      'views': {
        'lazyLoadView': {
          'controller': 'IntakeCtrl', // This view will use AppCtrl loaded below in the resolve
          'templateUrl': '/static/ng/partial/intake/intake.html'
        }
      },
      */
      'resolve': {
        'LoadCtrl': ['$ocLazyLoad', function($ocLazyLoad) {
            // you can lazy load files for an existing module
            return $ocLazyLoad.load({
              'name': 'toolkit-gui',
              'files': ['/static/ng/partial/intake/intakeCtrl.js']
            });
          }]
      } 
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

angular.module('toolkit-gui')
  .config(function (IntercomServiceProvider) {
     IntercomServiceProvider
         .asyncLoading(true)
         // manually set url since there is no local server running
         .scriptUrl('https://static.intercomcdn.com/intercom.v1.js');
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
