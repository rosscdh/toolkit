angular.module('toolkit-gui')


.controller('deleteTaskCtrl',[
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