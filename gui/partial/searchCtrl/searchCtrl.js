angular.module('toolkit-gui').controller('SearchCtrl',[
	'$scope',
	'searchService',
	'smartRoutes',
	'$rootScope',
	'$timeout',
	'$state',
    '$log',
	function($scope, searchService, smartRoutes, $rootScope, $timeout, $state, $log){
		'use strict';
	
		var routeParams = smartRoutes.params();

		$scope.data = {
			'searchResults': [],
			'matterSlug': routeParams.matterSlug,
			'term': '',
			'display': false
		};

		$scope.startSearch = function( keyCode ) {

			if( keyCode !== 13 ) {
				// Search
				searchService.filter( $scope.data.matterSlug, $scope.data.term ).then(
					function success( results ) {
                        $log.debug("Found results: " + results.length);
						$scope.data.searchResults = results;
						$scope.data.display = true;
					},
					function error( data ) {
						$scope.data.searchResults = [];
						$scope.data.display = false;
					}
				);

			} else if( $scope.data.searchResults.length > 0 ) {
				// Select item
				$scope.selectItem( $scope.data.searchResults[0] );
			}
		};

		$scope.selectItem = function( item ) {
			$rootScope.$broadcast('itemSelected', item);
			$scope.hide();

			$state.transitionTo('checklist.item', { 'itemSlug': item.slug });
		};

		$scope.hide = function() {
			$timeout( function(){
				$scope.data.display = false;
				$scope.data.searchResults = [];
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