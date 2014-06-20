angular.module('toolkit-gui').controller('DiscussionCtrl', [
    '$modal',
    '$rootScope',
    '$scope',
    '$state',
    '$location',
    '$anchorScroll',
    'discussionService',
    'ezConfirm',
    'matterService',
    'smartRoutes',
    'toaster',
    '$log',
    '$q',
    function($modal, $rootScope, $scope, $state, $location, $anchorScroll, discussionService, ezConfirm, matterService, smartRoutes, toaster, $log, $q) {
        'use strict';

        var routeParams = smartRoutes.params();

        $scope.data = {
            'matter': null,
            'matterSlug': routeParams.matterSlug,
            'page': 'discussion',
            'request': {
                'message': null,
            },
            'selectedThread': null,
            'threads': [],
            'threadId': routeParams.threadId
        };

        if ($scope.data.matterSlug && $scope.data.matterSlug !== '' && $scope.data.matterCalled == null) {
            $scope.data.matterCalled = true;

            matterService.get($scope.data.matterSlug).then(
                function success(singleMatter) {
                    $scope.data.matter = singleMatter;

                    // set matter in the services
                    matterService.selectMatter(singleMatter);
                    // $scope.initialiseMatter(singleMatter);
                    $scope.initializeDiscussion(singleMatter);

                    // userService.setCurrent(singleMatter.current_user, singleMatter.lawyer);

                    // $scope.initialiseIntercom(singleMatter.current_user);

                    $scope.handleUrlState();
                },
                function error(/*err*/) {
                    toaster.pop('error', 'Error!', 'Unable to load matter', 5000);
                }
            );
        }

        $rootScope.$on('$stateChangeSuccess', function() {
            $scope.handleUrlState();
        });

        $scope.handleUrlState = function() {
            var threadId = $state.params.threadId;

            if (threadId && (!$scope.data.selectedThread || threadId !== $scope.data.selectedThread.id)) {
                $scope.selectThread(threadId);
            }
        };

        $scope.initializeDiscussion = function() {
            var matterSlug = $scope.data.matterSlug;

            discussionService.list(matterSlug).then(
                function success(result) {
                    $scope.data.threads = result;
                },
                function error(/*err*/) {
                    toaster.pop('error', 'Error!', 'Unable to read discussion list.', 5000);
                }
            );
        };

        $scope.createThread = function() {
            var modalInstance = $modal.open({
                'templateUrl': '/static/ng/partial/discussion/includes/create-thread.html',
                'controller': 'CreateThreadCtrl',
                'resolve': {
                    'currentUser': function() {
                        return $scope.data.matter.current_user;
                    },
                    'matter': function() {
                        return $scope.data.matter;
                    }
                }
            });

            modalInstance.result.then(
                function ok() {
                    $scope.initializeDiscussion($scope.data.matter);
                },
                function cancel() {}
            );
        };

        $scope.deleteThread = function(thread) {
            ezConfirm.create('Delete Thread', 'Please confirm you would like to delete this thread?',
                function yes() {
                    var matterSlug = $scope.data.matterSlug;
                    discussionService.delete(matterSlug, thread.id).then(
                        function success() {
                            $scope.initializeDiscussion();
                        },
                        function error(/*err*/) {
                            toaster.pop('error', 'Error!', 'Unable to delete thread.', 5000);
                        }
                    );
                }
            );
        };

        $scope.selectThread = function(threadId) {
            $scope.loadThreadDetails(threadId).then(
                function success(thread) {
                    $scope.data.selectedThread = thread;
                }
            );

            $scope.displayThread();
        };

        $scope.loadThreadDetails = function(threadId) {
            var deferred = $q.defer();

            var matterSlug = $scope.data.matterSlug;
            discussionService.get(matterSlug, threadId).then(
                function success(thread) {
                    deferred.resolve(thread);
                },
                function error(/*err*/) {
                    toaster.pop('error', 'Error!', 'Unable to read discussion thread.', 5000);
                }
            );

            return deferred.promise;
        };

        $scope.displayThread = function() {
            $scope.data.page = 'thread';
        };

        $scope.request = function() {
            var deferred = $q.defer();

            var matterSlug = $scope.data.matterSlug;
            var threadId = $scope.data.selectedThread.id;

            $scope.sendingMessage = true;

            discussionService.comment(matterSlug, threadId, $scope.data.request.message).then(
                function success(response) {
                    deferred.resolve(response);
                    $scope.selectThread(threadId);

                    // Clear message in GUI
                    $scope.data.request.message = '';
                    $scope.sendingMessage = false;                    
                },
                function error(/*err*/) {
                    toaster.pop('error', 'Error!', 'Unable to comment on discussion.', 5000);
                    $scope.sendingMessage = false;
                }
            );
        };

        $scope.addThreadParticipant = function(thread) {
            var modalInstance = $modal.open({
                'templateUrl': '/static/ng/partial/discussion/includes/add-thread-participant.html',
                'controller': 'AddThreadParticipantCtrl',
                'resolve': {
                    'currentUser': function() {
                        return $scope.data.matter.current_user;
                    },
                    'matter': function() {
                        return $scope.data.matter;
                    },
                    'thread': function() {
                        return thread;
                    }
                }
            });

            modalInstance.result.then(
                function ok() {
                    $scope.selectThread(thread.id);
                },
                function cancel() {}
            );
        };
    }
]);
