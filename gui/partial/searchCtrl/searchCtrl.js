angular.module('toolkit-gui').controller('SearchCtrl',[
	'$scope',
	'searchService',
	'$rootScope',
	'$timeout',
	'$state',
    '$log',
	function($scope, searchService, $rootScope, $timeout, $state, $log){
		'use strict';
		$scope.data = {
			'searchResults': searchService.data(),
			'term': '',
			'display': false
		};

		$scope.startSearch = function( keyCode ) {
			if( keyCode!==13 ) {
				searchService.filter( $scope.data.term );
			} else if( $scope.data.searchResults.results.length>0 ) {
				$scope.selectItem( $scope.data.searchResults.results[0] );
			}
			$scope.data.display = true;
		};

		$scope.selectItem = function( item ) {
			$rootScope.$broadcast('itemSelected', item);
			$scope.hide();

			$state.transitionTo('checklist.item', { 'itemSlug': item.slug });
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

		$scope.keyPress = function( $event ) {
			$log.debug( $event );
		};
	}
]);