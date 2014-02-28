angular.module('toolkit-gui').controller('ParticipantInviteCtrl',[
	'$scope',
	'$modalInstance',
	'participants',
	'participantService',
	function($scope, $modalInstance, participants){
		$scope.participants = participants;

		$scope.ok = function () {
			$modalInstance.close( $scope.participants );
		};

		$scope.cancel = function () {
			$modalInstance.dismiss('cancel');
		};
	}
]);

// $modalInstance, items