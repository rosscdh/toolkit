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
            'archivedThreads': [],
            'matter': null,
            'matterSlug': routeParams.matterSlug,
            'page': 'discussion',
            'request': {
                'message': null,
            },
            'searchEnabled': false,
            'selectedThread': null,
            'threads': [],
            'view': 'inbox',
            'threadSlug': routeParams.threadSlug

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

        $rootScope.$on('discussionChangeParticipantSuccess', function() {
            $scope.initializeDiscussion();
        });

        $scope.handleUrlState = function() {
            var threadSlug = $state.params.threadSlug;

            if (threadSlug && (!$scope.data.selectedThread || threadSlug !== $scope.data.selectedThread.slug)) {
                $scope.selectThread(threadSlug);
            }
        };

        $scope.initializeDiscussion = function() {
            var matterSlug = $scope.data.matterSlug;

            discussionService.list(matterSlug).then(
                function success(result) {
                    $scope.data.threads = result;
                },
                function error(/*err*/) {
                    toaster.pop('error', 'Error!', 'Unable to read discussion threads.', 5000);
                }
            );

            discussionService.listArchived(matterSlug).then(
                function success(result) {
                    $scope.data.archivedThreads = result;
                },
                function error(/*err*/) {
                    toaster.pop('error', 'Error!', 'Unable to read archived discussion threads.', 5000);
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

        $scope.archiveThread = function(thread) {
            ezConfirm.create('Archive Thread', 'Please confirm you would like to archive this thread?',
                function yes() {
                    var matterSlug = $scope.data.matterSlug;
                    discussionService.archive(matterSlug, thread.slug).then(
                        function success(thread) {
                            $scope.initializeDiscussion();
                            $scope.data.selectedThread = thread;
                        },
                        function error(/*err*/) {
                            toaster.pop('error', 'Error!', 'Unable to archive thread.', 5000);
                        }
                    );
                }
            );
        };

        $scope.unarchiveThread = function(thread) {
            ezConfirm.create('Unarchive Thread', 'Please confirm you would like to unarchive this thread?',
                function yes() {
                    var matterSlug = $scope.data.matterSlug;
                    discussionService.unarchive(matterSlug, thread.slug).then(
                        function success(thread) {
                            $scope.initializeDiscussion();
                            $scope.data.selectedThread = thread;
                            // $scope.selectThread(thread);
                        },
                        function error(/*err*/) {
                            toaster.pop('error', 'Error!', 'Unable to unarchive thread.', 5000);
                        }
                    );
                }
            );
        };

        $scope.deleteThread = function(thread) {
            ezConfirm.create('Delete Thread', 'Please confirm you would like to delete this thread?',
                function yes() {
                    var matterSlug = $scope.data.matterSlug;
                    discussionService.delete(matterSlug, thread.slug).then(
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

        $scope.selectThread = function(threadSlug) {
            $scope.loadThreadDetails(threadSlug).then(
                function success(thread) {
                    $scope.data.selectedThread = thread;
                }
            );

            $scope.displayThread();
        };

        $scope.loadThreadDetails = function(threadSlug) {
            var deferred = $q.defer();

            var matterSlug = $scope.data.matterSlug;
            discussionService.get(matterSlug, threadSlug).then(
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
            var threadSlug = $scope.data.selectedThread.slug;

            if (!$scope.data.request.message) {
                return;
            }

            $scope.sendingMessage = true;

            discussionService.addComment(matterSlug, threadSlug, $scope.data.request.message).then(
                function success(response) {
                    deferred.resolve(response);
                    $scope.initializeDiscussion();
                    $scope.selectThread(threadSlug);

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

        $scope.manageThreadParticipants = function(thread) {
            var modalInstance = $modal.open({
                'templateUrl': '/static/ng/partial/discussion/includes/manage-thread-participants.html',
                'controller': 'ManageThreadParticipantsCtrl',
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
                    $scope.selectThread(thread.slug);
                },
                function cancel() {}
            );
        };

         $scope.showMarkDownInfo = function() {
          $modal.open({
            'templateUrl': '/static/ng/partial/markdown/markdown-info.html',
            'controller': 'MarkdownInfoCtrl'
          });

        };
    }
]);
