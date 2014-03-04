angular.module('toolkit-gui').controller('ParticipantInviteCtrl',[
	'$scope',
	'$modalInstance',
	'participants',
	'currentUser',
	'matter',
	'participantService',
	function($scope, $modalInstance, participants, currentUser, matter, participantService){
		$scope.participants = participants;
		$scope.currentUser = currentUser;
		$scope.matter = matter;

		$scope.data = {
			'invitee': { 'email': '', 'message': '' }
		};

		$scope.ok = function () {
			$modalInstance.close( $scope.participants );
		};

		$scope.invite = function () {
			participantService.invite( matter.selected.slug, $scope.data.invitee ).then(
				function success() {
					//
				},
				function error() {
					//
				}
			);
		};

		$scope.cancel = function () {
			$modalInstance.dismiss('cancel');
		};

		$scope.compareUrls = function( urla, urlb ) {
			console.log(urla, urlb, urla.indexOf(urlb)>=0||urlb.indexOf(urla)>=0);
			return urla.indexOf(urlb)>=0||urlb.indexOf(urla)>=0;
		};
	}
]);

// $modalInstance, items