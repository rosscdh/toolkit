



angular.module('toolkit-gui').directive('modalLoading', ['$log', function ($log) {
    return {
      transclude: true,
      scope: {
          'modalLoading': "="
      },
      template: '<div class="loading" ng-show="modalLoading"><i class="fa fa-spinner fa-3x fa-spin"></i></div><div ng-transclude></div>',
      controller: ['$scope', function ($scope) {
      }]
    };
}]);
