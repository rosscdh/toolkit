angular.module('toolkit-gui')


.controller('MarkdownInfoCtrl',[
  '$scope',
  '$modalInstance',
  function($scope, $modalInstance){
    'use strict';
    /**
     * Closes dialog
     * @memberOf MarkdownInfoCtrl
     * @method cancel
     */
    $scope.cancel = function(){
      $modalInstance.dismiss();
    };
  }


]);