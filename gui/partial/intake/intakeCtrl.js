//
angular.module('toolkit-gui').controller('IntakeCtrl',[
	'$scope',
	'$rootScope',
	'$routeParams',
	'$state',
	'smartRoutes',
	'matterService',
	'toaster',
	function($scope, $rootScope, $routeParams, $state, smartRoutes, matterService, toaster){
		'use strict';

		var routeParams = smartRoutes.params();

		$scope.matter = matterService.data();

		$scope.data = {
			'slug': routeParams.matterSlug,
			'matter': null
		};

		// LOAD MATTER if not already loaded
		function loadMatter() {
			matterService.get( $scope.data.slug ).then(
				function success( singleMatter ){
					matterService.selectMatter(singleMatter); //set matter in the services
				}
			);
		}

		if( !$scope.matter.selected && $scope.data.slug && $scope.data.slug!=='') {
			loadMatter();
		}

		// STUFF
	}
]);