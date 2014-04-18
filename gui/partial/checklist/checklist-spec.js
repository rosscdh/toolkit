describe('ChecklistCtrl', function() {
    beforeEach(function() {
        module(function($provide) {            
			$provide.constant('API_BASE_URL', '/api/v1/');
            $provide.constant('STATUS_LEVEL', {'OK':0,'WARNING':1,'ERROR':2} );
            $provide.constant('DEBUG_MODE', false);
            $provide.constant('SENTRY_PUBLIC_DSN', 'https://b5a6429d03e2418cbe71cd5a4c9faca6@app.getsentry.com/6287' );
            $provide.constant('INTERCOM_APP_ID', 'ooqtbx99' );
			

			
			$provide.constant('matterCategoryService',{});
			$provide.constant('matterItemService',{});
			$provide.constant('baseService',{});
        });
		
	});
	beforeEach(module('toolkit-gui'));

	var 
	$scope,
	ctrl,
	$rootScope,
	smartRoutes,
	$q,
    matterService;

	
    beforeEach(inject(function($injector, $rootScope, $controller) {
	
	  $rootScope = $injector.get('$rootScope');
	  $controller = $injector.get('$controller');
	  $q = $injector.get('$q');
	  
      $scope = $rootScope.$new();
	  //mocking smartRoutes		
	  smartRoutes = {'params': function() { return { 'matterSlug': 'test-matter' }; }}
	  //mocking matterService       
	  matterService = jasmine.createSpyObj('matterService',['get','selectMatter']);
	  matterService.get.andCallFake(function(param){
		   var deferred = $q.defer();							
		   deferred.resolve({ message: "This is great!" });	           
		   return deferred.promise;		
	  });
	  matterService.selectMatter.andCallFake(function(param){});  
      ctrl = $controller('ChecklistCtrl', {
		  $scope: $scope,
		  $rootScope:$rootScope,
		  $routeParams:{},
		  $location:{},
		  smartRoutes:smartRoutes,
		  ezConfirm:{},
		  toaster:{},
		  $modal:{},
		  baseService:{},
		  matterService:matterService
	  });
    }));	

	// Ceheck objects
	it('should have usdata and call "matterService.get"', function () {
		expect($scope.data instanceof Object).toBe(true);
		expect($scope.data.usdata instanceof Object).toBe(true);
		expect(matterService.get).toHaveBeenCalled();
	});
	
	it('should evaluate smart routes', inject(function() {
		expect(1).toEqual(1);
		expect($scope.data.slug).toEqual('test-matter');
	}));
	
	// selectItem
	it('should set selected checklist item', inject(function() {
		var dte = new Date();

		$scope.selectItem( { 'date_due': dte }, 'My Category' );

		expect($scope.data.selectedItem.date_due).toEqual(dte);
		expect($scope.data.selectedCategory).toEqual('My Category');
	}));
	
	// initialiseMatter
	it('should initialise matter', inject(function() {
		$scope.initialiseMatter( { 'items': [ { 'category': 'My Category', 'slug': '123' } ], 'categories': [ 'My Category' ] } );

		expect($scope.data.categories.length).toEqual(2); // 2 because of the null category
		expect($scope.data.matter.items.length).toEqual(1);
	}));

	//deleteCommentIsEnabled
	it('should determine comment enabled', inject(function() {
		//data.comment
		$scope.data.usdata.current= { 'user_class': 'lawyer' };
		var enabled = $scope.deleteCommentIsEnabled( { 'data': {'comment': 'Hello' } } );
		expect(enabled).toEqual(true); // 2 because of the null category
		
		$scope.data.usdata.current= { 'user_class': 'customer' };
		enabled = $scope.deleteCommentIsEnabled( { 'data': {'comment': {}} } );
		expect(enabled).toEqual(false); // 2 because of the null category
	}));

	// new date selected
	it('should change selected item`s date', inject(function() {
		var dte = new Date();
		// $$scope.data.selectedItem
		$scope.data.selectedItem = { 'date_due': new Date() };
		$scope.data.dueDatePickerDate = dte;

		expect($scope.data.selectedItem.date_due).toEqual(dte);
	}));

	// show catgegory form
	it('should set show category form by index', inject(function() {
		$scope.showEditCategoryForm(1);
		expect($scope.data.showEditCategoryForm).toEqual(1);
	}));
	
	//matterService.get success
	it('if matterService.get performed successfully -$scope.initialiseMatter should called', inject(function() {
	    spyOn($scope,'initialiseMatter');
		spyOn($scope,'initializeActivityStream');
	    $scope.$apply();//makes promise.resolve to fire
		expect($scope.initialiseMatter).toHaveBeenCalled();
		expect($scope.initializeActivityStream).toHaveBeenCalled();
	}));
	
});
//matterService.get failure
describe('ChecklistCtrl', function() {
    beforeEach(function() {
        module(function($provide) {            
			$provide.constant('API_BASE_URL', '/api/v1/');
            $provide.constant('STATUS_LEVEL', {'OK':0,'WARNING':1,'ERROR':2} );
            $provide.constant('DEBUG_MODE', false);
            $provide.constant('SENTRY_PUBLIC_DSN', 'https://b5a6429d03e2418cbe71cd5a4c9faca6@app.getsentry.com/6287' );
            $provide.constant('INTERCOM_APP_ID', 'ooqtbx99' );
			

			
			$provide.constant('matterCategoryService',{});
			$provide.constant('matterItemService',{});
			$provide.constant('baseService',{});
        });
		
	});
	beforeEach(module('toolkit-gui'));

	var 
	$scope,
	ctrl,
	$rootScope,
	smartRoutes,
	$q,
	toaster,
    matterService;

	
    beforeEach(inject(function($injector, $rootScope, $controller) {
	
	  $rootScope = $injector.get('$rootScope');
	  $controller = $injector.get('$controller');
	  $q = $injector.get('$q');
	  
      $scope = $rootScope.$new();
	  //mocking smartRoutes		
	  smartRoutes = {'params': function() { return { 'matterSlug': 'test-matter' }; }}
	  //mocking matterService       
	  matterService = jasmine.createSpyObj('matterService',['get','selectMatter']);
	  matterService.get.andCallFake(function(param){
		   var deferred = $q.defer();							
		   deferred.reject({ message: "This is great!" });	           
		   return deferred.promise;		
	  });
	  
	  toaster  = jasmine.createSpyObj('toaster',['pop']);
	  toaster.pop.andCallFake(function(param1,param2,param3){});
	  
	  matterService.selectMatter.andCallFake(function(param){});  
      ctrl = $controller('ChecklistCtrl', {
		  $scope: $scope,
		  $rootScope:$rootScope,
		  $routeParams:{},
		  $location:{},
		  smartRoutes:smartRoutes,
		  ezConfirm:{},
		  toaster:toaster,
		  $modal:{},
		  baseService:{},
		  matterService:matterService
	  });
    }));

	
	//matterService.get success
	it('if matterService.get performed successfully -$scope.initialiseMatter should called', inject(function() {
        
	    $scope.$apply();//makes promise.resolve to fire
        expect(toaster.pop.mostRecentCall.args[0]).toBe('error');
	}));	
});