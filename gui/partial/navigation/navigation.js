angular.module('toolkit-gui')
/**
 * @class NavigationCtrl
 * @classdesc 		                      Displaying/hiding menu items. This controller also shows the participant dialog
 * @param  {Object} $scope                Contains the scope of this controller
 * @param  {Obect} $routeParams           Provides access to angular rounte params
 * @param  {Function} $location           Provides methods to navigate to specific views/urls
 * @param  {Object} userService           Provides methods/data for accessing user related data
 * @param  {Object} matterService         Provides methods/data for accessing matter related data
 * @param  {Function} anon                Controller function
 */
.controller('NavigationCtrl',[
	'$scope',
	'$routeParams',
	'$location',
	'$modal',
	'userService',
	'matterService',
	function( $scope, $routeParams, $location, $modal, userService, matterService ){
		/**
		 * In scope variable containing containing a list of participants
		 * @memberof NavigationCtrl
		 * @type {Object}
		 * @private
		 */
		$scope.users = userService.data();

		/**
		 * In scope variable containing containing the currently selected matter
		 * @memberof NavigationCtrl
		 * @type {Object}
		 * @private
		 */
		$scope.matter = matterService.data();

		/**
		 * Scope based data for this controller
		 * @memberof			NavigationCtrl
		 * @private
		 * @type {Object}
		 */
		$scope.data = {
			'id': $routeParams.id,
		};

		/**
		 * This method is used by navigation items to determine ifthey should be highlighted (i.e. .active)
		 * @param  {String}  path Path passed in by the navigation item
		 * @return {Boolean}      True if the current location contains the path of the navigation item
		 * @name				isActive
		 * 
		 * @private
		 * @method				isActive
		 * @memberof			NavigationCtrl
		 */
		$scope.isActive = function( path ) {
			return $location.path().indexOf(path)>=0;
		};

		/**
		 * Show invite matter participant modal
		 * @name				invite
		 * 
		 * @private
		 * @method				invite
		 * @memberof			NavigationCtrl
		 */
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

		/**
		 * Update in scope variable that tracks the current matter ID
		 * @name				updateNavigationID
		 * 
		 * @private
		 * @method				updateNavigationID
		 * @memberof			NavigationCtrl
		 */
		$scope.$on('$routeChangeSuccess', function updateNavigationID() {
			$scope.data.id = $routeParams.id;
		});
	}
]);