angular.module('toolkit-gui')
/**
 * @class ViewDocumentCtrl
 * @classdesc 		                      Responsible for viewing a specfic document
 * @param  {Object} $scope                Contains the scope of this controller
 * @param  {Function} $modalInstance      Provides access to close and cancel methods
 * @param  {Object} data                  Details about the document to display
 * @param  {Function} anon                Controller function
 */
.controller('ViewDocumentCtrl',[
	'$scope',
	'$modalInstance',
	'data',
	function($scope, $modalInstance, data ){

		/**
		 * WIP
		 *
		 * @name				ok
		 * 
		 * @private
		 * @method				ok
		 * @memberof			ViewDocumentCtrl
		 */
		$scope.ok = function () {
			$modalInstance.close();
		};

		/**
		 * WIP
		 *
		 * @name				cancel
		 * 
		 * @private
		 * @method				cancel
		 * @memberof			ViewDocumentCtrl
		 */
		$scope.cancel = function () {
			$modalInstance.dismiss('cancel');
		};
	}
]);