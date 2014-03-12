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

    //$rootScope.API_BASE_URL = "http://localhost:8002/api/v1/";
    // @TODO levels to discuss
    //$rootScope.STATUS_LEVEL = {'OK':0,'WARNING':1,'ERROR':2};

});
