angular.module('toolkit-gui')

  .controller('assignTaskCtrl',[
    '$scope',
    '$modalInstance',
    'participants',
    function($scope, $modalInstance){
      'use strict';
      /**
       * Closes dialog
       * @memberOf Ma
       * @method cancel
       */
      $scope.cancel = function(){
        $modalInstance.dismiss();
      };
    }


]);