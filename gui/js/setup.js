angular.module('toolkit-gui', ['ui.bootstrap','ui.utils','ngRoute','ngAnimate', 'ngResource']);

angular.module('toolkit-gui').config(function($routeProvider) {

    $routeProvider.
    when('/',{templateUrl: 'partial/home/home.html'}).
	when('/matter/:id/checklist',{'templateUrl': 'partial/checklist/checklist.html', 'controller': 'ChecklistCtrl'}).
	when('/matter/:id/closing',{templateUrl: 'partial/closing/closing.html'}).
	when('/matter/:matterSlug/invite',{templateUrl: 'partial/participant-invite/participant-invite.html'}).
	when('/matter/:matterSlug/attachment/:id',{templateUrl: 'partial/view-document/view-document.html'}).
	/* Add New Routes Above */
    otherwise({redirectTo:'/'});

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
