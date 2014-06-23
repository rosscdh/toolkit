angular.module('toolkit-gui').factory('discussionService', [
    '$q',
    '$resource',
    'API_BASE_URL',
    '$log',
    function($q, $resource, API_BASE_URL, $log) {
        function discussionResource() {
            return $resource(API_BASE_URL + 'matters/:matterSlug/discussions/:threadId', {}, {
                'create': { 'method': 'POST', 'headers': { 'Content-Type': 'application/json' }},
                'delete': { 'method': 'DELETE', 'headers': { 'Content-Type': 'application/json' }},
                'get':    { 'method': 'GET', 'headers': { 'Content-Type': 'application/json' }},
                'list':   { 'method': 'GET', 'headers': { 'Content-Type': 'application/json' }},
                'update': { 'method': 'PATCH', 'headers': { 'Content-Type': 'application/json' }}
            });
        }

        function discussionCommentsResource() {
            return $resource(API_BASE_URL + 'matters/:matterSlug/discussions/:threadId/comments/:commentId', {}, {
                'create': { 'method': 'POST', 'headers': { 'Content-Type': 'application/json' }},
                'delete': { 'method': 'DELETE', 'headers': { 'Content-Type': 'application/json' }},
                'list':   { 'method': 'GET', 'headers': { 'Content-Type': 'application/json' }}
            });
        }

        function discussionParticipantsResource() {
            return $resource(API_BASE_URL + 'matters/:matterSlug/discussions/:threadId/participants/:username', {}, {
                'create': { 'method': 'POST', 'headers': { 'Content-Type': 'application/json' }},
                'delete': { 'method': 'DELETE', 'headers': { 'Content-Type': 'application/json' }},
                'list':   { 'method': 'GET', 'headers': { 'Content-Type': 'application/json' }}
            });
        }

        return {
            'create': function(matterSlug, comment, title) {
                var api = discussionResource();
                var deferred = $q.defer();

                api.create({ 'matterSlug': matterSlug }, { 'content': comment, 'title': title },
                    function success(thread) {
                        deferred.resolve(thread);
                    },
                    function error(err) {
                        deferred.reject(err);
                    }
                );

                return deferred.promise;
            },

            'delete': function(matterSlug, threadId) {
                var api = discussionResource();
                var deferred = $q.defer();

                api.delete({ 'matterSlug': matterSlug, 'threadId': threadId },
                    function success() {
                        deferred.resolve();
                    },
                    function error(err) {
                        deferred.reject(err);
                    }
                );

                return deferred.promise;
            },

            'get': function(matterSlug, threadId) {
                var api = discussionResource();
                var deferred = $q.defer();

                api.get({ 'matterSlug': matterSlug, 'threadId': threadId },
                    function success(thread) {
                        deferred.resolve(thread);
                    },
                    function error(err) {
                        deferred.reject(err);
                    }
                );

                return deferred.promise;
            },

            'list': function(matterSlug) {
                var api = discussionResource();
                var deferred = $q.defer();

                api.list({ 'matterSlug': matterSlug },
                    function success(result) {
                        deferred.resolve(result.results);
                    },
                    function error(err) {
                        deferred.reject(err);
                    }
                );

                return deferred.promise;
            },

            'update': function(matterSlug, threadId, comment, title) {
                var api = discussionResource();
                var deferred = $q.defer();

                api.update({ 'matterSlug': matterSlug, 'threadId': threadId}, { 'content': comment, 'title': title },
                    function success(thread) {
                        deferred.resolve(thread);
                    },
                    function error(err) {
                        deferred.reject(err);
                    }
                );

                return deferred.promise;
            },

            'addComment': function(matterSlug, threadId, comment) {
                var api = discussionCommentsResource();
                var deferred = $q.defer();

                api.create({ 'matterSlug': matterSlug, 'threadId': threadId }, { 'content': comment },
                    function success() {
                        deferred.resolve();
                    },
                    function error(err) {
                        deferred.reject(err);
                    }
                );

                return deferred.promise;
            },

            'getComments': function(matterSlug, threadId) {
                var api = discussionCommentsResource();
                var deferred = $q.defer();

                api.list({ 'matterSlug': matterSlug, 'threadId': threadId },
                    function success() {
                        deferred.resolve();
                    },
                    function error(err) {
                        deferred.reject(err);
                    }
                );

                return deferred.promise;
            },

            'removeComment': function(matterSlug, threadId, commentId) {
                var api = discussionCommentsResource();
                var deferred = $q.defer();

                api.delete({ 'matterSlug': matterSlug, 'threadId': threadId, 'commentId': commentId },
                    function success() {
                        deferred.resolve();
                    },
                    function error(err) {
                        deferred.reject(err);
                    }
                );

                return deferred.promise;
            },

            'addParticipant': function(matterSlug, threadId, details) {
                var api = discussionParticipantsResource();
                var deferred = $q.defer();

                api.create({ 'matterSlug': matterSlug, 'threadId': threadId }, details,
                    function success(response) {
                        deferred.resolve(response);
                    },
                    function error(err) {
                        deferred.reject(err);
                    }
                );

                return deferred.promise;
            },

            'getParticipants': function(matterSlug, threadId) {
                var api = discussionParticipantsResource();
                var deferred = $q.defer();

                api.list({ 'matterSlug': matterSlug, 'threadId': threadId },
                    function success(response) {
                        deferred.resolve(response);
                    },
                    function error(err) {
                        deferred.reject(err);
                    }
                );

                return deferred.promise;
            },

            'removeParticipant': function(matterSlug, threadId, username) {
                var api = discussionParticipantsResource();
                var deferred = $q.defer();

                api.delete({ 'matterSlug': matterSlug, 'threadId': threadId, 'username': username },
                    function success(response) {
                        deferred.resolve(response);
                    },
                    function error(err) {
                        deferred.reject(err);
                    }
                );

                return deferred.promise;
            }
        };


    }]
);


