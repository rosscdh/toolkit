angular.module('toolkit-gui').controller('NavigationCtrl',[
	'$scope',
	'$routeParams',
	'$location',
	'userService',
	'matterService',
	function( $scope, $routeParams, $location, userService, matterService ){
		$scope.users = userService.data();
		$scope.matter = matterService.data();

		$scope.data = {
			'id': $routeParams.id,
		};

		$scope.isActive = function( path ) {
			return $location.path().indexOf(path)>=0;
		};

		$scope.$on('$routeChangeSuccess', function() {
			$scope.data.id = $routeParams.id;
		});
	}
]);