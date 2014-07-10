angular.module('toolkit-gui')
    .controller('manageTaskCtrl', [
        '$scope',
        '$modalInstance',
        'toaster',
        'participants',
        'currentUser',
        'matter',
        'checklistItem',
        'task',
        'taskService',
        '$log',
        function ($scope, $modalInstance, toaster, participants, currentUser, matter, checklistItem, task, taskService, $log) {
            'use strict';
            /**
             * In scope variable containing a list of participants within this matter. This is passed through from the originating controller.
             * This object is cloned, and therefore changes to this object will not be refected in thr originating object.
             *
             * @memberof manageTaskCtrl
             * @type {Array}
             * @private
             */
            $scope.participants = angular.copy(participants);
            /**
             * In scope variable containing details about the current user. This is passed through from the originating controller.
             * @memberof manageTaskCtrl
             * @type {Object}
             * @private
             */
            $scope.currentUser = currentUser;
            /**
             * In scope variable containing details about the matter. This is passed through from the originating controller.
             * @memberof manageTaskCtrl
             * @type {Object}
             * @private
             */
            $scope.matter = matter;


            /**
             * In scope variable containing details about the specific checklist item, with which to make the request
             * @memberof manageTaskCtrl
             * @type {Object}
             * @private
             */
            $scope.checklistItem = checklistItem;

            /**
             * In scope variable containing details about the specific checklist item, with which to make the request
             * @memberof manageTaskCtrl
             * @type {Object}
             * @private
             */
            if (task) {
                $scope.task = angular.copy(task);
                $log.debug(task);
            } else {
                $scope.task = {
                    'name': '',
                    'description': '',
                    'created_by': {},
                    'assigned_to': []
                };
            }

            $scope.data = {
                'selectedUsers': {}
            };

            $scope.dateOptions = {
                formatYear: 'yy',
                startingDay: 1,
                'datepickerIsOpened': false,
                'minDueDate': new Date()
            };

            /**
             * Close dialog on afirmative user initiated event (.e.g. click's OK button).
             * Returns updated participants array.
             *
             * @name                ok
             *
             * @private
             * @method                ok
             * @memberof            RequestreviewCtrl
             */
            $scope.submitTask = function (taskForm) {
                $scope.data.formSubmitted = true;
                $scope.task.assigned_to = [];

                if (taskForm.$valid) {
                    jQuery.each($scope.data.selectedUsers, function (i, obj) {
                            $scope.task.assigned_to.push(obj.username);
                    });

                    if (!$scope.task.slug) {
                        taskService.create($scope.matter.slug, $scope.checklistItem.slug, $scope.task).then(
                            function success(task) {
                                $modalInstance.close($scope.task);
                            },
                            function error(/*err*/) {
                                if (!toaster.toast || !toaster.toast.body || toaster.toast.body !== 'Unable to create task.') {
                                    toaster.pop('error', 'Error!', 'Unable to create task.', 5000);
                                }
                            }
                        );
                    } else {
                        taskService.update($scope.matter.slug, $scope.checklistItem.slug, $scope.task.slug, $scope.task).then(
                            function success(task) {
                                $modalInstance.close($scope.task);
                            },
                            function error(/*err*/) {
                                if (!toaster.toast || !toaster.toast.body || toaster.toast.body !== 'Unable to update task.') {
                                    toaster.pop('error', 'Error!', 'Unable to update task.', 5000);
                                }
                            }
                        );
                    }
                }
            };

            $scope.isEditTaskEnabled = function () {
                if ($scope.currentUser.role === 'owner') {
                    return true;
                }

                if ($scope.currentUser.permissions.manage_task) {
                    return true;
                }

                if ($scope.currentUser.username === $scope.task.created_by.username) {
                    return true;
                }

                return false;
            };

            $scope.toggleUser = function (user) {
                if (!(user.username in $scope.data.selectedUsers)) {
                    $scope.data.selectedUsers[user.username] = user;
                } else {
                    delete $scope.data.selectedUsers[user.username];
                }
            };

            $scope.taskIsEditable = function () {
                return $scope.currentUser.role === 'owner' || $scope.currentUser.username === $scope.task.created_by.username;
            };

            $scope.init = function () {
                if ($scope.task.assigned_to && $scope.task.assigned_to.length > 0) {
                    jQuery.each($scope.task.assigned_to, function (index, obj) {
                        $scope.toggleUser(obj);
                    });
                }
            };

            $scope.toggleDatepicker = function($event) {
                $event.preventDefault();
                $event.stopPropagation();
                $scope.dateOptions.datepickerIsOpened = !$scope.dateOptions.datepickerIsOpened;
                $log.debug('asdeded');
            };

            $scope.init();

            /**
             * Closes dialog
             * @memberOf Ma
             * @method cancel
             */
            $scope.cancel = function () {
                $modalInstance.dismiss();
            };
        }


    ]);