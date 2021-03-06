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
	'baseService',
	'matter',
	'checklistItem',
	'revision',
	'signer',
	'$log',
	function($scope, $modalInstance, toaster, baseService, matter, checklistItem, revision, signer, $log){

		/**
		 * Close modal window
		 *
		 * @name				ok
		 * 
		 * @private
		 * @method				ok
		 * @memberof			ViewReviewCtrl
		 */
		$scope.ok = function () {
            baseService.loadObjectByUrl(revision.signing.url).then(
                function success(obj) {
                    $modalInstance.close(obj);
                },
                function error(/*err*/) {
                    if( !toaster.toast || !toaster.toast.body || toaster.toast.body!== 'Unable to reload the signing request.') {
                        toaster.pop('error', 'Error!', 'Unable to reload the signing request.', 5000);
                    }
                }
            );
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

        $scope.signer = signer;

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
                if ($scope.signer) {
                    return $scope.signer.sign_url;
                } else {
                    return $scope.revision.signing.sign_url;
                }
            } else {
                return $scope.revision.signing.claim_url;
            }
        };
	}
]);