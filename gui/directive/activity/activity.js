
angular.module('toolkit-gui').directive('activity', ['$compile','$log', '$sce', '$filter',function($compile, $log, $sce, $filter) {
  return {
    scope: {
      ngModel: '=',
      matterSlug: '=',
      itemSlug: '=',
      user: '=',
      activityStream: '='
    },
    replace: true,
    controller: ['$scope', '$http', '$log', 'commentService', 'toaster','$timeout',
        function($scope, $http, $log, commentService, toaster, $timeout) {

         $scope.deleteComment = function(){
             //TODO itemSlug shouldnt be necessary
             commentService.delete($scope.matterSlug, $scope.itemSlug, $scope.ngModel.id).then(
				 function success(){
                    $scope.isDeleted = true;
				 },
				 function error(/*err*/){
					toaster.pop('error', 'Error!', 'Unable to delete comment.',5000);
				 }
			);
         };

         $scope.saveComment = function(){
             commentService.update($scope.matterSlug, $scope.itemSlug, $scope.ngModel.id, $scope.comment).then(
				 function success(){
				 },
				 function error(/*err*/){
					toaster.pop('error', 'Error!', 'Unable to update comment.',5000);
				 }
			);
         };

        $scope.startEditingComment = function(){
            //TODO check user permission
            $scope.show_edit_comment=true;
            $scope.edit_comment=$scope.comment;

            $timeout(function (){
			  $scope.$broadcast('focusOn', 'event_edit_comment');
			}, 300);
        };

        /**
		 * Checks if the current user may delete the given comment item
         *
		 * @memberof			ChecklistCtrl
		 * @private
		 * @type {Object}
		 */
        $scope.deleteCommentIsEnabled = function(){
            if ($scope.ngModel.type === "item-comment") {
                $log.debug($scope.user.user_class);
                //if user is lawyer, he might delete all comments
                if($scope.user.user_class==='lawyer'){
                    return true;
                } else {
                    var comments = jQuery.grep( $scope.activityStream, function( item ){ return item.type==="item-comment"; } );
                    var index = jQuery.inArray( $scope.ngModel,comments );
                    $log.debug(index);

                    //if the user is a client, then he might only delete his own comments if there is no newer comment
                    //TODO username not yet provided
                    /*if($scope.ngModel.actor.username === $scope.user.username && index===0) {
                        return true;
                    }*/
                }
            }

            return false;
        };
    }],
    templateUrl: '/static/ng/directive/activity/event.html',

    link: function(scope, element, attrs) {
        var eventhtml = jQuery(scope.ngModel.event);

        if (scope.ngModel.type === "item-comment"){
            scope.head = $sce.trustAsHtml(eventhtml.find(".ng-head").html());
            scope.comment = $sce.trustAsHtml(eventhtml.find(".ng-comment").html());
        }
    }
  };
}]);