angular.module('toolkit-gui').directive('mentionsContainer', ['$compile', '$log', '$sce', '$filter', function ($compile, $log, $sce, $filter) {
    return {
        scope: {
            participants: '=',
            currUser: '='
        },
        replace: true,
        controller: ['$scope', '$http', '$log', function ($scope, $http, $log) {
            $scope.data = {
                'isContainerVisible': false,
                'filtered_participants': $scope.participants,
                'coords': {
                    'x': 0,
                    'y': 0
                },
                'width': 400
            }

            $scope.filterParticipants = function (text) {
                $log.debug('filtering participants');
                $scope.data.filtered_participants = jQuery.grep($scope.participants, function (p) {
                    return (p.username.match("^" + text));
                });
            }

            $scope.showContainer = function (args) {
                $log.debug(args);

                var searchtext = args.text;

                if (searchtext) {
                    //http://stackoverflow.com/questions/7150652/regex-valid-twitter-mention
                    var n = searchtext.match(/\B\@([\w\-]+)/gim);
                    $log.debug(n);
                    if (n !== null) {
                        var foundtags = n[n.length - 1].substring(1, n[0].length);
                        $log.debug(foundtags);

                        $scope.filterParticipants(foundtags);

                        if ($scope.data.filtered_participants.length > 0) {
                            $scope.data.coords = args.coords;

                            if (args.position === 'left') {
                                $scope.data.coords.x -= $scope.data.width;
                            }

                            $scope.data.isContainerVisible = true;

                        } else {
                            $scope.data.isContainerVisible = false;
                        }
                    } else {
                        $scope.data.isContainerVisible = false;
                    }
                } else {
                    $scope.data.isContainerVisible = false;
                }
            }
        }],
        templateUrl: '/static/ng/directive/mentions/mentionscontainer.html',
        link: function (scope, element, attrs) {

            scope.$on('mentions-showMentionsContainer', function (event, args) {
                scope.showContainer(args);
            });
        }
    };
}]);

