'use strict';

describe('Controller: MessagingCtrl', function () {

  // load the controller's module
  beforeEach(module('toolkitGuiApp'));

  var MessagingCtrl,
    scope;

  // Initialize the controller and a mock scope
  beforeEach(inject(function ($controller, $rootScope) {
    scope = $rootScope.$new();
    MessagingCtrl = $controller('MessagingCtrl', {
      $scope: scope
    });
  }));

  it('should attach a list of awesomeThings to the scope', function () {
    expect(scope.awesomeThings.length).toBe(3);
  });
});
