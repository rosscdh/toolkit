/**
 * Directive for displaying the mentions box and completing the user tags.
 * Communicates through the broadcasts with the mentions container which is appended to the body.
 *
**/
angular.module('toolkit-gui').directive('mentionsBox', ['$compile', '$log', '$sce', '$filter', function ($compile, $log, $sce, $filter) {
    return {
        scope: {
            text: '=',
            participants: '=',
            currUser: '=',
            containerPosition: "@"
        },
        replace: true,
        controller: ['$rootScope', '$scope', '$http', '$log',
            function ($rootScope, $scope, $http, $log) {
                $scope.data = {
                    'coords': {
                        'x': 0,
                        'y': 0
                    },
                    'cursorpos': 0,
                    'containerVisible': false,
                    'boxid': ''
                };

                $scope.transmitContent = function () {
                    var coords = angular.copy($scope.data.coords);
                    $rootScope.$broadcast('mentions-showMentionsContainer', {
                        'text': $scope.text,
                        'cursorpos': $scope.data.cursorpos,
                        'coords': coords,
                        'position': $scope.containerPosition,
                        'boxid': $scope.data.boxid
                    });
                };

                $scope.$on('mentions-setTag', function (event, args) {
                    if (args.boxid === $scope.data.boxid) {
                        var tagpos = args.tagpos;
                        var tag = args.tag;
                        var username = args.username;

                        //complete tag in specific area in text
                        $scope.text = $scope.text.substring(0, tagpos) + $scope.text.substring(tagpos, tagpos + tag.length).replace(tag, "@" + username) + $scope.text.substring(tagpos + tag.length, $scope.text.length);
                        $scope.$broadcast('focusOn', "taginserted");
                    }
                });

                $scope.$on('mentions-containerStateChanged', function (event, args) {
                    $scope.data.containerVisible = args.isVisible;
                });

                $scope.keyListener = function (event) {
                    if ($scope.data.containerVisible && jQuery.inArray(event.keyCode, [13,38,40]) !== -1) {
                        $rootScope.$broadcast('mentions-keydown', {'keyCode': event.keyCode});
                        event.stopPropagation();
                        event.preventDefault();
                    }
                };

            }],
        template: '<textarea class="form-control" ng-model="text" ng-keyup="textListener()" ng-keydown="keyListener($event)" focus-on="taginserted"></textarea>',
        link: function (scope, element, attrs) {
            var elem = jQuery(element);

            scope.data.boxid = Math.random().toString(36).substring(7);

            scope.getCursorPosition = function () {
                var el = jQuery(element).get(0);
                var pos = 0;
                if ('selectionStart' in el) {
                    pos = el.selectionStart;
                } else if ('selection' in document) {
                    el.focus();
                    var Sel = document.selection.createRange();
                    var SelLength = document.selection.createRange().text.length;
                    Sel.moveStart('character', -el.value.length);
                    pos = Sel.text.length - SelLength;
                }
                return pos;
            };

            scope.textListener = function () {
                var offset = elem.offset();
                scope.data.coords.x = offset.left - jQuery(window).scrollLeft();
                scope.data.coords.y = offset.top - jQuery(window).scrollTop() + elem.height();

                scope.data.cursorpos = scope.getCursorPosition();
                scope.transmitContent();
            };

        }
    };
}]);

