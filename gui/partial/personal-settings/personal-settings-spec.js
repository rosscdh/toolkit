describe("PersonalSettingsCtrl", function () {
	'use strict';
	var ctrl, scope, modalInstance;

	// CONSTANTS
	beforeEach(function() {
		module(function($provide) {      
			$provide.constant('API_BASE_URL', '/api/v1/');
			$provide.constant('STATUS_LEVEL', {'OK':0,'WARNING':1,'ERROR':2} );
			$provide.constant('DEBUG_MODE', false);
			$provide.constant('SENTRY_PUBLIC_DSN', 'https://b5a6429d03e2418cbe71cd5a4c9faca6@app.getsentry.com/6287' );
			$provide.constant('INTERCOM_APP_ID', 'ooqtbx99' );
			$provide.constant('pusher_api_key', '60281f610bbf5370aeaa' );
		});
	});

	// INITIATE APP
	beforeEach(module('toolkit-gui'));

	// INITIATE Controller
	beforeEach(inject(function ($rootScope, $controller) {
		// Create scope
		scope = $rootScope.$new();

		// modal instance, create method spys
		modalInstance = {
			'close': jasmine.createSpy('modalInstance.close'),
			'dismiss': jasmine.createSpy('modalInstance.dismiss'),
			'result': {
				'then': jasmine.createSpy('modalInstance.result.then')
			}
		};

		// Create controller
		ctrl = $controller('PersonalSettingsCtrl', {
			'$scope': scope,
			'$modalInstance': modalInstance
		});
	}));

	// Tests
	it("has cancel method", function () {
		expect(scope.cancel instanceof Function).toBe(true);
	});
});