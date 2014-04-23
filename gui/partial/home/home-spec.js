describe('HomeCtrl', function() {
	'use strict';

	beforeEach(module('toolkit-gui'));

	var scope,ctrl;

	beforeEach(inject(function($rootScope, $controller) {
		scope = $rootScope.$new();
		ctrl = $controller('HomeCtrl', {$scope: scope});
	}));

	// Controller exists
	it('should have data', function () {
		expect(scope.data instanceof Object).toBe(true);
	});
});