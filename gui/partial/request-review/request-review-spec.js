describe('RequestreviewCtrl', function() {

	beforeEach(module('toolkit-gui'));

	var scope,ctrl;

    beforeEach(inject(function($rootScope, $controller) {
      scope = $rootScope.$new();
      ctrl = $controller('RequestreviewCtrl', {
      	'$scope': scope,
      	'$modalInstance': {},
      	'participants': [],
      	'checklistItem': {},
      	'revision': {},
      	'currentUser': { 'name': 'Me' },
      	'matter': { 'name': 'Matter name' },
      	'participantService': {}
      });
    }));	

	it('should ...', inject(function() {

		expect(1).toEqual(1);
		
	}));

});