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
	'toaster',
	'matterItemService',
	'matter',
	'checklistItem',
	'revision',
	function($scope, $modalInstance, toaster, matterItemService, matter, checklistItem, revision ){

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

        /**
		 * In scope variable containing details about the matter. This is passed through from the originating controller.
		 * @memberof ViewDocumentCtrl
		 * @type {Object}
		 * @private
		 */
		$scope.matter = matter;

		/**
		 * In scope variable containing details about the specific checklist item, with which to make the request
		 * @memberof ViewDocumentCtrl
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
		 * Get the reviewer url from the matterItemService
		 * @memberof ViewDocumentCtrl
		 * @private
		*/
        if($scope.revision != null && $scope.revision.user_review_url == null) {
            matterItemService.loadRevision($scope.matter.slug, $scope.item.slug, $scope.revision.slug).then(
                function success(revision){
                    $scope.revision.user_review_url = revision.user_review_url;
                },
                function error(err){
                    toaster.pop('error', "Error!", "Unable to load revision details");
                }
            );
        }
	}
]);