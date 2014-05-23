/**
 * Directive for displaying the mentions box and completing the user tags.
 * Communicates through the broadcasts with the mentions container which is appended to the body.
 *
**/
angular.module('toolkit-gui').directive('mentionsContainer', ['$compile', '$log', '$sce', '$filter', function ($compile, $log, $sce, $filter) {
    return {
        scope: {
            participants: '=',
            currUser: '='
        },
        replace: true,
        controller: ['$rootScope', '$scope', '$http', '$log', function ($rootScope, $scope, $http, $log) {
            $scope.data = {
                'isContainerVisible': false,
                'filtered_participants': $scope.participants,
                'coords': {
                    'x': 0,
                    'y': 0
                },
                'width': 250,
                'mentiontag': null,
                'searchtext': null,
                'position': 'left',
                'cursorpos': 0,
                'focusIndex': 0
            };

            $scope.filterParticipants = function (tag) {
                var searchStr = tag.substring(1, tag.length).toLowerCase();

                $log.debug('filtering participants by tag: ' + searchStr);

                $scope.data.filtered_participants = jQuery.grep($scope.participants, function (p) {
                    if (p.username === searchStr) {
                        //tag already complete
                        return false;
                    }

                    var username = p.username.toLowerCase();
                    var first_name = p.first_name.toLowerCase();
                    var last_name = p.last_name.toLowerCase();

                    return (username.match("^" + searchStr) || first_name.match("^" + searchStr) || last_name.match("^" + searchStr));
                });
            };

            $scope.extractMentiontag = function () {
                var text = $scope.data.searchtext;
                var cursorpos = parseInt($scope.data.cursorpos);
                text = text.replace(/\n/g, ' ');
                var tagslistarr = text.split(' ');
                $scope.data.mentiontag = null;

                jQuery.each(tagslistarr, function (i, tag) {
                    if (tag.indexOf('@') === 0) {

                        //find all tag occurences in complete string
                        var tagpos = $scope.getIndicesOf(tag, text);
                        jQuery.each(tagpos, function (i, tagpos) {
                            //if cursorpos between beginning and end of string, this is the tag we are looking for
                            var tagend = parseInt(tagpos + tag.length);
                            if (tagpos < cursorpos && tagend >= cursorpos) {
                                $scope.data.foundtagpos = tagpos;
                                $scope.data.mentiontag = tag;
                                return;
                            }
                        });

                        if ($scope.data.mentiontag != null) {
                            return;
                        }
                    }
                });

                return $scope.data.mentiontag;
            };

            $scope.showContainer = function () {
                var mentiontag = $scope.extractMentiontag();

                if (mentiontag && mentiontag.length > 1) {
                    $scope.filterParticipants(mentiontag);

                    if ($scope.data.filtered_participants.length > 0) {
                        var position = $scope.data.position;

                        if (position === 'left') {
                            $scope.data.coords.x -= $scope.data.width + 10;
                        }

                        if ($scope.data.focusIndex >= $scope.data.filtered_participants.length){
                            $scope.data.focusIndex=0;
                        }

                        $scope.data.isContainerVisible = true;

                    } else {
                        $scope.data.isContainerVisible = false;
                    }
                } else {
                    $scope.data.isContainerVisible = false;
                }
            };

            $scope.selectParticipant = function (participant) {
                $rootScope.$broadcast('mentions-setTag', {'tagpos': $scope.data.foundtagpos, 'tag': $scope.data.mentiontag, 'username': participant.username, 'boxid': $scope.data.boxid });
                $scope.data.isContainerVisible = false;
            };


            $scope.getIndicesOf = function (searchStr, str) {
                var startIndex = 0, searchStrLen = searchStr.length;
                var index, indices = [];

                while ((index = str.indexOf(searchStr, startIndex)) > -1) {
                    indices.push(index);
                    startIndex = index + searchStrLen;
                }
                return indices;
            };

            $scope.keyPressed = function(keyCode){
                if (keyCode === 13) {
                        $scope.selectParticipant($scope.data.filtered_participants[$scope.data.focusIndex]);
                } else if (keyCode === 38) {
                    if ($scope.data.focusIndex > 0){
                        $scope.data.focusIndex--;
                    } else {
                        $scope.data.focusIndex = $scope.data.filtered_participants.length-1;
                    }
                } else if (keyCode === 40) {
                    if ($scope.data.focusIndex < $scope.data.filtered_participants.length-1){
                        $scope.data.focusIndex++;
                    } else {
                        $scope.data.focusIndex = 0;
                    }
                }
            };

            $scope.$watch('data.isContainerVisible', function () {
                $rootScope.$broadcast('mentions-containerStateChanged', {'isVisible': $scope.data.isContainerVisible });
            });

        }],
        templateUrl: '/static/ng/directive/mentions/mentionscontainer.html',
        link: function (scope, element, attrs) {

            scope.$on('mentions-showMentionsContainer', function (event, args) {
                scope.data.coords = args.coords;
                scope.data.position = args.position;
                scope.data.searchtext = args.text;
                scope.data.cursorpos = args.cursorpos;
                scope.data.boxid = args.boxid;

                if(scope.data.searchtext){
                    scope.showContainer();
                }
            });

            scope.$on('mentions-keydown', function (event, args) {
                scope.keyPressed(args.keyCode);
            });
        }
    };
}]);

