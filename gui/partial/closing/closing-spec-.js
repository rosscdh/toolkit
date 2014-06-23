describe('ClosingCtrl', function() {

	beforeEach(
		module('toolkit-gui')
		.constant('API_BASE_URL', '/api/v1/')
	    .constant('STATUS_LEVEL', {'OK':0,'WARNING':1,'ERROR':2} )
	    .constant('DEBUG_MODE', true)
	    .constant('SENTRY_PUBLIC_DSN', 'http://5584db708b75400fb439d4592c29fc9a@sentry.ambient-innovation.com/24' )
	);

	var scope,ctrl;

    beforeEach(inject(function($rootScope, $controller) {
      scope = $rootScope.$new();
      ctrl = $controller('ClosingCtrl', {$scope: scope});
    }));	

	it('should ...', inject(function() {

		expect(1).toEqual(1);
		
	}));

});