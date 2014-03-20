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
    'btford.markdown',
    'monospaced.elastic',
    'angularFileUpload'
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
    });
    /*
    $routeSegmentProvider.within('checklist').segment('itemInfo', {
    'templateUrl': '/static/ng/partial/checklist/includes/itemdetails.html'});
    */
   
    $urlRouterProvider.otherwise('/checklist'); 
});

//Required to be compatible with the django CSRF protection
angular.module('toolkit-gui').config(['$httpProvider', function($httpProvider) {
    $httpProvider.defaults.xsrfCookieName = 'csrftoken';
    $httpProvider.defaults.xsrfHeaderName = 'X-CSRFToken';    }
]);


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