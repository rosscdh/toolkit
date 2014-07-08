/**
 * Directive for displaying the mentions box and completing the user tags.
 * Communicates through the broadcasts with the mentions container which is appended to the body.
 *
 **/
angular.module('toolkit-gui').directive('tasksList', ['$compile', '$log', '$sce', '$filter', function ($compile, $log, $sce, $filter) {
    return {
        scope: {
            matter: '=',
            selectedItem: '=',
            currUser: '='
        },
        replace: true,
        controller: ['$rootScope',
            '$scope',
            '$http',
            '$log',
            'ezConfirm',
            'toaster',
            '$modal',
            'taskService',
            function ($rootScope, $scope, $http, $log, ezConfirm, toaster, $modal, taskService) {
                $scope.data = {
                    tasks: []
                };

                $log.debug($scope.matter);
                $log.debug($scope.selectedItem);
                $log.debug($scope.currUser);


                $scope.manageTask = function (task) {
                    $modal.open({
                        'templateUrl': '/static/ng/directive/task/manage-task.html',
                        'controller': 'manageTaskCtrl',
                        'resolve': {
                            'participants': function () {
                                return $scope.matter.participants;
                            },
                            'currentUser': function () {
                                return $scope.matter.current_user;
                            },
                            'matter': function () {
                                return $scope.matter;
                            },
                            'checklistItem': function () {
                                return $scope.selectedItem;
                            },
                            'task': function () {
                                return task;
                            }
                        }
                    });
                };

                //delete task confirmation modal
                $scope.deleteTask = function (task) {
                    ezConfirm.create('Delete Task', 'Please confirm you would like to delete this task?',
                        function yes() {
                            // Confirmed- delete category
                            taskService.delete(matterSlug, $scope.selectedItem.slug, task.slug).then(
                                function success() {
                                    var index = jQuery.inArray(task, $scope.data.tasks);
                                    if (index >= 0) {
                                        // Remove item from in RAM array
                                        $scope.data.tasks.splice(index, 1);
                                    }
                                },
                                function error(/*err*/) {
                                    toaster.pop('error', 'Error!', 'Unable to delete task', 5000);
                                }
                            );
                        }
                    );
                };


                $scope.loadTasks = function () {
                    taskService.query($scope.matter.slug, $scope.selectedItem.slug).then(
                        function success(tasks) {
                            $scope.data.tasks = tasks;
                        },
                        function error(/*err*/) {
                            if (!toaster.toast || !toaster.toast.body || toaster.toast.body !== 'Unable to load item tasks.') {
                                toaster.pop('error', 'Error!', 'Unable to load item tasks.', 5000);
                            }
                        }
                    );
                };

                $scope.$watch('selectedItem', function (newValue, oldValue) {
                    $log.debug('Value changed');

                    if ($scope.selectedItem) {
                        $scope.loadTasks();
                    }
                });

            }],
        templateUrl: '/static/ng/directive/task/list-task.html',
        link: function (scope, element, attrs) {

        }
    };
}]);

