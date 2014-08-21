angular.module('toolkit-gui')
    .controller('manageAttachmentCtrl', [
        '$scope',
        '$modalInstance',
        'toaster',
        'participants',
        'currentUser',
        'matter',
        'checklistItem',
        'attachmentService',
        '$log',
        function ($scope, $modalInstance, toaster, participants, currentUser, matter, checklistItem, attachmentService, $log) {
            'use strict';
            /**
             * In scope variable containing a list of participants within this matter. This is passed through from the originating controller.
             * This object is cloned, and therefore changes to this object will not be refected in thr originating object.
             *
             * @memberof manageAttachmentCtrl
             * @type {Array}
             * @private
             */
            $scope.participants = angular.copy(participants);
            /**
             * In scope variable containing details about the current user. This is passed through from the originating controller.
             * @memberof manageAttachmentCtrl
             * @type {Object}
             * @private
             */
            $scope.currentUser = currentUser;
            /**
             * In scope variable containing details about the matter. This is passed through from the originating controller.
             * @memberof manageAttachmentCtrl
             * @type {Object}
             * @private
             */
            $scope.matter = matter;


            /**
             * In scope variable containing details about the specific checklist item, with which to make the request
             * @memberof manageAttachmentCtrl
             * @type {Object}
             * @private
             */
            $scope.checklistItem = checklistItem;


            $scope.data = {
                'uploading': false,
                'uploadingPercent': 0
            };


            /**
             * Recieves file details from filepicker.io directive
             *
             * @name                processUpload
             *
             * @param {Object} cat Catgory object
             *
             * @private
             * @method                processUpload
             * @memberof            ChecklistCtrl
             */
            $scope.processCloudUpload = function (files) {
                var matterSlug = $scope.matter.slug;
                var itemSlug = $scope.checklistItem.slug;

                $scope.data.uploading = true;
                $scope.data.uploadingPercent = 0;

                attachmentService.uploadFromCloud(matterSlug, itemSlug, files).then(
                    function success(response) {
                        $scope.data.uploading = false;
                        $scope.data.uploadingPercent = 0;
                        toaster.pop('success', 'Success!', 'File added successfully', 3000);

                        $modalInstance.close();
                    },
                    function error(err) {
                        $log.debug(err);
                        $scope.data.uploading = false;
                        $scope.data.uploadingPercent = 0;

                        var msg = err && err.message ? err.message : err;
                        var title = err && err.title ? err.title : 'Error';

                        toaster.pop('error', title, msg, 5000);
                    }
                );
            };

            /**
             * Initiate the file upload process
             * @param  {Array} $files HTML5 files object
             */
            $scope.onFileDropped = function ($files) {
                var matterSlug = $scope.matter.slug;
                var itemSlug = $scope.checklistItem.slug;

                var promise;

                $scope.data.uploading = true;
                $scope.data.uploadingPercent = 0;

                promise = attachmentService.uploadFile(matterSlug, itemSlug, $files);

                promise.then(
                    function success() {
                        $scope.data.uploading = false;
                        $scope.data.uploadingPercent = 0;
                        toaster.pop('success', 'Success!', 'File added successfully', 3000);

                        $modalInstance.close();
                    },
                    function error(err) {
                        $log.debug(err);
                        try {
                            var msg = err.executed_file[0]
                        } catch (e) {
                            var msg = '';
                        }
                        $scope.data.uploading = false;
                        $scope.data.uploadingPercent = 0;

                        var msg = err && err.message ? err.message : 'Unable to upload file: ' + msg;
                        var title = err && err.title ? err.title : 'Error';

                        toaster.pop('error', title, msg, 5000);
                    },
                    function progress(num) {
                        /* IE-Fix, timeout and force GUI update */
                        setTimeout(function () {
                            $scope.data.uploadingPercent = num;
                            $scope.$apply();
                        }, 10);
                    }
                );
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