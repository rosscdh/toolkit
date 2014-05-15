angular.module('toolkit-gui').directive('activity', ['$compile', '$log', '$sce', '$filter', function ($compile, $log, $sce, $filter) {
    return {
        scope: {
            ngModel: '=',
            matterSlug: '=',
            itemSlug: '=',
            user: '='
        },
        replace: true,
        controller: ['$scope', '$http', '$log', 'commentService', 'toaster', '$timeout',
            function ($scope, $http, $log, commentService, toaster, $timeout) {

                $scope.data = {
                    'edit_comment': '',
                    'comment': ''
                };

                $scope.deleteComment = function () {
                    //TODO itemSlug shouldnt be necessary
                    commentService.delete($scope.matterSlug, $scope.itemSlug, $scope.ngModel.id).then(
                        function success() {
                            $scope.isDeleted = true;
                        },
                        function error(/*err*/) {
                            toaster.pop('error', 'Error!', 'Unable to delete comment.', 5000);
                        }
                    );
                };

                $scope.saveComment = function () {
                    $scope.data.comment = $scope.data.edit_comment;
                    commentService.update($scope.matterSlug, $scope.itemSlug, $scope.ngModel.id, $scope.data.comment).then(
                        function success() {
                        },
                        function error(/*err*/) {
                            toaster.pop('error', 'Error!', 'Unable to update comment.', 5000);
                        }
                    );
                };

                $scope.startEditingComment = function () {
                    if ($scope.editCommentIsEnabled()) {
                        $scope.show_edit_comment = true;
                        $scope.data.edit_comment = $scope.data.comment;

                        $timeout(function () {
                            $scope.$broadcast('focusOn', 'event_edit_comment');
                        }, 300);
                    }
                };

                /**
                 * Checks if the current user may delete the given comment item
                 *
                 * @memberof            ChecklistCtrl
                 * @private
                 * @type {Object}
                 */
                $scope.deleteCommentIsEnabled = function () {
                    if ($scope.ngModel.type === "item-comment") {
                        $log.debug($scope.user.user_class);
                        //if user is lawyer, he might delete all comments
                        if ($scope.user.user_class === 'lawyer') {
                            return true;
                        } else {
                            var timediff = moment().diff(moment($scope.ngModel.timestamp),'minutes');
                            //if the user is a client, then he might only delete his own comments if there are not older than 60minutes
                            if ($scope.ngModel.username === $scope.user.username && timediff<=60) {
                                return true;
                            }
                        }
                    }

                    return false;
                };

                /**
                 * Checks if the current user may delete the given comment item
                 *
                 * @memberof            ChecklistCtrl
                 * @private
                 * @type {Object}
                 */
                $scope.editCommentIsEnabled = function () {
                    if ($scope.ngModel.type === "item-comment") {
                        $log.debug($scope.user.user_class);

                        var timediff = moment().diff(moment($scope.ngModel.timestamp),'minutes');

                        //you can only delete your own comments if there are not older than 60minutes
                        if ($scope.ngModel.username === $scope.user.username && timediff<=60) {
                            return true;
                        }
                    }

                    return false;
                };
            }],
        templateUrl: '/static/ng/directive/activity/event.html',

        link: function (scope, element, attrs) {
            var eventhtml = jQuery(scope.ngModel.event);

            if (scope.ngModel.type === "item-comment") {
                scope.head = $sce.trustAsHtml(eventhtml.find(".ng-head").html());
                scope.data.comment = $sce.trustAsHtml(eventhtml.find(".ng-comment").html()).toString();
            }
        }
    };
}]);