angular.module('toolkit-gui').directive('mentionsBox', ['$compile', '$log', '$sce', '$filter', function ($compile, $log, $sce, $filter) {
    return {
        scope: {
            text: '=',
            participants: '=',
            currUser: '='
        },
        replace: true,
        controller: ['$rootScope', '$scope', '$http', '$log',
            function ($rootScope, $scope, $http, $log) {
                $scope.data = {
                    'coords': {
                        'x': 0,
                        'y': 0
                    }
                }

                $scope.searchInText = function () {
                    var coords = angular.copy($scope.data.coords);
                    $rootScope.$broadcast('mentions-showMentionsContainer', {'text': $scope.text, 'coords': coords, 'position': 'left'});
                }
        }],
        template: '<textarea class="form-control" ng-model="text" ng-keyup="searchInText()"></textarea>',
        link: function (scope, element, attrs) {
            $log.debug('Init mentions directive');
            var elem = jQuery(element);

            var offset = elem.offset();
            scope.data.coords.x = offset.left - jQuery(window).scrollLeft();
            scope.data.coords.y = offset.top - jQuery(window).scrollTop();
        }
    };
}]);

