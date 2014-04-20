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
	ezConfirm,
	matterItemService,
	participantService,
	matterCategoryService,
    matterService;

	
    beforeEach(inject(function($injector, $rootScope, $controller) {
	
	  $rootScope = $injector.get('$rootScope');
	  $controller = $injector.get('$controller');
	  $q = $injector.get('$q');
	  
      $scope = $rootScope.$new();
	  
	  //MOCKS
	  //mocking smartRoutes		
	  smartRoutes = {'params': function() { return { 'matterSlug': 'test-matter', itemSlug:'123' }; }}
	  //mocking matterService       
	  matterService = jasmine.createSpyObj('matterService',['get','selectMatter']);
	  matterService.get.andCallFake(function(param){
		   var deferred = $q.defer();							
		   deferred.resolve({ message: "This is great!" });	           
		   return deferred.promise;		
	  });
	  matterItemService  = jasmine.createSpyObj('matterItemService',['create','delete','update']);
	  matterItemService.create.andCallFake(function(param){
		   var deferred = $q.defer();							
		   deferred.resolve({ message: "This is great!" });	           
		   return deferred.promise;		  
	  });
	  matterItemService.delete.andCallFake(function(param){
		   var deferred = $q.defer();							
		   deferred.resolve({ message: "This is so great!" });	           
		   return deferred.promise;		  
	  });
	  matterItemService.update.andCallFake(function(param){
		   var deferred = $q.defer();							
		   deferred.resolve({ message: "This is so great!" });	           
		   return deferred.promise;		  
	  });	
	  
	  baseService = jasmine.createSpyObj('baseService',['loadObjectByUrl']);
	  baseService.loadObjectByUrl.andCallFake(function(param){
		   var deferred = $q.defer();							
		   deferred.resolve({ message: "This is great!" });	           
		   return deferred.promise;		  	  
	  });
	  
	  toaster = jasmine.createSpyObj('toaster',['pop']);
	  toaster.pop.andCallFake(function(param){});
	  
	  ezConfirm = jasmine.createSpyObj('ezConfirm',['create']);
	  ezConfirm.create.andCallFake(function(param,param1,callbck){           
		   callbck()	  
	  });
	  
	  participantService = jasmine.createSpyObj('participantService',['getByURL']);
	  participantService.getByURL.andCallFake(function(param){
		   var deferred = $q.defer();							
		   deferred.resolve({ message: "This is great!" });	           
		   return deferred.promise;	  
	  });
	  matterCategoryService = jasmine.createSpyObj('matterCategoryService',['create','delete','update']);
	  matterCategoryService.create.andCallFake(function(param){
		   var deferred = $q.defer();							
		   deferred.resolve({ message: "This is great!" });	           
		   return deferred.promise;	  
	  });
	  matterCategoryService.delete.andCallFake(function(param){
		   var deferred = $q.defer();							
		   deferred.resolve({ message: "This is great!" });	           
		   return deferred.promise;	  
	  });
	  matterCategoryService.update.andCallFake(function(param){
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
		  ezConfirm:ezConfirm,
		  toaster:toaster,
		  $modal:{},
		  baseService: baseService,
		  matterService:matterService,
		  matterItemService:matterItemService,
		  matterCategoryService:matterCategoryService,
		  participantService:participantService		  
	  });
    }));	

	  
	// Check objects
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
		//should also sselect item
		expect(angular.equals($scope.data.selectedItem,{category: 'My Category', slug: '123'})).toBeTruthy();
	}));
	
    // initialiseMatter if error 
	it('should initialise matter without "matter.categories" parameter', inject(function() {
		$scope.initialiseMatter( {items:[]} );

		//should also sselect item
		expect(toaster.pop).toHaveBeenCalled();
	}));
	
	//$scope.submitNewItem
	it('should',function() {
	    $scope.data.newItemName = 'newItem'
		var category = {name:'ooo',items:[]};
		expect(angular.equals([],category.items)).toBeTruthy();
		$scope.submitNewItem(category);
		$scope.$apply();
		expect(angular.equals([{message: 'This is great!'}],category.items)).toBeTruthy();
	})
	
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
	
	// show catgegory form 2
	it('if showEditCategoryForm  already set', inject(function() {
	    $scope.data.showEditCategoryForm = 1;
		$scope.showEditCategoryForm(1);
		expect($scope.data.showEditCategoryForm).toBe(null);
	}));
	
	//matterService.get success
	it('if matterService.get performed successfully -$scope.initialiseMatter should called', inject(function() {
	    spyOn($scope,'initialiseMatter');
		spyOn($scope,'initializeActivityStream');
	    $scope.$apply();//makes promise.resolve to fire
		expect($scope.initialiseMatter).toHaveBeenCalled();
		expect($scope.initializeActivityStream).toHaveBeenCalled();
	}));
	
	//on
	it('after itemSelected event fired, $scope.selectItem should called',function() {
	   spyOn($scope,'selectItem');
	   $scope.$broadcast('itemSelected',{category:'someCategory'});
	   expect($scope.selectItem).toHaveBeenCalled();
	});
	
	//on 2
	it('after itemSelected event fired, $scope.selectItem should called with found category',function() {
	   spyOn($scope,'selectItem');
	   $scope.data.categories.push({name:'someCategory'})
	   $scope.$broadcast('itemSelected',{category:'someCategory'});
	   expect($scope.selectItem).toHaveBeenCalledWith({category:'someCategory'},{ name : 'someCategory' });	
	});
	
	//$scope.loadItemDetails 
	it('$scope.loadItemDetails "item.latest_revision" must be populated with response data',function(){
	    var item = {latest_revision:{url:'somerevision'}};
		$scope.loadItemDetails(item);
		expect(baseService.loadObjectByUrl).toHaveBeenCalled();
		$scope.$apply();
		expect(item.latest_revision).toEqual({ message: "This is great!" });
	});
	
	//$scope.deleteItem
	it('$scope.deleteItem',function(){
	    $scope.data.selectedItem = {};
	    $scope.deleteItem();
		expect(ezConfirm.create).toHaveBeenCalled();
	});	
	
	//$scope.deleteItem
	it('$scope.deleteItem -"ezConfirm.create" should been called',function(){
	    $scope.data.selectedItem = {name:'some'};
		$scope.data.selectedCategory={items :[$scope.data.selectedItem]};
	    $scope.deleteItem();
		expect(ezConfirm.create).toHaveBeenCalled();
		expect(matterItemService.delete).toHaveBeenCalled();
		$scope.$apply();
		expect($scope.data.selectedItem).toBe(null)
	});	
	
	//$scope.showAddItemForm
	it('$scope.data.showAddForm NOT equal to index parameter, $scope.data.showAddForm  should upadted respectviely',function(){
	    $scope.data.showAddForm = 2;
		$scope.showAddItemForm(1);
		expect($scope.data.showAddForm).toBe(1)
	})
	
	it(' $scope.data.showAddForm is equal to index parameter $scope.data.showAddForm should become NULL',function(){
	    $scope.data.showAddForm = 1;
		$scope.showAddItemForm(1);
		expect($scope.data.showAddForm).toBe(null)
	})	
	
	//$scope.saveSelectedItem
	it('$scope.saveSelectedItem',function(){
	    $scope.data.selectedItem = {};
	    $scope.saveSelectedItem();
		expect(matterItemService.update).toHaveBeenCalled();
	});
	
	//$scope.getParticipantByUrl - 1
    it('$scope.getParticipantByUrl when url speified',function(){
		$scope.getParticipantByUrl('someUrl');
		expect(angular.equals($scope.data.loadedParticipants,{someUrl:{}})).toBeTruthy();
		$scope.$apply();
		expect(angular.equals($scope.data.loadedParticipants['someUrl'],{ message: "This is great!" })).toBeTruthy();		
	});	
	
	//$scope.getParticipantByUrl - 2
    it('$scope.getParticipantByUrl when NO url speified',function(){
		var result = $scope.getParticipantByUrl();
		expect(result).toEqual('');
	});	
	
	//$scope.getParticipantByUrl - 3
    it('$scope.getParticipantByUrl when "loadedParticipants[participanturl]" already has some data',function(){
	   var participanturl = 'someUrl';
	   $scope.data.loadedParticipants ={'someUrl':'some data'};
		var result = $scope.getParticipantByUrl(participanturl);
		expect(result).toEqual('some data');
	});	
   
    //$scope.submitNewCategory
	it('$scope.submitNewCategory',function(){
	    $scope.data.categories = ['something']
	    $scope.data.newCatName = 'shlomo';
		$scope.submitNewCategory();
		$scope.$apply();
		expect(angular.equals($scope.data.categories[1],{name: 'shlomo', items: []})).toBeTruthy();
	})
	
	it('$scope.deleteCategory',function(){
	    $scope.data.categories = ['shlomo','momo']
		$scope.deleteCategory('shlomo');
		$scope.$apply();
		expect(angular.equals($scope.data.categories,['momo'])).toBeTruthy();
	});
	
	it('$scope.deleteCategory if cat is selected',function(){
	    $scope.data.categories = ['shlomo','momo'];
		$scope.data.selectedCategory = 'shlomo';
		$scope.deleteCategory('shlomo');
		$scope.$apply();
		expect($scope.data.selectedItem).toBe(null);
	});	
	
	//$scope.editCategory
	it('calling $scope.editCategory should change the param category name to $scope.data.newCategoryName', function(){
	    $scope.data.newCategoryName = 'Sasha';
		var cat ={name:'shlomo'};
		$scope.editCategory(cat);
		$scope.$apply();
		expect(cat.name).toBe('Sasha');
	});
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
    matterService,
	baseService,
	ezConfirm,
	participantService,
	matterCategoryService,
	matterItemService;

	
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
		   deferred.reject({ message: "This is not so great!" });	           
		   return deferred.promise;		
	  });
	  matterItemService  = jasmine.createSpyObj('matterItemService',['create','delete','update']);
	  matterItemService.create.andCallFake(function(param){
		   var deferred = $q.defer();							
		   deferred.reject({ message: "This is not so great!" });	           
		   return deferred.promise;		  
	  });
	  
	  matterItemService.delete.andCallFake(function(param){
		   var deferred = $q.defer();							
		   deferred.reject({ message: "This is not so great!" });	           
		   return deferred.promise;		  
	  });
	  matterItemService.update.andCallFake(function(param){
		   var deferred = $q.defer();							
		   deferred.reject({ message: "This is not so great!" });	           
		   return deferred.promise;		  
	  });	  
	  baseService = jasmine.createSpyObj('baseService',['loadObjectByUrl']);
	  baseService.loadObjectByUrl.andCallFake(function(param){
		   var deferred = $q.defer();							
		   deferred.reject({ message: "This is great!" });	           
		   return deferred.promise;		  	  
	  });	  
	  toaster  = jasmine.createSpyObj('toaster',['pop']);
	  toaster.pop.andCallFake(function(param1,param2,param3){});
	  ezConfirm = jasmine.createSpyObj('ezConfirm',['create']);
	  ezConfirm.create.andCallFake(function(param,param1,callbck){           
		   callbck()	  
	  });
	  
	  participantService = jasmine.createSpyObj('participantService',['getByURL']);
	  participantService.getByURL.andCallFake(function(param){
		   var deferred = $q.defer();							
		   deferred.reject({ message: "This is bad!" });	           
		   return deferred.promise;	  
	  });
	  matterCategoryService = jasmine.createSpyObj('matterCategoryService',['create','delete','update']);
	  matterCategoryService.create.andCallFake(function(param){
		   var deferred = $q.defer();							
		   deferred.reject({ message: "This is not great!" });	           
		   return deferred.promise;	  
	  });
	  matterCategoryService.delete.andCallFake(function(param){
		   var deferred = $q.defer();							
		   deferred.reject({ message: "This is not great!" });	           
		   return deferred.promise;	  
	  }); 
	  matterCategoryService.update.andCallFake(function(param){
		   var deferred = $q.defer();							
		   deferred.reject({ message: "This is NOT great!" });	           
		   return deferred.promise;	  
	  }); 	  
	  matterService.selectMatter.andCallFake(function(param){});  
      ctrl = $controller('ChecklistCtrl', {
		  $scope: $scope,
		  $rootScope:$rootScope,
		  $routeParams:{itemSlug:'111'},
		  $location:{},
		  smartRoutes:smartRoutes,
		  ezConfirm:ezConfirm,
		  toaster:toaster,
		  $modal:{},
		  baseService:baseService,
		  matterService:matterService,
		  matterItemService:matterItemService,
		  matterCategoryService:matterCategoryService,		  
		  participantService:participantService
	  });
    }));

	
	//matterService.get failure
	it('if matterService.get performed successfully -$scope.initialiseMatter should called', inject(function() {
        
	    $scope.$apply();//makes promise.resolve to fire
        expect(toaster.pop.mostRecentCall.args[0]).toBe('error');
	}));
	
	//$scope.submitNewItem  failure
	it('should',function() {
	    $scope.data.newItemName = 'newItem'
		var category = {name:'ooo',items:[]};
		expect(angular.equals([],category.items)).toBeTruthy();
		$scope.submitNewItem(category);
		$scope.$apply();
		expect(toaster.pop.mostRecentCall.args[0]).toBe('error');
	});
	
	//$scope.loadItemDetails   failure
	it('$scope.loadItemDetails should call the toaster',function(){
	    var item = {latest_revision:{url:'somerevision'}};
		$scope.loadItemDetails(item);
		expect(baseService.loadObjectByUrl).toHaveBeenCalled();
		$scope.$apply();
		expect(toaster.pop.mostRecentCall.args[0]).toBe('error');
	});
	
	it('$scope.deleteItem',function(){
	    $scope.data.selectedItem = {};
	    $scope.deleteItem();
		expect(ezConfirm.create).toHaveBeenCalled();
		$scope.$apply();
		expect(toaster.pop.mostRecentCall.args[0]).toBe('error');		
	});
	//$scope.saveSelectedItem
	it('$scope.saveSelectedItem',function(){
	    $scope.data.selectedItem = {};
	    $scope.saveSelectedItem();
		$scope.$apply();
		expect(toaster.pop.mostRecentCall.args[0]).toBe('error');
	});
	//$scope.getParticipantByUrl failure
    it('$scope.getParticipantByUrl when url speified',function(){
		$scope.getParticipantByUrl('someUrl');
		expect(angular.equals($scope.data.loadedParticipants,{someUrl:{}})).toBeTruthy();
		$scope.$apply();
		expect(toaster.pop.mostRecentCall.args[0]).toBe('error');		
	});	
    //$scope.submitNewCategory failure
	it('$scope.submitNewCategory',function(){
	    $scope.data.categories = ['something']
	    $scope.data.newCatName = 'shlomo';
		$scope.submitNewCategory();
		$scope.$apply();
		expect(toaster.pop.mostRecentCall.args[0]).toBe('error');	
	});
	
	it('$scope.deleteCategory faiure',function(){
	    $scope.data.categories = ['shlomo','momo'];
		$scope.data.selectedCategory = 'shlomo';
		$scope.deleteCategory('shlomo');
		$scope.$apply();
		expect(toaster.pop.mostRecentCall.args[2]).toBe("Unable to delete category");	
	});	

	//$scope.editCategory failure
	it('calling $scope.editCategory should change the param category name to $scope.data.newCategoryName', function(){
	    $scope.data.newCategoryName = 'Sasha';
		var cat ={name:'shlomo'};
		$scope.editCategory(cat);
		$scope.$apply();
		expect(toaster.pop.mostRecentCall.args[2]).toBe("Unable to edit category");
	});
});