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
    'monospaced.elastic'
]);

angular.module('toolkit-gui').config(function($routeProvider) {

    $routeProvider.
    when('/',{templateUrl: '/static/ng/partial/home/home.html'}).
	when('/matters/:matterSlug/checklist',{'templateUrl': '/static/ng/partial/checklist/checklist.html', 'controller': 'ChecklistCtrl'}).
	when('/matters/:matterSlug/closing',{templateUrl: '/static/ng/partial/closing/closing.html'}).
	when('/matters/:id/closing',{templateUrl: '/static/ng/partial/closing/closing.html'}).
	when('/matters/:matterSlug/invite',{templateUrl: '/static/ng/partial/participant-invite/participant-invite.html'}).
	when('/matters/:matterSlug/attachment/:id',{templateUrl: '/static/ng/partial/view-document/view-document.html'}).

    otherwise({redirectTo:'/'});
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

    $rootScope.API_BASE_URL = "http://localhost:8000/api/v1/";
});
