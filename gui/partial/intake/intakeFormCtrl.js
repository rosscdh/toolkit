//
angular.module('toolkit-gui').controller('IntakeFormCtrl',[
	'$scope',
	'$rootScope',
	'$routeParams',
	'$state',
	'smartRoutes',
	'userService',
	'intakeService',
	'toaster',
	function($scope, $rootScope, $routeParams, $state, smartRoutes, userService, intakeService, toaster){
		'use strict';

		var routeParams = smartRoutes.params();
		$scope.intakeData = intakeService.data();

		$scope.slug = routeParams.slug;
	}
]);