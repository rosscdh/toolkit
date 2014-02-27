angular.module('toolkit-gui').controller('HomeCtrl', [
	'$scope',
	'matterService',
	function( $scope, matterService ){

		$scope.data = {
			'matters': matterService.data()
		};

		$scope.selectMatter = function( matter ) {
			matterService.selectMatter( matter );
		};

		matterService.list().then(
			function success( result ) {
				console.log( result );
			},
			function error(err) {
				console.error(err);
			}
		);
	}
]);