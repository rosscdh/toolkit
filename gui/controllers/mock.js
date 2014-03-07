/**
 * Mock controllers for the development of seperate features
 */

// Mock controller/wrapper for invite modal
angular.module('toolkit-gui').controller('mockInviteModalCtrl', [ '$scope', '$modal', function($scope, $modal){
	$scope.data = {
		'participants': [
			{ 'name': 'Bob' },
			{ 'name': 'Zara'}
		]
	};

	$scope.open = function() {
		var modalInstance = $modal.open({
			'templateUrl': 'partial/participant-invite/participant-invite.html',
			'controller': 'ParticipantInviteCtrl',
			'resolve': {
				participants: function () {
					return $scope.data.participants;
				}
			}
		});

		modalInstance.result.then(
			function ok(selectedItem) {
				alert('ok');
			},
			function cancel() {
				//
			}
		);
	};
	
}]);

// Mock controller/wrapper for invite modal
angular.module('toolkit-gui').controller('mockViewDocumentCtrl', [ '$scope', '$modal', function($scope, $modal){
	$scope.data = {};

	$scope.open = function() {
		var modalInstance = $modal.open({
			'templateUrl': 'partial/view-document/view-document.html',
			'controller': 'ViewDocumentCtrl',
			'resolve': {
				data: function () {
					return $scope.data;
				}
			}
		});

		modalInstance.result.then(
			function ok(selectedItem) {
				alert('ok');
			},
			function cancel() {
				//
			}
		);
	};
	
}]);