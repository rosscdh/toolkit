describe('NavigationCtrl', function() {

	beforeEach(module('toolkit-gui'));

	var scope,ctrl;

	beforeEach(inject(function($rootScope, $controller) {
		scope = $rootScope.$new();
		ctrl = $controller('NavigationCtrl', {$scope: scope});
	}));	

	// Check objects
	it('should have data', function () {
		expect(scope.data instanceof Object).toBe(true);
	});
});