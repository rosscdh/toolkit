angular.module('toolkit-gui')


.controller('PersonalSettingsCtrl',[
  '$scope',
  '$modalInstance',
  function($scope, $modalInstance){
    'use strict';

    $scope.state = 'default';

    $scope.settings = {
      'notificationPermissionLevel': 'default'
    };

    /**
     * Requests desktop notifications, when selected closed the dialog
     * Returns updated participants array.
     *
     * @name        requestNotifyPermission
     * 
     * @private
     * @method        requestNotifyPermission
     * @memberof      ParticipantInviteCtrl
     */
    $scope.requestNotifyPermission = function() {
      $scope.state = 'requestingDesktopPermissions';
      notify.requestPermission(function(){
        $scope.state = 'default';

        $scope.settings.notificationPermissionLevel = notify.permissionLevel();
        $modalInstance.close( $scope.settings );
      });
    };



    
    $scope.ok = function () {
      $modalInstance.close( $scope.participants );
    };

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