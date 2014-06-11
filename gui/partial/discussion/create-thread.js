angular.module('toolkit-gui').controller('CreateThreadCtrl', [
    '$modalInstance',
    '$scope',
    'currentUser',
    'discussionService',
    'matter',
    'matterService',
    'toaster',
    '$log',
    '$q',
    function($modalInstance, $scope, currentUser, discussionService, matter, matterService, toaster, $log, $q) {
        'use strict';

        $scope.currentUser = currentUser;
        $scope.data = {
            'request': {
                'comment': null,
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
            discussionService.create(matterSlug, comment, title).then(
                function success(response) {
                    $modalInstance.close();

                    deferred.resolve(response);
                },
                function error(/*err*/) {
                    toaster.pop('error', 'Error!', 'Unable to create the thread.', 5000);
                }
            );

            return deferred.promise;
        };
    }
]);
