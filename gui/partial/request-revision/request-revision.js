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

		$scope.participants = angular.copy(participants);
		$scope.currentUser = currentUser;
		$scope.matter = matter;
		$scope.checklistItem = checklistItem;

		$scope.data = {
			'inviteExternal': false,
			'request': {
				'person': null,
				'email': null,
				'message': null
			}
		};

		$scope.ok = function () {
			$modalInstance.close( $scope.participants );
		};

		$scope.cancel = function () {
			$modalInstance.dismiss('cancel');
		};

		$scope.request = function() {
			var email = $scope.data.request.email;
			var message = $scope.data.request.message;
			var person = $scope.data.request.person&&$scope.data.request.person!==''?$scope.data.request.person:null;

			$modalInstance.close( { 'email': email, 'message': message, 'username': person } );
		};

		$scope.invalid = function() {
			return !$scope.data.request.person&&!$scope.data.request.email;
		};
	}
]);