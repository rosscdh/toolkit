angular.module('toolkit-gui').controller('ParticipantInviteCtrl',[
	'$scope',
	'$modalInstance',
	'participants',
	'currentUser',
	'matter',
	'participantService',
	'toaster',
	function($scope, $modalInstance, participants, currentUser, matter, participantService, toaster){
		$scope.participants = participants;
		$scope.currentUser = currentUser;
		$scope.matter = matter;

		$scope.data = {
			'invitee': { 'email': '', 'message': '' }
		};

		$scope.invite = function () {
			participantService.invite( matter.selected.slug, $scope.data.invitee ).then(
				function success() {
					//
				},
				function error() {
					toaster.pop('error', "Error!", "Unable to invite this person to particpate, please try again in a few moments");
				}
			);
		};

		$scope.revoke = function ( person ) {
			participantService.invite( matter.selected.slug, person ).then(
				function success() {
					//
				},
				function error() {
					toaster.pop('error', "Error!", "Unable to invite this person to particpate, please try again in a few moments");
				}
			);
		};

		$scope.ok = function () {
			$modalInstance.close( $scope.participants );
		};

		$scope.cancel = function () {
			$modalInstance.dismiss('cancel');
		};

		/*
		$scope.compareUrls = function( urla, urlb ) {
			console.log(urla, urlb, urla.indexOf(urlb)>=0||urlb.indexOf(urla)>=0);
			return urla.indexOf(urlb)>=0||urlb.indexOf(urla)>=0;
		};
		*/
	}
]);

// $modalInstance, items