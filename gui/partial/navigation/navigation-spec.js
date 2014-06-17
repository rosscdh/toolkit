describe("NavigationCtrl", function () {
	'use strict';
	var ctrl,
		scope,
		routeParams,
		smartRoutes,
		location,
		modal,
		timeout,
		toaster,
		userService,
		matterService,
		q,
		log;

	/*
	 _   _ _   _ _ _ _   _          __                  _   _                 
	| | | | |_(_) (_) |_(_)_   _   / _|_   _ _ __   ___| |_(_) ___  _ __  ___ 
	| | | | __| | | | __| | | | | | |_| | | | '_ \ / __| __| |/ _ \| '_ \/ __|
	| |_| | |_| | | | |_| | |_| | |  _| |_| | | | | (__| |_| | (_) | | | \__ \
	 \___/ \__|_|_|_|\__|_|\__, | |_|  \__,_|_| |_|\___|\__|_|\___/|_| |_|___/
	                       |___/             
	 */
	function doPromiseResolve(msg){
		return  function(){
		   var deferred = q.defer();
		   deferred.resolve(msg);           
		   return deferred.promise;
		};
	}

	function doPromiseReject(msg){
		return  function(){
		   var deferred = q.defer();
		   deferred.reject(msg);           
		   return deferred.promise;
		};
	}

	function makeFake(fkname, methods){
		var msg  = { message: "This is so great!" };
		var fk = jasmine.createSpyObj(fkname,methods);
		angular.forEach(methods, function(func){
			fk[func].andCallFake(doPromiseResolve(msg));
		});
		return 	fk;
	}
	/*
	var fakeModalPromise = {
            'result' : {
              'then': function(callback) {
                  callback("item1");
              }
            }
    };
    */

    var fakeLog = {
		'log' : function(message){ console.log(message);},
		'debug' : function(message){ console.log(message);}
	};

	// BEFORE

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
	beforeEach(inject(function ($rootScope, $controller, $injector) {
		// Create scope
		scope = $rootScope.$new();

		// Standard mocks
		location = $injector.get('$location');
		timeout = $injector.get('$timeout');
		modal = $injector.get('$modal'); // Bootstrap ui (angular bootstrap ui)
		q = $injector.get('$q');
		log = fakeLog;
		toaster = makeFake('toaster',['pop']);

		// Custom mocks
		routeParams = { 'matterSlug': 'test-matter'};
		smartRoutes = {	//mocking smartRoutes, custom route parser
			'params': function() {
				return { 'matterSlug': 'test-matter', 'itemSlug':'123', 'id': '456' }; 
			}
		};
		matterService = makeFake('matterService',['get','selectMatter','data', 'list']);	  	 
		matterService.data.andCallFake(function(/*param*/){        
		   return {'selected':{'current_user':''}};
		});
		userService = {
			'data': function(){ return { 'current':{'user_class':'lawyer'}};},
			'setCurrent': function(/*p*/){return {};}
		};

		// Create controller
		ctrl = $controller('NavigationCtrl', {
			'$scope': scope,
			'$routeParams': routeParams,
			'smartRoutes': smartRoutes,
			'$location': { 'path': function() {} },
			'$modal': modal,
			'$log': log,
			'$timeout': timeout,
			'toaster': toaster,
			'userService': userService,
			'matterService': matterService
		});
	}));

	/*
	 _____         _       
	|_   _|__  ___| |_ ___ 
	  | |/ _ \/ __| __/ __|
	  | |  __/\__ \ |_\__ \
	  |_|\___||___/\__|___/
	 */
	// USERS
	it("has users object", function () {
		console.log( scope.users.current.user_class );
		expect(scope.users instanceof Object).toBe(true);
		expect(scope.users.current.user_class === 'lawyer').toBe(true);
	});

	// MATTER
	it("has matter object", function () {
		expect(scope.matter instanceof Object).toBe(true);
		expect(scope.matter.selected instanceof Object).toBe(true);
	});

	// Get list of matters
	it('matterService.list success',function(){
		expect(matterService.list).toHaveBeenCalled();
	});

	// Got matter ID from URL
	it('has matter id',function(){
		expect(scope.data.id === '456').toBe(true);
	});
});