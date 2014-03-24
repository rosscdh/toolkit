describe('ChecklistCtrl', function() {

	beforeEach(module('toolkit-gui'));

	var $q,scope,ctrl,matterService={};

	var localContext = {
		"window":{
			'location':{
				'href': "http://lawpal.com/matters/test-matter#/checklist?varName=foo"
			}
		}
	};

	beforeEach(inject(function($rootScope, $controller, _$q_) {
		scope = $rootScope.$new();
		ctrl = $controller('ChecklistCtrl', 
			{
				'$scope': scope,
				'smartRoutes': 
				{
					'params': function() { return { 'matterSlug': 'test-matter' }; } 
				}
			}
		);
		$q = _$q_;
	}));

	beforeEach(function(){
		// matterService
		matterService.get = jasmine.createSpy('get');
		var matterDefer = $q.defer();

		//resolve on a defer and passing it data, will always run the first argument of the then() if you want to test the second one, write reject() instead, but here by default we want to resolve it and pass it an empty object that we can change it's value in any unit test
		matterDefer.resolve();
		//defer.promise is actually the object that has the then() method
		matterService.get.andReturn(matterDefer.promise);
	});

	it('should ...', inject(function() {
		expect(1).toEqual(1);
		expect(scope.data.slug).toEqual('test-matter');
		//expect(matterService.get).toHaveBeenCalled();
	}));

	it('should set selected checklist item', inject(function() {
		var dte = new Date();

		scope.selectItem( { 'date_due': dte }, 'My Category' );

		expect(scope.data.selectedItem.date_due).toEqual(dte);
		expect(scope.data.selectedCategory).toEqual('My Category');
	}));

});

/**
 * $scope.selectItem = function(item, category) {
			$scope.data.selectedItem = item;
			$scope.data.selectedCategory = category;

			$scope.initializeActivityItemStream();

			//Reset controls
            $scope.data.dueDatePickerDate = $scope.data.selectedItem.date_due;
			$scope.data.showEditItemDescriptionForm = false;
			$scope.data.showEditItemTitleForm = false;
			$scope.data.showPreviousRevisions = false;

			$log.debug(item);
		};
 */