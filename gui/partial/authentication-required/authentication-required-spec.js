describe('AuthenticationRequiredCtrl', function() {
    beforeEach(function() {
        module(function($provide) {            
			$provide.constant('API_BASE_URL', '/api/v1/');
            $provide.constant('STATUS_LEVEL', {'OK':0,'WARNING':1,'ERROR':2} );
            $provide.constant('DEBUG_MODE', false);
            $provide.constant('SENTRY_PUBLIC_DSN', 'https://b5a6429d03e2418cbe71cd5a4c9faca6@app.getsentry.com/6287' );
            $provide.constant('INTERCOM_APP_ID', 'ooqtbx99' );
			
			$provide.constant('currentUser',{});
			$provide.constant('matter',{});
        });
		
	});
	beforeEach(module('toolkit-gui'));
    //variables:
	var $rootScope,
	$controller,
	scope,
	ctrl,
	$modalInstance, 
	currentUser,
	matter,
	toaster;

    beforeEach(inject(function($injector) {
	 $rootScope = $injector.get('$rootScope');
	 $controller = $injector.get('$controller');
     scope = $rootScope.$new();
	 currentUser = $injector.get('currentUser');
     matter = $injector.get('matter');
     toaster = $injector.get('toaster');
	 
     $modalInstance = {                    // Create a mock object using spies
        close: jasmine.createSpy('modalInstance.close'),
        dismiss: jasmine.createSpy('modalInstance.dismiss'),
        result: {
          then: jasmine.createSpy('modalInstance.result.then')
        }
      };	  
	  
	  
	  
      ctrl = $controller('AuthenticationRequiredCtrl',{	  
		$scope: scope,
	    $modalInstance:$modalInstance,
	    currentUser:currentUser, 
		matter:matter, 
		toaster:toaster
	  });
	  
	  
    }));	

	it('should ...', inject(function() {

		expect(1).toEqual(1);
		
	}));

});