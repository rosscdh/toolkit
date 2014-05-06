angular.module('toolkit-gui').controller('HomeCtrl', [
	'$scope',
	'matterService',
    '$log',
	function( $scope, matterService, $log){
		'use strict';
		$scope.data = {
			'matters': matterService.data()
		};

		$scope.selectMatter = function( matter ) {
			matterService.selectMatter( matter );
		};

		matterService.list().then(
			function success( result ) {
				$log.debug( result );
			},
			function error(err) {
				$log.debug(err);
			}
		);
	}
]);