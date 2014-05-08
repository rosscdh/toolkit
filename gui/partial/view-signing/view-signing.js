angular.module('toolkit-gui')
/**
 * @class ViewSigningCtrl
 * @classdesc 		                      Responsible for viewing a specfic document
 * @param  {Object} $scope                Contains the scope of this controller
 * @param  {Function} $modalInstance      Provides access to close and cancel methods
 * @param  {Object} data                  Details about the review to display
 * @param  {Function} anon                Controller function
 */
.controller('ViewSigningCtrl',[
	'$scope',
	'$modalInstance',
	'toaster',
	'matterItemService',
	'matter',
	'checklistItem',
	'revision',
	'$log',
	function($scope, $modalInstance, toaster, matterItemService, matter, checklistItem, revision, $log){

		/**
		 * WIP
		 *
		 * @name				ok
		 * 
		 * @private
		 * @method				ok
		 * @memberof			ViewReviewCtrl
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
		 * @memberof			ViewReviewCtrl
		 */
		$scope.cancel = function () {
			$modalInstance.dismiss('cancel');
		};

        /**
		 * In scope variable containing details about the matter. This is passed through from the originating controller.
		 * @memberof ViewReviewCtrl
		 * @type {Object}
		 * @private
		 */
		$scope.matter = matter;

		/**
		 * In scope variable containing details about the specific checklist item, with which to make the request
		 * @memberof ViewReviewCtrl
		 * @type {Object}
		 * @private
		 */
		$scope.item = checklistItem;


        /**
		 * In scope variable containing details about the specific revision
		 * @memberof ViewDocumentCtrl
		 * @type {Object}
		 * @private
		 */
		$scope.revision = revision;

         /**
         * Updates the signing process
         *
         * @memberof ViewReviewCtrl
		 * @type method
		 * @private
         */
        $scope.saveSigning = function(){

        };

        $scope.getSigningUrl = function(){
            if ($scope.revision.signing.is_claimed === true){
                $log.debug('signing is claimed');
                return $scope.revision.signing.sign_url;
            } else {
                return $scope.revision.signing.claim_url;
            }
        };
	}
]);