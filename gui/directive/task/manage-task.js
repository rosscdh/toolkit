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
        function ($scope, $modalInstance, toaster, participants, currentUser, matter, checklistItem, task, taskService) {
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
                $scope.task = task;
            } else {
                $scope.task = {
                    'name': '',
                    'description': ''
                };
            }

            $scope.data = {
                'selectedUsers': {}
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
            $scope.submitTask = function () {
                $scope.task.assigned_to = [];

                jQuery.each($scope.data.selectedUsers, function(i, obj){
                    $scope.task.assigned_to.push(obj.username);
                });

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
            };

            $scope.toggleUser = function (user) {
                if (!(user.username in $scope.data.selectedUsers)) {
                    $scope.data.selectedUsers[user.username] = user;
                } else {
                    delete $scope.data.selectedUsers[user.username];
                }
            };

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