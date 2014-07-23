/**
 * Directive for handling attachments
 *
 **/
angular.module('toolkit-gui').directive('attachmentsList', ['$compile', '$log', '$sce', '$filter', function ($compile, $log, $sce, $filter) {
    return {
        scope: {
            matter: '=',
            selectedItem: '=',
            currentUser: '='
        },
        replace: true,
        controller: [
            '$rootScope',
            '$scope',
            '$http',
            '$log',
            'ezConfirm',
            'toaster',
            '$modal',
            'userService',
            'attachmentService',
            function ($rootScope, $scope, $http, $log, ezConfirm, toaster, $modal, userService, attachmentService) {
                $scope.data = {
                    'usdata': userService.data(),
                    'attachments': [],
                };


                $scope.manageAttachment = function () {
                    var modalInstance = $modal.open({
                        'templateUrl': '/static/ng/directive/attachment/manage-attachment.html',
                        'controller': 'manageAttachmentCtrl',
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
                            }
                        }
                    });

                    modalInstance.result.then(
                        function ok(result) {
                            $log.debug(result);

                            $scope.loadAttachments();
                        },
                        function cancel() {
                            //
                        }
                    );
                };

                //delete attachment confirmation modal
                $scope.deleteAttachment = function (attachment) {
                    ezConfirm.create('Delete attachment', 'Please confirm you would like to delete this attachment?',
                        function yes() {
                            // Confirmed- delete category
                            attachmentService.delete(attachment.slug).then(
                                function success() {
                                    var index = jQuery.inArray(attachment, $scope.data.attachments);
                                    if (index >= 0) {
                                        // Remove item from in RAM array
                                        $scope.data.attachments.splice(index, 1);
                                    }
                                },
                                function error(/*err*/) {
                                    toaster.pop('error', 'Error!', 'Unable to delete attachment', 5000);
                                }
                            );
                        }
                    );
                };

                $scope.loadAttachments = function () {
                    attachmentService.query($scope.matter.slug, $scope.selectedItem.slug).then(
                        function success(attachments) {
                            $log.debug(attachments);
                            $scope.data.attachments = attachments;
                        },
                        function error(/*err*/) {
                            if (!toaster.toast || !toaster.toast.body || toaster.toast.body !== 'Unable to load item attachments.') {
                                toaster.pop('error', 'Error!', 'Unable to load item attachments.', 5000);
                            }
                        }
                    );
                };

                $scope.isDeleteAttachmentEnabled = function (attachment) {
                    if ($scope.selectedItem.is_complete) {
                        return false;
                    }

                    if ($scope.currentUser.role === 'owner') {
                        return true;
                    }

                    if ($scope.currentUser.permissions.manage_attachment) {
                        return true;
                    }

                    if ($scope.currentUser.username === attachment.uploaded_by.username) {
                        return true;
                    }

                    return false;
                };


                $scope.$watch('selectedItem', function (newValue, oldValue) {
                    $log.debug('Value changed');

                    if ($scope.selectedItem) {
                        $scope.loadAttachments();
                    }
                });

            }],
        templateUrl: '/static/ng/directive/attachment/list-attachment.html',
        link: function (scope, element, attrs) {

        }
    };
}]);
 
