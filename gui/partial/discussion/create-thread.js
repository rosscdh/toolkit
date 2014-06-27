angular.module('toolkit-gui').controller('CreateThreadCtrl', [
    '$modalInstance',
    '$rootScope',
    '$scope',
    'currentUser',
    'discussionService',
    'matter',
    'matterService',
    'toaster',
    '$log',
    '$q',
    function($modalInstance, $rootScope, $scope, currentUser, discussionService, matter, matterService, toaster, $log, $q) {
        'use strict';

        $scope.currentUser = currentUser;
        $scope.data = {
            'request': {
                'comment': null,
                'participants': {},
                'title': null
            }
        };
        $scope.matter = matter;

        $scope.cancel = function() {
            $modalInstance.dismiss('cancel');
        };

        $scope.ok = function() {
            $modalInstance.close();
        };

        $scope.create = function() {
            var deferred = $q.defer();

            var matterSlug = $scope.matter.slug;
            var comment = $scope.data.request.comment;
            var title = $scope.data.request.title;

            var participants = $scope.data.request.participants;

            discussionService.create(matterSlug, comment, title).then(
                function success(response) {
                    deferred.resolve(response);

                    angular.forEach(participants, function(key, participant) {
                        discussionService.addParticipant(matterSlug, response.slug, { 'username': participant }).then(
                            function success(response) {
                                $rootScope.$emit('discussionChangeParticipantSuccess');
                            },
                            function error(/*err*/) {
                                toaster.pop('error', 'Error!', 'Unable to add the participant.', 5000);
                            }
                        );
                    });

                    $modalInstance.close();
                },
                function error(/*err*/) {
                    toaster.pop('error', 'Error!', 'Unable to create the thread.', 5000);
                }
            );

            return deferred.promise;
        };
    }
]);
