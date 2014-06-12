/**
 * @class activity
 * @classdesc                             Directive for handling activity events
 *
 * @param  {Object} $scope                Contains the scope of this controller
 * @param  {Object} commentService        An angular service designed to work with the COMMENT end-point
 * @param  {Object} ngModel               The activity event object
 * @param  {Object} matterSlug            The slug of the matter
 * @param  {Object} itemSlug              The slug of the currently selected item
 * @param  {Object} user                  The current user object
 */
angular.module('toolkit-gui').directive('activity', ['$compile', '$log', '$sce', '$filter', 'genericFunctions', function ($compile, $log, $sce, $filter, genericFunctions) {
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

                /**
                 * Delete the given comment object
                 *
                 * @memberof            activity
                 * @private
                 * @type {Object}
                 */
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

                /**
                 * Update the given comment object
                 *
                 * @memberof            activity
                 * @private
                 * @type {Object}
                 */
                $scope.saveComment = function () {
                    $scope.data.comment = genericFunctions.cleanHTML($scope.data.edit_comment);
                    commentService.update($scope.matterSlug, $scope.itemSlug, $scope.ngModel.id, $scope.data.comment).then(
                        function success() {
                        },
                        function error(/*err*/) {
                            toaster.pop('error', 'Error!', 'Unable to update comment.', 5000);
                        }
                    );
                };

				/**
				 * Delete the given comment object
				 *
				 * @memberof            activity
				 * @private
				 * @type {Object}
				 */
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
				 * @memberof            activity
				 * @private
				 * @type {Object}
				 */
				$scope.deleteCommentIsEnabled = function () {
					if ($scope.ngModel.type === "item-comment" && $scope.itemSlug) {
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
				 * Checks if the current user may edit the given comment item
				 *
				 * @memberof            activity
				 * @private
				 * @type {Object}
				 */
				$scope.editCommentIsEnabled = function () {
					if ($scope.ngModel.type === "item-comment" && $scope.itemSlug) {

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
