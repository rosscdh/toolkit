angular.module('toolkit-gui')


  .controller('newTaskCtrl',[
    '$scope',
    '$modalInstance',
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