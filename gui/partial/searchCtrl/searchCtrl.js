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
			'searchPromise': null,
			'searchResults': [],
			'matterSlug': routeParams.matterSlug,
			'term': '',
			'display': false
		};

		$scope.startSearch = function( keyCode ) {

			if( keyCode !== 13 ) {
				// Search

				// kill the promise if another keypress comes in
				if ( $scope.searchPromise !== null ) {
					$timeout.cancel($scope.searchPromise);
				}
				// delay the search pending another term entry on keyup
				$scope.searchPromise = $timeout(function () {

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

				},300);

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