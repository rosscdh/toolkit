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
            currentUser: '='
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
                $log.debug($scope.currentUser);


                $scope.manageTask = function (task) {
                    var modalInstance = $modal.open({
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

                    modalInstance.result.then(
                        function ok(result) {
                            $log.debug(result);

                            $scope.loadTasks();

                            /*
                             var olditems = jQuery.grep($scope.data.tasks, function(obj){
                             return obj.slug === result.slug;
                             });
                             if (olditems.length === 0) {
                             $scope.data.tasks.push(result);
                             } else {
                             olditems[0] = angular.extend(olditems[0], result);
                             }*/
                        },
                        function cancel() {
                            //
                        }
                    );
                };

                //delete task confirmation modal
                $scope.deleteTask = function (task) {
                    ezConfirm.create('Delete Task', 'Please confirm you would like to delete this task?',
                        function yes() {
                            // Confirmed- delete category
                            taskService.delete($scope.matter.slug, $scope.selectedItem.slug, task.slug).then(
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
                            $log.debug(tasks);
                            $scope.data.tasks = tasks;
                        },
                        function error(/*err*/) {
                            if (!toaster.toast || !toaster.toast.body || toaster.toast.body !== 'Unable to load item tasks.') {
                                toaster.pop('error', 'Error!', 'Unable to load item tasks.', 5000);
                            }
                        }
                    );
                };

                $scope.toggleCompleteTask = function (task) {
                    if ($scope.isCompleteTaskEnabled) {
                        task.is_complete = !task.is_complete;

                        taskService.update($scope.matter.slug, $scope.selectedItem.slug, task.slug, task).then(
                            function success(tasks) {
                                //do nothing
                            },
                            function error(/*err*/) {
                                if (!toaster.toast || !toaster.toast.body || toaster.toast.body !== 'Unable to update task.') {
                                    toaster.pop('error', 'Error!', 'Unable to update task.', 5000);
                                }
                                //revert change
                                task.is_complete = !task.is_complete;
                            }
                        );
                    }
                };

                $scope.isDeleteTaskEnabled = function (task) {
                    if ($scope.currentUser.role === 'owner') {
                        return true;
                    }

                    if ($scope.currentUser.permissions.manage_task) {
                        return true;
                    }

                    if ($scope.currentUser.username === task.created_by.username) {
                        return true;
                    }

                    return false;
                };

                $scope.isCompleteTaskEnabled = function (task) {
                    if ($scope.currentUser.role === 'owner') {
                        return true;
                    }

                    if ($scope.currentUser.permissions.manage_task) {
                        return true;
                    }

                    if ($scope.currentUser.username === task.created_by.username) {
                        return true;
                    }

                    var index = jQuery.inArray($scope.currentUser, task.assigned_to);
                    if (index >= 0) {
                        return true;
                    }

                    return false;
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
