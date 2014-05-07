angular.module('toolkit-gui')
/**
 * @class RequestrevisionCtrl
 * @classdesc 		                      Responsible for managing and requesting the API to request a new revision
 * @param  {Object} $scope                Contains the scope of this controller
 * @param  {Function} $modalInstance      Provides access to close and cancel methods
 * @param  {Object} currentUser           The current user
 * @param  {Object} matter                The matter for which participants will be invited
 * @param  {Function} toaster             Provides a handle to show/hide UI toasters
 */
.controller('AuthenticationRequiredCtrl',[
	'$scope',
	'$modalInstance',
	'currentUser',
	'matter',
	/*'toaster',*/
	function($scope, $modalInstance, currentUser, matter/*, toaster*/){
		'use strict';

		/**
		 * In scope variable containing details about the current user. This is passed through from the originating controller.
		 * @memberof RequestrevisionCtrl
		 * @type {Object}
		 * @private
		 */
		$scope.currentUser = currentUser;
		/**
		 * In scope variable containing details about the matter. This is passed through from the originating controller.
		 * @memberof RequestrevisionCtrl
		 * @type {Object}
		 * @private
		 */
		$scope.matter = matter;


		/**
		 * Scope based data for this controller
		 * @memberof			RequestrevisionCtrl
		 * @private
		 * @type {Object}
		 */
		$scope.data = {
		};

		/**
		 * Close dialog on afirmative user initiated event (.e.g. click's OK button).
		 * Returns updated participants array.
		 *
		 * @name				ok
		 * 
		 * @private
		 * @method				ok
		 * @memberof			RequestrevisionCtrl
		 */
		$scope.ok = function () {
			$modalInstance.close();
		};
	}
]);