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
	'customstatusdict',
	'defaultstatusdict',
	'matterService',
	'toaster',
	'$log',
	function($scope, $modalInstance, currentUser, matter, customstatusdict, defaultstatusdict, matterService, toaster, $log){
		'use strict';
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
        $scope.customstatusdict = customstatusdict;
        $scope.statuslist = [];
        jQuery.each( $scope.customstatusdict, function( key, value ) {
          $scope.statuslist.push({'key':key, 'value': value});
        });


        $scope.defaultstatusdict = defaultstatusdict;

        /**
		 * Reset status to default.
		 * @memberof EditRevisionStatusCtrl
		 * @type {Object}
		 * @private
		 */
        $scope.resetDefault = function (key) {
            if (!key){
                $scope.statuslist = [];
                jQuery.each( $scope.defaultstatusdict, function( key, value ) {
                        $scope.statuslist.push({'key':key, 'value': value});
                });
            } else {
                var results = jQuery.grep( $scope.statuslist, function( status ){ return parseInt(status.key)===parseInt(key); } );
                $log.debug(results);
                if( results.length===1 ) {
                    results[0].value = $scope.defaultstatusdict[key];
                }
            }
        };

        /**
		 * Add a new status.
		 * @memberof EditRevisionStatusCtrl
		 * @type {Object}
		 * @private
		 */
        $scope.addStatus = function() {
            var statuslabel = '';
            var newkey;

            //find first free statuscode
            for (var i=0;i<9;i++){
                var results = jQuery.grep( $scope.statuslist, function( status ){ return parseInt(status.key)===i; } );

                if( results.length===0 ) {
				    newkey=i;
                    break;
			    }
            }

            if ($scope.defaultstatusdict[newkey]) {
                statuslabel = $scope.defaultstatusdict[newkey];
            }

            $scope.statuslist.push({'key':newkey, 'value': statuslabel});
        };

         /**
		 * Deletes a status.
		 * @memberof EditRevisionStatusCtrl
		 * @type {Object}
		 * @private
		 */
        $scope.removeStatus = function(key, index) {
            /*var qtyStatus = $scope.statuslist.length;*/
            var statusToRemove = parseInt(key);

            var inUse = false;
            jQuery.each( $scope.matter.items, function( index, item ) {
                if (item.latest_revision && parseInt(item.latest_revision.status) === statusToRemove) {
                    inUse = true;
                    return;
                }
            });

            if (inUse === true) {
                toaster.pop('warning', 'Warning!', 'This status is in use and cannot be removed.', 5000);
            } else {
                $scope.statuslist.splice(index,1);
            }
        };


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
            $scope.customstatusdict = {};
            jQuery.each( $scope.statuslist, function( index, obj ) {
                $scope.customstatusdict[obj.key] = obj.value;
            });

            var postdata = {'status_labels': $scope.customstatusdict};
            $log.debug(postdata);

            matterService.saveRevisionStatus($scope.matter.slug, postdata).then(
                    function success(){
                        $modalInstance.close(  $scope.customstatusdict );
                    },
                    function error(/*err*/){
                        if( !toaster.toast || !toaster.toast.body || toaster.toast.body !== 'Unable to save the status.') {
                            toaster.pop('error', 'Error!', 'Unable to save the status.',5000);
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