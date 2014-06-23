angular.module('toolkit-gui').controller('AddThreadParticipantCtrl', [
    '$modalInstance',
    '$scope',
    'currentUser',
    'discussionService',
    'matter',
    'matterService',
    'thread',
    'toaster',
    '$log',
    '$q',
    function($modalInstance, $scope, currentUser, discussionService, matter, matterService, thread, toaster, $log, $q) {
        'use strict';

        $scope.currentUser = currentUser;
        $scope.data = {};
        $scope.matter = matter;
        $scope.thread = thread;

        $scope.cancel = function() {
            $modalInstance.dismiss('cancel');
        };

        $scope.ok = function() {
            $modalInstance.close();
        };

        $scope.addParticipant = function() {
            var deferred = $q.defer();

            var matterSlug = $scope.matter.slug;
            var threadId = $scope.thread.id;

            var details = {
                'email': 'testlawyer@lawpal.com'
                // 'username': 'testlawyer'
            };

            discussionService.addParticipant(matterSlug, threadId, details).then(
                function success(response) {
                    $modalInstance.close();

                    deferred.resolve(response);
                },
                function error(/*err*/) {
                    toaster.pop('error', 'Error!', 'Unable to add the participant.', 5000);
                }
            );

            return deferred.promise;
        };

        $scope.removeParticipant = function() {
            var deferred = $q.defer();

            var matterSlug = $scope.matter.slug;
            var threadId = $scope.thread.id;

            var username = 'testlawyer';

            discussionService.removeParticipant(matterSlug, threadId, username).then(
                function success(response) {
                    $modalInstance.close();

                    deferred.resolve(response);
                },
                function error(/*err*/) {
                    toaster.pop('error', 'Error!', 'Unable to remove the participant.', 5000);
                }
            );

            return deferred.promise;
        };
    }
]);
