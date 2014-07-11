//
angular.module('toolkit-gui').controller('IntakeCtrl',[
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

		$scope.usdata = userService.data();

		$scope.data = {
			'intakes': [],
			'selectedIntake': null
		};

		userService.current().then(
			function success( profile ) {
				console.log(profile);
			}
		);

		intakeService.list().then(
			function success( intakeList ) {
				$scope.data.intakeList = intakeList;
			}
		);

		// STUFF
		// 
		$scope.selectForm = function( form ) {
			intakeService.setCurrent( form );
		};
	}
]);