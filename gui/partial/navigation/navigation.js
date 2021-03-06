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
	'$rootScope',
	'$routeParams',
	'smartRoutes',
	'$location',
	'$modal',
	'$log',
	'$timeout',
	'toaster',
	'userService',
	'matterService',
	function( $scope, $rootScope, $routeParams, smartRoutes, $location, $modal, $log, $timeout, toaster, userService, matterService ){
		'use strict';
		var routeParams = smartRoutes.params();
		$scope.selectedStatusFilter = null;

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
			'id': routeParams.id
		};

		//load all other matters from the current user
		matterService.list().then(
			 function success(response){
				$scope.data.matterlist = response;
			 },
			 function error(/*err*/){
				toaster.pop('error', 'Error!', 'Unable to other matters.',5000);
			 }
		);

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
                'windowClass': 'modal-participants',
				'resolve': {
					participants: function () {
						return $scope.matter.selected.participants;
					},
					currentUser: function () {
						return $scope.matter.selected.current_user;
					},
					matter: function () {
						return $scope.matter.selected;
					}
				}
			});

			modalInstance.result.then(
				function ok(/*selectedItem*/) {

				},
				function cancel() {
					//
				}
			);
		};

		/**
		 * Send request to show th intro tutorial
		 * @name				showIntro
		 *
		 * @private
		 * @method				showIntro
		 * @memberof			NavigationCtrl		 */
		$scope.showIntro = function() {
			$rootScope.$broadcast('showIntro');
		};

		/*
		 _____ _ _ _
		|  ___(_) | |_ ___ _ __ ___
		| |_  | | | __/ _ \ '__/ __|
		|  _| | | | ||  __/ |  \__ \
		|_|   |_|_|\__\___|_|  |___/

		 */
		/**
		 * applyStatusFilter  filters for checklist based on status 0-4
		 * @param  {Object} filter Filter to apply to latest_revision
		 */
		$scope.applyStatusFilter = function( filter, statusCode ) {
			// Initialise status filter
			$scope.matter.statusFilter = $scope.matter.statusFilter||{};
			$scope.matter.selectedStatusFilter = statusCode;

			// Clear other filters
			$scope.matter.itemFilter = null;

			if( filter ) {
				for(var key in filter) {
					// Convert { "0": "Draft" } to { "status": 0 }
					$scope.matter.statusFilter[key] = parseInt(filter[key]);
				}
			} else {
				// Clear all filters
				$scope.matter.itemFilter = null;
				$scope.matter.statusFilter = null;
				$scope.matter.selectedStatusFilter = null;
			}
		};

		/**
		 * applyItemFilter  filters for checklist item properties such as is_complete
		 * @param  {Object} filter Filter to apply to base o checklsit item object
		 */
		$scope.applyItemFilter = function( filter, label ) {
			// Initialise item filter
			$scope.matter.itemFilter = $scope.data.itemFilter||{};

			// Clear other filters
			$scope.matter.statusFilter = null;
			$scope.matter.selectedStatusFilter = label;

			if( filter ) {
				for(var key in filter) {
					$scope.matter.itemFilter[key] = filter[key];
				}
			} else {
				// Clear all filters
				$scope.matter.itemFilter = null;
				$scope.matter.statusFilter = null;
				$scope.matter.selectedStatusFilter = null;
			}
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
			var routeParams = smartRoutes.params();
			$scope.data.id = routeParams.id;
		});

		/**
		 * recievePusherNotification - recieves broadcast message
		 * @param  {Event} evt     browser triggered event
		 * @param  {Object} message JSON object from server
		 *
		 * @private
		 * @method				recievePusherNotification
		 * @memberof			NavigationCtrl
		 */
		$scope.$on('notification', function recievePusherNotification( evt, message ){
			var msgText = (message&&message.detail)?message.detail:'Lawpal has a notification for you';
			// Remove notification styles
			$scope.matter.selected.current_user.has_notifications = false;
			// Re-apply style in a few moments so that the css animation runs again
			$timeout(function(){
				$scope.matter.selected.current_user.has_notifications = true;
			},100);

			$scope.notificationPermissionLevel = notify.permissionLevel();

			if( notify ) {
				notify.createNotification("Notification", { 'body':msgText, 'icon': '/static/images/lp-notification.png' });
			}
		});

		if( notify ) {
			$scope.notificationPermissionLevel = notify.permissionLevel();
		}
	}
]);