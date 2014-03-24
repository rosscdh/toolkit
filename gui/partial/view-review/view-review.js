angular.module('toolkit-gui')
/**
 * @class ViewReviewCtrl
 * @classdesc 		                      Responsible for viewing a specfic document
 * @param  {Object} $scope                Contains the scope of this controller
 * @param  {Function} $modalInstance      Provides access to close and cancel methods
 * @param  {Object} data                  Details about the review to display
 * @param  {Function} anon                Controller function
 */
.controller('ViewReviewCtrl',[
	'$scope',
	'$modalInstance',
	'toaster',
	'matterItemService',
	'matter',
	'checklistItem',
	'revision',
	'review',
	'$log',
	function($scope, $modalInstance, toaster, matterItemService, matter, checklistItem, revision, review, $log){

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
		 * In scope variable containing details about the specific revision
		 * @memberof ViewReviewCtrl
		 * @type {Object}
		 * @private
		 */
		$scope.review = review;


        $scope.initUserWithAccess = function(){
            var reviews = $scope.revision.reviewers;
            var participants = matter.participants;
            var usersWithAccess = [];
            var reviewers = [];

            if ($scope.item.latest_revision.slug === $scope.revision.slug){
                jQuery.each( reviews, function( index, r ){
                   reviewers.push(r.reviewer);
                });

                jQuery.each( participants, function( index, p ){
                    var results = jQuery.grep( reviewers, function( r ){ return r.username===p.username; });
                    if(results.length===0){
                        usersWithAccess.push(p);
                    }
                });

                $scope.usersWithAccess = jQuery.merge(usersWithAccess, reviewers);
            } else {
                jQuery.each( participants, function( index, p ){
                    if(p.user_class === 'lawyer'){
                        usersWithAccess.push(p);
                    }
                });
                $scope.usersWithAccess = usersWithAccess;
            }
        };

        $scope.initUserWithAccess();

	}
]);