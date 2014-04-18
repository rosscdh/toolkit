describe('ParticipantInviteCtrl', function() {
    beforeEach(function() {
        module(function($provide) {            
			$provide.constant('API_BASE_URL', '/api/v1/');
            $provide.constant('STATUS_LEVEL', {'OK':0,'WARNING':1,'ERROR':2} );
            $provide.constant('DEBUG_MODE', false);
            $provide.constant('SENTRY_PUBLIC_DSN', 'https://b5a6429d03e2418cbe71cd5a4c9faca6@app.getsentry.com/6287' );
            $provide.constant('INTERCOM_APP_ID', 'ooqtbx99' );
			
			$provide.constant('$modalInstance',{});
			$provide.constant('participants',{});
			$provide.constant('currentUser',{});
			$provide.constant('matter',{});
        });
		
	});
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