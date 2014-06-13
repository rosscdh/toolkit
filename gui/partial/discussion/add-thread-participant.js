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
    }
]);
