angular.module('toolkit-gui').controller('ViewDocumentCtrl',[
	'$scope',
	'$modalInstance',
	'data',
	function($scope, $modalInstance, data ){

		$scope.ok = function () {
			$modalInstance.close();
		};

		$scope.cancel = function () {
			$modalInstance.dismiss('cancel');
		};
	}
]);