angular.module('toolkit-gui').controller('SearchCtrl',[
	'$scope',
	'searchService',
	'$rootScope',
	'$timeout',
	function($scope, searchService, $rootScope, $timeout){
		$scope.data = {
			'searchResults': searchService.data(),
			'term': '',
			'display': false
		};

		$scope.startSearch = function() {
			searchService.filter( $scope.data.term );
			$scope.data.display = true;
		};

		$scope.selectItem = function( item ) {
			$rootScope.$broadcast('itemSelected', item);
			$scope.hide();
		};

		$scope.hide = function() {
			$timeout( function(){
				$scope.data.display = false;
				$scope.data.searchResults.results = [];
				$scope.data.term = '';
			},300);
		};

		$scope.show = function() {
			$scope.data.display = true;
		};
	}
]);