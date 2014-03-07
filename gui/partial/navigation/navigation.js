angular.module('toolkit-gui').controller('NavigationCtrl',[
	'$scope',
	'$routeParams',
	'$location',
	'$modal',
	'userService',
	'matterService',
	function( $scope, $routeParams, $location, $modal, userService, matterService ){
		$scope.users = userService.data();
		$scope.matter = matterService.data();

		$scope.data = {
			'id': $routeParams.id,
		};

		$scope.isActive = function( path ) {
			return $location.path().indexOf(path)>=0;
		};

		$scope.invite = function() {
			var modalInstance = $modal.open({
				'templateUrl': '/static/ng/partial/participant-invite/participant-invite.html',
				'controller': 'ParticipantInviteCtrl',
				'resolve': {
					participants: function () {
						return $scope.matter.selected.participants;
					},
					currentUser: function () {
						return $scope.matter.selected.current_user;
					},
					matter: function () {
						return $scope.matter;
					}
				}
			});

			modalInstance.result.then(
				function ok(selectedItem) {
					
				},
				function cancel() {
					//
				}
			);
		};

		$scope.$on('$routeChangeSuccess', function() {
			$scope.data.id = $routeParams.id;
		});
	}
]);