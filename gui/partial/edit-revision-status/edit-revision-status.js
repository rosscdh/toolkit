angular.module('toolkit-gui')
/**
 * @class EditRevisionStatusCtrl
 * @classdesc 		                      Responsible for managing and requesting the API to request a new revision
 * @param  {Object} $scope                Contains the scope of this controller
 * @param  {Function} $modalInstance      Provides access to close and cancel methods
 * @param  {Object} currentUser           The current user
 * @param  {Object} matter                The matter for which participants will be invited
 * @param  {Object} matterService         Contains methods to make matter requests to the API
 * @param  {Function} toaster             Provides a handle to show/hide UI toasters
 * @param  {Function} log                 Angular logger
 */
.controller('EditRevisionStatusCtrl',[
	'$scope',
	'$modalInstance',
	'currentUser',
	'matter',
	'statusdict',
	'matterService',
	'toaster',
	'$log',
	function($scope, $modalInstance, currentUser, matter, statusdict, matterService, toaster, $log){

		/**
		 * In scope variable containing details about the current user. This is passed through from the originating controller.
		 * @memberof EditRevisionStatusCtrl
		 * @type {Object}
		 * @private
		 */
		$scope.currentUser = currentUser;
		/**
		 * In scope variable containing details about the matter. This is passed through from the originating controller.
		 * @memberof EditRevisionStatusCtrl
		 * @type {Object}
		 * @private
		 */
		$scope.matter = matter;


        /**
		 * In scope variable containing details about each status. This is passed through from the originating controller.
		 * @memberof EditRevisionStatusCtrl
		 * @type {Object}
		 * @private
		 */
        $scope.statusdict = statusdict;
        $scope.statuslist = [];
        jQuery.each( $scope.statusdict, function( key, value ) {
          $scope.statuslist.push({'key':key, 'value': value});
        });

		/**
		 * Close dialog on afirmative user initiated event (.e.g. click's OK button).
		 * Returns nothing
		 *
		 * @name				cancel
		 * 
		 * @private
		 * @method				cancel
		 * @memberof			EditRevisionStatusCtrl
		 */
		$scope.cancel = function () {
			$modalInstance.dismiss('cancel');
		};


		/**
		 * Initiates the process to save the status.
		 *
		 * @name				request
		 * 
		 * @param  {Object} person	User object
		 * @private
		 * @method				request
		 * @memberof			EditRevisionStatusCtrl
		 */
		$scope.request = function() {
            jQuery.each( $scope.statuslist, function( index, obj ) {
                $scope.statusdict[obj.key] = obj.value;
            });
            var postdata = {'status_labels': $scope.statusdict};
            $log.debug(postdata);

            matterService.saveRevisionStatus($scope.matter.slug, postdata).then(
                    function success(){
                        $modalInstance.close(  $scope.statusdict );
                    },
                    function error(err){
                        if( !toaster.toast || !toaster.toast.body || toaster.toast.body!== "Unable to save the status.") {
                            toaster.pop('error', "Error!", "Unable to save the status.");
                        }
                    }
            );

		};

		/**
		 * Determines if the form is valid or not.
		 *
		 * @name				invalid
		 * 
		 * @private
		 * @method				invalid
		 * @memberof			EditRevisionStatusCtrl
		 */
		$scope.invalid = function() {
            return false;
		};
	}
]);