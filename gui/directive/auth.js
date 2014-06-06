/*angular.module('toolkit-gui').directive('requiredPermission', ['$log', function ($log) {
 return function (scope, elem, attr){
 var curr_user = scope.data.usdata.current;

 if (curr_user) {

 }


 function link($scope, $element, attr, ctrl) {

 if (attr.hasOwnProperty("ngShow")) {
 $scope.$watch("ngShow", function (value) {
 if (value) {
 $element.show();
 }
 else {
 $element.hide();
 }
 });
 };
 }]);*/


angular.module('toolkit-gui').directive('auth', [
    '$rootScope',
    'matterService',
    '$log',
    function ($rootScope, matterService, $log) {
        return {
            replace: false,
            scope: {
                'requiredPermission': "@",
                'notPermission': "@"
            },
            controller: ['$scope', function ($scope) {
                $scope.hasAccess = false;

                $rootScope.$on('permissionsSet', function (e) {
                    if (!$scope.user) {
                        $scope.user = matterService.data().selected.current_user;
                    }

                    $log.debug("checking permissions");
                    if ($scope.user.permissions && $scope.requiredPermission && $scope.user.permissions[$scope.requiredPermission] === true) {
                        $scope.hasAccess = true;
                    } else if ($scope.user.permissions && $scope.notPermission && $scope.user.permissions[$scope.notPermission] === false) {
                        $scope.hasAccess = true;
                    }
                });
            }],
            link: function ($scope, $element, attr, ctrl) {
                $scope.$watch("hasAccess", function (value) {
                    if (value) {
                        $element.show();
                    }
                    else {
                        $element.hide();
                    }
                });
            }
        }
    }]);
