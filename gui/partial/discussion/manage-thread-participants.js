angular.module('toolkit-gui').controller('ManageThreadParticipantsCtrl', [
    '$modalInstance',
    '$rootScope',
    '$scope',
    'currentUser',
    'discussionService',
    'matter',
    'matterService',
    'thread',
    'toaster',
    '$log',
    '$q',
    function($modalInstance, $rootScope, $scope, currentUser, discussionService, matter, matterService, thread, toaster, $log, $q) {
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

        $scope.isParticipant = function(person) {
            var isParticipant = false;
            angular.forEach($scope.thread.participants, function(participant, key) {
                if (participant.username === person.username) {
                    isParticipant = true;
                }
            });

            return isParticipant;
        };

        $scope.isColleague = function(person) {
            if (person.role === 'owner' || person.role === 'colleague') {
                return true;
            }

            return false;
        };

        $scope.addParticipant = function(person) {
            var deferred = $q.defer();

            var matterSlug = $scope.matter.slug;
            var threadSlug = $scope.thread.slug;

            var details = { 'username': person.username };

            discussionService.addParticipant(matterSlug, threadSlug, details).then(
                function success(response) {
                    $modalInstance.close();
                    $rootScope.$emit('discussionChangeParticipantSuccess');

                    deferred.resolve(response);
                },
                function error(/*err*/) {
                    toaster.pop('error', 'Error!', 'Unable to add the participant.', 5000);
                }
            );

            return deferred.promise;
        };

        $scope.removeAsParticipant = function() {
            var deferred = $q.defer();

            var matterSlug = $scope.matter.slug;
            var threadSlug = $scope.thread.slug;

            discussionService.removeParticipant(matterSlug, threadSlug, $scope.currentUser.username).then(
                function success(response) {
                    $modalInstance.close();
                    $rootScope.$emit('discussionChangeParticipantSuccess');

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
