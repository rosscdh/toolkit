describe('ParticipantInviteCtrl', function() {

	beforeEach(module('toolkit-gui'));

	var scope,ctrl;

    beforeEach(inject(function($rootScope, $controller) {
      scope = $rootScope.$new();
      ctrl = $controller('ParticipantInviteCtrl', {
      	'$scope': scope,
      	'$modalInstance': {},
      	'participants': [],
      	'currentUser': { 'name': 'Me' },
      	'matter': { 'name': 'Matter name' },
      	'participantService': {}
      });
    }));	

	it('should have data', function () {
		expect(scope.data instanceof Object).toBe(true);
	});

	it('should have participants', function () {
		expect(scope.participants.length).toBe(0);
	});

	it('should have participants', function () {
		expect(scope.currentUser.name).toBe('Me');
	});

	it('should have matter', function () {
		expect(scope.matter.name).toBe('Matter name');
	});
});