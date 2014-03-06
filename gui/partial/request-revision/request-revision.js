angular.module('toolkit-gui').controller('RequestrevisionCtrl',[
	'$scope',
	'$modalInstance',
	'participants',
	'currentUser',
	'matter',
	'checklistItem',
	'participantService',
	'toaster',
	function($scope, $modalInstance, participants, currentUser, matter, checklistItem, participantService, toaster){

		$scope.participants = participants;
		$scope.currentUser = currentUser;
		$scope.matter = matter;

		$scope.ok = function () {
			$modalInstance.close( $scope.participants );
		};

		$scope.cancel = function () {
			$modalInstance.dismiss('cancel');
		};

	}
]);