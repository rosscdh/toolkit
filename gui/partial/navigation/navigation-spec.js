describe('NavigationCtrl', function() {
    function doPromiseResolve(msg){
	    return  function(){
		   var deferred = $q.defer();							
		   deferred.resolve(msg);     
		   return deferred.promise;
        }		   
	}
	function makeFake(fkname, methods){
	    var msg  = { message: "This is so great!" };
	    var fk = jasmine.createSpyObj(fkname,methods);
	    angular.forEach(methods, function(func, key){
			fk[func].andCallFake(doPromiseResolve(msg));
        });
	    return 	fk;	
	}
    function doPromiseReject(msg){
	    return  function(){
		   var deferred = $q.defer();							
		   deferred.reject(msg);           
		   return deferred.promise;
        }		   
	}	
	function createContrl(){
	
	  
      ctrl = $controller('NavigationCtrl', {
	    $scope: $scope,
		$routeParams:$routeParams,
		smartRoutes:smartRoutes,
		$location:$location,
		$modal:$modal,
		$log:$log,
		toaster:toaster,
		userService:userService,
		matterService:matterService
	  });
      	 
	}
	
    beforeEach(function() {
        module(function($provide) {            
			$provide.constant('API_BASE_URL', '/api/v1/');
            $provide.constant('STATUS_LEVEL', {'OK':0,'WARNING':1,'ERROR':2} );
            $provide.constant('DEBUG_MODE', false);
            $provide.constant('SENTRY_PUBLIC_DSN', 'https://b5a6429d03e2418cbe71cd5a4c9faca6@app.getsentry.com/6287' );
            $provide.constant('INTERCOM_APP_ID', 'ooqtbx99' );
        });
		
	});
	beforeEach(module('toolkit-gui'));

	var 
	$scope,
	$routeParams,
	smartRoutes,
	$location,
	$modal,
	$log,
	toaster,
	userService,
	matterService,
	$q,
	ctrl;
  //$routeParams, smartRoutes, $location, $modal, $log, toaster, userService, matterService
    beforeEach(inject(function($rootScope, $controller, $injector) {
      $scope = $rootScope.$new();
	  matterService = makeFake('matterService',['list','data']);	
	  $routeParams = {id:'1'};	
	  smartRoutes = makeFake('smartRoutes',['params']);	
	  $location = makeFake('$location',['path']);	
	  $modal= makeFake('$modal',['path']);
	  $log= makeFake('$log',['path']);
	  toaster= makeFake('toaster',['pop']);
	  userService= makeFake('userService',['data']);
	  $q = $injector.get('$q');	  
    }));	

	// Check objects
	it('should have data', function () {
	    createContrl();
		expect($scope.data instanceof Object).toBe(true);
	});

	
	it('matterService.list should called when controller initiated',function(){
	   createContrl();
	   expect(matterService.list).toHaveBeenCalled();
	   $scope.$apply();
	   expect(angular.equals({message: 'This is so great!'},$scope.data.matterlist)).toBeTruthy()
	});
	
	it('matterService.list failure',function(){
	   matterService.list.andCallFake(doPromiseReject({message:'This is NOT great!'}))	   
	   createContrl();
	   expect(matterService.list).toHaveBeenCalled();
	   $scope.$apply();
	   expect(toaster.pop).toHaveBeenCalled()
	});
	
	it('$scope.isActive should call location.path',function(){
	    $location.path.andReturn('some')
	    createContrl();
		$scope.isActive();
		expect($location.path).toHaveBeenCalled()
	});
});