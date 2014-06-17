angular.module('toolkit-gui')


.controller('MarkdownInfoCtrl',[
  '$scope',
  '$modalInstance',
  function($scope, $modalInstance){
    'use strict';
    $scope.cancel = function(){
      $modalInstance.dismiss();

    };

  }


]);