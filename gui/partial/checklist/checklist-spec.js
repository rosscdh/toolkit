
describe('Controller: Checklist', function() {
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
	$modal,
	userService,
	searchService,
	userService, 
	AuthenticationRequiredCtrl,
	$modalInstance,	
    matterService;

	
    beforeEach(inject(function($injector) {
	  
	  $rootScope = $injector.get('$rootScope');
	  $controller = $injector.get('$controller');
	  $q = $injector.get('$q');
	  $timeout = $injector.get('$timeout');
      $scope = $rootScope.$new();
	  //AuthenticationRequiredCtrl = $injector.get('AuthenticationRequiredCtrl');
	  //MOCKS
	  var msg  = { message: "This is so great!" };
	  //mocking smartRoutes		
	  smartRoutes = {'params': function() { return { 'matterSlug': 'test-matter', itemSlug:'123' }; }}
	  //mocking matterService       
  
	  
	  matterItemService  = makeFake('matterItemService',[
	  'create',
	  'delete',
	  'update',
	  'uploadRevision',
	  'updateRevision',
	  'deleteRevision',
	  'loadRevision',
	  'remindRevisionRequest',
	  'deleteRevisionRequest',
	  'remindRevisionReview',
	  'deleteRevisionReviewRequest',	  
	  'uploadRevisionFile'	  
	  ]);	  
	  matterItemService.deleteRevisionRequest.andCallFake(doPromiseResolve({ is_requested: "This is so great!" }));
	  
	  baseService = makeFake('baseService',['loadObjectByUrl']);	  
	  
	  
	  toaster = makeFake('toaster',['pop']);
	  
	  
	  ezConfirm = jasmine.createSpyObj('ezConfirm',['create']);
	  ezConfirm.create.andCallFake(function(param,param1,callbck){           
		   callbck()	  
	  });
	  
	  participantService = makeFake('participantService',['getByURL']);	  
	  matterCategoryService = makeFake('matterCategoryService',['create','delete','update']); 

	  matterService = makeFake('matterService',['get','selectMatter','data']);	  	 
	  matterService.data.andCallFake(function(param){           
		   return {selected:{current_user:''}};	
	  });	

        
      $modalInstance = {                    // Create a mock object using spies
        close: jasmine.createSpy('modalInstance.close'),
        dismiss: jasmine.createSpy('modalInstance.dismiss'),
        result: {
          then: jasmine.createSpy('modalInstance.result.then')
        }
      };	  

	  $modal = jasmine.createSpyObj('$modal',['open'])
	  $modal.open.andCallFake(function(param){	  
	    /*
	    'templateUrl': '/static/ng/partial/authentication-required/authentication-required.html',
        'controller': 'AuthenticationRequiredCtrl',
        'backdrop': 'static',
        'resolve'	  
	    */
		//$controller(param.controller,{$scope: $scope, $modalInstance:$modalInstance, matter:{},toaster:{}})
		
		
	    return {
		 result: function(){
		   var deferred = $q.defer();							
		   deferred.resolve({ responsible_party: "This is great!" });	           
		   return deferred.promise;	  		 
		 }()
		}
	  }); 
	  
	  userService = {data:function(){return { current:{user_class:'lawyer'}};},setCurrent:function(p){return {};}};
	  searchService = {data:function(){return {};}};
	  activityService = makeFake('matterCategoryService',['itemstream']);
	 
	  
      ctrl = $controller('ChecklistCtrl', {
		  $scope: $scope,
		  $rootScope:$rootScope,
		  $routeParams:{},
		  $location:{},
		  smartRoutes:smartRoutes,
		  ezConfirm:ezConfirm,
		  toaster:toaster,
		  $modal:$modal,
		  baseService: baseService,
		  matterService:matterService,
		  matterItemService:matterItemService,
		  matterCategoryService:matterCategoryService,
		  participantService:participantService,		  
		  searchService:searchService,
		  activityService:activityService,
		  userService:userService		  
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
        var item =  { 'category': 'My Category', 'slug': '123' };
        var cat =  'My Category';
		$scope.initialiseMatter( { 'items': [ item ], 'categories': [ cat ] } );

		expect($scope.data.categories.length).toEqual(2); // 2 because of the null category
		expect($scope.data.matter.items.length).toEqual(1);
		//should also select item
        $scope.selectItem( item , cat );
		expect(angular.equals($scope.data.selectedItem, item)).toBeTruthy();
	}));
	
    // initialiseMatter if error 
	it('should initialise matter without "matter.categories" parameter', inject(function() {
		$scope.initialiseMatter( {items:[]} );

		//should also sselect item
		expect(toaster.pop).toHaveBeenCalled();
	}));
	
	//$scope.submitNewItem
	it('$scope.submitNewItem should return result as exected',function() {
	    $scope.data.newItemName = 'newItem'
		var category = {name:'ooo',items:[]};
		expect(angular.equals([],category.items)).toBeTruthy();
		$scope.submitNewItem(category);
		$scope.$apply();
		expect(angular.equals([{message: 'This is so great!'}],category.items)).toBeTruthy();
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
	
	//$scope.loadItemDetails KKKK 
	it('$scope.loadItemDetails "item.latest_revision" must be populated with response data',function(){
	    var item = {latest_revision:{url:'somerevision'}};
		$scope.loadItemDetails(item);
		expect(baseService.loadObjectByUrl).toHaveBeenCalled();
		$scope.$apply();
		expect(item.latest_revision).toEqual({ message: "This is so great!" });
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
    it('$scope.getParticipantByUrl when url specified',function(){
		$scope.getParticipantByUrl('someUrl');
		expect(angular.equals($scope.data.loadedParticipants,{someUrl:{}})).toBeTruthy();
		$scope.$apply();
		expect(angular.equals($scope.data.loadedParticipants['someUrl'],{ message: "This is so great!" })).toBeTruthy();		
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
	
	//$scope.processUpload
	it('$scope.processUpload - $scope.data.showPreviousRevisions should become false', function(){
	   $scope.processUpload([],{slug:1});
	   $scope.$apply();
	   expect($scope.data.showPreviousRevisions).toBe(false);
	});
	
	it('$scope.saveLatestRevision sholud call "matterItemService.updateRevision"', function(){
		$scope.data.selectedItem = {latest_revision:'something'};
		$scope.saveLatestRevision();
		expect(matterItemService.updateRevision).toHaveBeenCalled();
	});
	
	//$scope.deleteLatestRevision
	it('$scope.deleteLatestRevision "matterItemService.deleteRevision" should been called',function(){
	    $scope.data.selectedItem = {latest_revision:{revisions:['something']},slug:'slugof'};
	    $scope.deleteLatestRevision();
		expect(matterItemService.deleteRevision).toHaveBeenCalled();
		$scope.$apply();
		
		expect(matterItemService.loadRevision).toHaveBeenCalledWith('test-matter','slugof','something');
	});

	it('$scope.deleteLatestRevision - if no reveisions there...',function(){
	    $scope.data.selectedItem = {latest_revision:{revisions:[]},slug:'slugof'};
	    $scope.deleteLatestRevision();
		expect(matterItemService.deleteRevision).toHaveBeenCalled();
		$scope.$apply();
		
		expect(matterItemService.loadRevision).not.toHaveBeenCalled();
		expect($scope.data.selectedItem.latest_revision).toBe(null)
	});	
	
    //$scope.deleteLatestRevision -matterItemService.loadRevision faliure
	
	it('$scope.deleteLatestRevision "matterItemService.loadRevision" failed',function(){
        matterItemService.loadRevision.andCallFake(function(param){	  
		   var deferred = $q.defer();							
		   deferred.reject({ message: "This is disgusting!" });	           
		   return deferred.promise;		
        });	
	    $scope.data.selectedItem = {latest_revision:{revisions:['something']},slug:'slugof'};
	    $scope.deleteLatestRevision();
		expect(matterItemService.deleteRevision).toHaveBeenCalled();
		$scope.$apply();
		
		expect(matterItemService.loadRevision).toHaveBeenCalledWith('test-matter','slugof','something');
		expect(toaster.pop.mostRecentCall.args[2]).toBe('Unable to set new current revision');	
	});	
	
	// $scope.loadPreviousRevisions
	it('$scope.loadPreviousRevisions - if  "previousRevisions:null" is  null -$scope.data.selectedItem.previousRevisions should become []',function(){
	    $scope.data.selectedItem = {previousRevisions:null,latest_revision:{revisions:[]}};
		$scope.loadPreviousRevisions();
		expect(angular.equals($scope.data.selectedItem.previousRevisions,[])).toBeTruthy();
	});	
	
	it('$scope.loadPreviousRevisions, latest_revision.revisions is array',function(){
	    $scope.data.selectedItem = {previousRevisions:null,latest_revision:{revisions:['something']}};
		$scope.loadPreviousRevisions();
		expect(angular.equals($scope.data.selectedItem.previousRevisions,[])).toBeTruthy();
		expect(matterItemService.loadRevision.callCount).toBe(1);//if there one item it should be called once
		$scope.$apply();
		expect(angular.equals($scope.data.selectedItem.previousRevisions[0],{message: 'This is so great!'})).toBeTruthy();
	});
	
	it('$scope.loadPreviousRevisions, if matterItemService.loadRevision fails',function(){
        matterItemService.loadRevision.andCallFake(function(param){	  
		   var deferred = $q.defer();							
		   deferred.reject({ message: "This is disgusting!" });	           
		   return deferred.promise;		
        });		
	    $scope.data.selectedItem = {previousRevisions:null,latest_revision:{revisions:['something']}};
		$scope.loadPreviousRevisions();
		expect(angular.equals($scope.data.selectedItem.previousRevisions,[])).toBeTruthy();
		expect(matterItemService.loadRevision.callCount).toBe(1);//if there one item it should be called once
		$scope.$apply();
        expect(toaster.pop.mostRecentCall.args[2]).toBe("Unable to load previous revision");
	});	
	
    it('$scope.requestRevision',function(){
	    $scope.data.matter = {current_user:{}};
		
	    $modal.open.andCallFake(function(param){	  
  
			var matter = param.resolve.matter();
			var currentUser = param.resolve.currentUser();
			var participants = param.resolve.participants();
			var checklistItem = param.resolve.checklistItem();			
			$controller(param.controller,//RequestrevisionCtrl
			{
				$scope: $scope,
				$modalInstance:$modalInstance,
				participants:participants,
				currentUser:currentUser,
				matter:matter,
				checklistItem:checklistItem
			});
		    
		    
			return {
				result: function(){
				   var deferred = $q.defer();							
				   deferred.resolve({ responsible_party: "This is great!" });	           
				   return deferred.promise;	  		 
				}()
			}
	    }); 	
	    var item  ={responsible_party:'some responsible_party'}
		$scope.requestRevision(item);
		$scope.$apply();
		expect(item.responsible_party).toBe('This is great!')
	});

	it('$scope.remindRevisionRequest success should trigger toaster',function(){
	    var item = {slug:{}};
		$scope.remindRevisionRequest(item);
		$scope.$apply();
		expect(toaster.pop.mostRecentCall.args[2]).toBe("The user has been successfully informed.");
	});


	it('$scope.remindRevisionRequest error should also trigger toaster',function(){
	    matterItemService.remindRevisionRequest.andCallFake(function(param){
		   var deferred = $q.defer();							
		   deferred.reject({ message: "This is not so great!" });	           
		   return deferred.promise;	   
	    });	
	    var item = {slug:{}};
		$scope.remindRevisionRequest(item);
		$scope.$apply();
		expect(toaster.pop.mostRecentCall.args[2]).toBe("Unable to remind the participant.");
	});
    
	it('$scope.deleteRevisionRequest success'	,function(){
	    var item = {slug:{},is_requested:''};
	    $scope.deleteRevisionRequest(item);
		$scope.$apply();
        expect(item.is_requested).toBe('This is so great!')		
	});

	it('$scope.deleteRevisionRequest error'	,function(){
	    matterItemService.deleteRevisionRequest.andCallFake(function(param){
		   var deferred = $q.defer();							
		   deferred.reject({ is_requested: "This is not so great!" });	           
		   return deferred.promise;	  
	    });	
	    var item = {slug:{},is_requested:''};
	    $scope.deleteRevisionRequest(item);
		$scope.$apply();
        expect(toaster.pop.mostRecentCall.args[2]).toBe("Unable to delete the revision request.");	
	});
	
	it('$scope.showRevisionDocument' 	,function(){
	    $modal.open.andCallFake(function(param){	  
  
			var matter = param.resolve.matter();						
			var checklistItem = param.resolve.checklistItem();
			var revision = param.resolve.revision();
			/*'$scope',
			'$modalInstance',
			'toaster',
			'matterItemService',
			'matter',
			'checklistItem',
			'revision',*/			
			$controller(param.controller,//ViewDocumentCtrl
			{
				$scope: $scope,
				$modalInstance:$modalInstance,
				toaster:{},
				matterItemService:{},
				matter:matter,
				checklistItem:checklistItem,
				revision:revision
			});
		    
		    
			return {
				result: function(){
				   var deferred = $q.defer();							
				   deferred.resolve({ responsible_party: "This is great!" });	           
				   return deferred.promise;	  		 
				}()
			}
	    }); 	
	    $scope.data.selectedItem = {};
		$scope.showRevisionDocument();
	});
	
	it('$scope.requestReview -  should add new reviewer to "reviewers"',function(){
	    $scope.data.matter = {participants:[]};
		var revision = {reviewers:[{reviewer:{username:'vasia'}}]};
		var new_reviewer = {reviewer:{username:'shlomo'}};
		
	    $modal.open.andCallFake(function(param){	  
            
			var participants = param.resolve.participants();						
			var currentUser = param.resolve.currentUser();
			var matter = param.resolve.matter();
			var checklistItem = param.resolve.checklistItem();
			var revision = param.resolve.revision();			
			$controller(param.controller,//RequestreviewCtrl
			{
				$scope: $scope,
				$modalInstance:$modalInstance,
				participants:participants,
				currentUser:currentUser,
				matter:matter,
				checklistItem:checklistItem,
				revision:revision
			});
		    
		    
			return {
				result: function(){
				   var deferred = $q.defer();							
				   deferred.resolve(new_reviewer);	           
				   return deferred.promise;	  		 
				}()
			}
	    }); 	
	    
		$scope.requestReview(revision);
		expect( $modal.open).toHaveBeenCalled();
		$scope.$apply();	        
		expect(angular.equals(revision.reviewers,[{reviewer:{username:'vasia'}},new_reviewer])).toBeTruthy()
	});

	it('$scope.requestReview -  if  "reviewers" inside revision is  null it should became empty array',function(){
	    $scope.data.matter = {participants:[]};
		var revision = {reviewers:null};
		var new_reviewer = {reviewer:{username:'shlomo'}};
		
	    $modal.open.andCallFake(function(param){	  
            
			var participants = param.resolve.participants();						
			var currentUser = param.resolve.currentUser();
			var matter = param.resolve.matter();
			var checklistItem = param.resolve.checklistItem();
			var revision = param.resolve.revision();			
			$controller(param.controller,//RequestreviewCtrl
			{
				$scope: $scope,
				$modalInstance:$modalInstance,
				participants:participants,
				currentUser:currentUser,
				matter:matter,
				checklistItem:checklistItem,
				revision:revision
			});
		    
		    
			return {
				result: function(){
				   var deferred = $q.defer();							
				   deferred.resolve(new_reviewer);	           
				   return deferred.promise;	  		 
				}()
			}
	    }); 	
	    
		$scope.requestReview(revision);
		expect( $modal.open).toHaveBeenCalled();
		$scope.$apply();	        
		
		expect(angular.equals(revision.reviewers,[new_reviewer])).toBeTruthy()
	});
	
	it('$scope.remindRevisionReview - success',function(){
		$scope.remindRevisionReview({slug:{}})
	    $scope.$apply();
		expect(toaster.pop.mostRecentCall.args[2]).toBe("All reviewers have been successfully informed.");
	});
	
	it('$scope.remindRevisionReview - failure',function(){
	    matterItemService.remindRevisionReview.andCallFake(function(param){
		   var deferred = $q.defer();							
		   deferred.reject({ is_requested: "This is so great!" });	           
		   return deferred.promise;		  
	    });	
		$scope.remindRevisionReview({slug:{}})
	    $scope.$apply();
		expect(toaster.pop.mostRecentCall.args[2]).toBe("Unable to remind the participant.");
	});
	

	
	it('$scope.onFileDropped - success',function(){	   
	    var $files = [], item = {slug:{}};
		$scope.onFileDropped($files, item);
		$scope.$apply();
		expect($scope.data.showPreviousRevisions).toBe(false);
	});
	
	it('$scope.onFileDropped - failure',function(){	
	    matterItemService.uploadRevisionFile.andCallFake(function(param){
		   var deferred = $q.defer();							
		   deferred.reject({ is_requested: "This is so great!" });	           
		   return deferred.promise;			
		})	
	    var $files = [], item = {slug:{}};
		$scope.onFileDropped($files, item);
		$scope.$apply();
		expect(toaster.pop.mostRecentCall.args[2]).toBe('Unable to upload revision');
	});	

    it('$scope.deleteRevisionReviewRequest' ,function(){
	   var  item = {slug:{},latest_revision:{reviewers:['some','other']}},review = 'some';
       $scope.deleteRevisionReviewRequest( item, review);
	   $scope.$apply();
	   expect(angular.equals(item.latest_revision.reviewers,['other'])).toBeTruthy();
	});

	it('$scope.deleteRevisionReviewRequest',function(){
	    matterItemService.deleteRevisionReviewRequest.andCallFake(function(param){
		   var deferred = $q.defer();							
		   deferred.reject({ is_requested: "This is not so great!" });	           
		   return deferred.promise;
		})
		$scope.deleteRevisionReviewRequest({slug:{}});
		$scope.$apply();
		expect(toaster.pop.mostRecentCall.args[2]).toBe('Unable to delete the revision review request.');
	});
	
	it('$scope.showReview ',function(){
		$scope.showReview();
		expect($modal.open).toHaveBeenCalled();
	});
	
	it('$scope.getReviewPercentageComplete - if 50% completed must return 50',function(){
	    var  item = {slug:{},latest_revision:{reviewers:[{name:'some',is_complete:false},{name:'other',is_complete:true}]}}
		var res = $scope.calculateReviewPercentageComplete(item);
	    expect(item.review_percentage_complete).toBe(50)
	});
	
	it('$scope.getReviewPercentageComplete - must return 0',function(){
	    var  item = {slug:{},latest_revision:{reviewers:null}};
		var res = $scope.calculateReviewPercentageComplete(item);
	    expect(item.review_percentage_complete).toBe(null)
	});

    it('$scope.focus',function(){
	    spyOn($scope,'$broadcast');
		$scope.focus('shlomo');
		$timeout.flush();
		expect($scope.$broadcast).toHaveBeenCalledWith('focusOn','shlomo')
	});
	
	it('$rootScope.$on  after getting the result -  $scope.data.authenticationModalOpened should be false',function(){
	    $scope.data.matter = {};
	    $modal.open.andCallFake(function(param){	  
  
			var matter = param.resolve.matter();
			var currentUser = param.resolve.currentUser();
			$controller(param.controller,
			{
				$scope: $scope,
				$modalInstance:$modalInstance,
				currentUser:currentUser,
				matter:matter
			});
		    
		    
			return {
				result: function(){
				   var deferred = $q.defer();							
				   deferred.resolve({ responsible_party: "This is great!" });	           
				   return deferred.promise;	  		 
				}()
			}
	    }); 	    
	    $scope.$emit('authenticationRequired',true);			
		expect($modal.open).toHaveBeenCalled();
		$scope.$apply();
		expect($scope.data.authenticationModalOpened).toBe(false)
	});
	
	it('watch after data.dueDatePickerDate',function(){
	    $scope.data.selectedItem = {date_due:{}};
        spyOn($scope,'saveSelectedItem');		
		jQuery.datepicker= jasmine.createSpyObj(jQuery.datepicker ,['formatDate']);					
		$scope.data.dueDatePickerDate = new  Date();
		
		
	    $scope.$apply();
		expect(jQuery.datepicker.formatDate).toHaveBeenCalled();
		expect($scope.saveSelectedItem).toHaveBeenCalled();
	})
});
//matterService.get failure
describe('ChecklistCtrl', function() {
    function doPromiseReject(msg){
	    return  function(){
		   var deferred = $q.defer();							
		   deferred.reject(msg);           
		   return deferred.promise;
        }		   
	}
	function makeFake(fkname, methods){
	    var msg  = { message: "This is not so great!" };
	    var fk = jasmine.createSpyObj(fkname,methods);
	    angular.forEach(methods, function(func, key){
			fk[func].andCallFake(doPromiseReject(msg));
        });
	    return 	fk;	
	}	
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
	  matterService = makeFake('matterService',['get','selectMatter','data']);
	  matterService.data.andCallFake(function(param){           
		   return {selected:{current_user:''}};		
	  });
      var msg  = { message: "This is not so great!" }; 	  
	  matterItemService  = makeFake('matterItemService',[
	  'create',
	  'delete',
	  'update',
	  'uploadRevision',
	  'updateRevision',
	  'deleteRevision',
	  'loadRevision'
	  ]);
 
	  
	  baseService = makeFake('baseService',['loadObjectByUrl']);
  
	  toaster  = makeFake('toaster',['pop']);
	  
	  ezConfirm = jasmine.createSpyObj('ezConfirm',['create']);
	  ezConfirm.create.andCallFake(function(param,param1,callbck){           
		   callbck()	  
	  });
	  
	  participantService = jasmine.createSpyObj('participantService',['getByURL']);
	  participantService.getByURL.andCallFake(doPromiseReject({ message: "This is bad!" }));

	  matterCategoryService = makeFake('matterCategoryService',['create','delete','update']);

	  
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
	
	//$scope.processUpload -failure
	it('$scope.processUpload- matterItemService.uploadRevision failed', function(){
	   $scope.processUpload([],{slug:1});
	   $scope.$apply();
	   expect(toaster.pop.mostRecentCall.args[2]).toBe("Unable to upload revision");
	});
	
	it('$scope.saveLatestRevision', function(){
		$scope.data.selectedItem = {latest_revision:'xxx'};
		$scope.saveLatestRevision();
	    $scope.$apply();
	    expect(toaster.pop.mostRecentCall.args[2]).toBe("Unable to update revision");
	});
    //$scope.deleteLatestRevision faliure
	it('$scope.deleteLatestRevision',function(){
	   $scope.data.selectedItem = {latest_revision:'something'};
	   $scope.deleteLatestRevision();
	   $scope.$apply();
	   
	   expect(toaster.pop.mostRecentCall.args[2]).toBe("Unable to delete revision")	  ;
	});	
	
	
});