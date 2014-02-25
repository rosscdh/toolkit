angular.module('toolkit-gui').controller('ChecklistCtrl', [ '$scope', '$routeParams', 'matterService', function($scope, $routeParams, matterService){
	$scope.data = {
		'id': $routeParams.id,
		'items': [],
		'categories': {},
		'users': [
			{ 'name': 'Sam Jackson', 'img': 'https://fbcdn-profile-a.akamaihd.net/hprofile-ak-ash3/t1/c0.0.100.100/p100x100/1014416_10100118438650161_136799916_a.jpg' },
			{ 'name': 'Bob Jackson', 'img': 'https://fbcdn-profile-a.akamaihd.net/hprofile-ak-ash2/t1/c12.12.155.155/314032_10150303812474864_594285312_a.jpg' },
			{ 'name': 'Hugh Jackson', 'img': 'https://fbcdn-profile-a.akamaihd.net/hprofile-ak-frc3/t1/c42.26.328.328/s320x320/229934_10150955684263644_890325486_n.jpg' }
		]
	};

	$scope.matter = matterService.data();

	if(!$scope.matter.items || $scope.matter.items.length===0) {
		matterService.list( $scope.data.id );
	}
}]);