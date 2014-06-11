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

        function threadResource() {
            return $resource(API_BASE_URL + 'matters/:matterSlug/discussions/:threadId/comments', {}, {
                'create': { 'method': 'POST', 'headers': { 'Content-Type': 'application/json' }},
                'delete': { 'method': 'DELETE', 'headers': { 'Content-Type': 'application/json' }},
                'update': { 'method': 'PATCH', 'headers': { 'Content-Type': 'application/json' }}
            });
        }

        return {
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

            'create': function(matterSlug, comment, title) {
                var api = discussionResource();
                var deferred = $q.defer();

                api.create({ 'matterSlug': matterSlug }, { 'comment': comment, 'title': title },
                    function success(thread) {
                        deferred.resolve(thread);
                    },
                    function error(err) {
                        deferred.reject(err);
                    }
                );

                return deferred.promise;
            },

            // 'delete': function(matterSlug, itemSlug, commentId) {
                // var api = commentResource();
                // var deferred = $q.defer();

                // api.delete({'matterSlug': matterSlug, 'itemSlug': itemSlug, 'id':commentId},
                    // function success() {
                        // deferred.resolve();
                    // },
                    // function error( err ) {
                        // deferred.reject( err );
                    // }
                // );

                // return deferred.promise;
            // },

            // 'update': function(matterSlug, itemSlug, commentId, comment) {
                // var api = commentResource();
                // var deferred = $q.defer();

                // api.update({'matterSlug': matterSlug, 'itemSlug': itemSlug, 'id':commentId}, {'comment': comment},
                    // function success() {
                        // deferred.resolve();
                    // },
                    // function error( err ) {
                        // deferred.reject( err );
                    // }
                // );

                // return deferred.promise;
            // }

            'comment': function(matterSlug, threadId, comment) {
                var api = threadResource();
                var deferred = $q.defer();

                api.create({'matterSlug': matterSlug, 'threadId': threadId}, {'comment': comment},
                    function success() {
                        deferred.resolve();
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
