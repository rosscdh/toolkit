describe('ChecklistCtrl', function() {
	'use strict';

	beforeEach(module('toolkit-gui'));

	var $q,scope,ctrl,matterService={};

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
		matterService.get = jasmine.createSpy('get');
		var matterDefer = $q.defer();

		//resolve on a defer and passing it data, will always run the first argument of the then() if you want to test the second one, write reject() instead, but here by default we want to resolve it and pass it an empty object that we can change it's value in any unit test
		matterDefer.resolve();
		//defer.promise is actually the object that has the then() method
		matterService.get.andReturn(matterDefer.promise);
	});

	// Ceheck objects
	it('should have usdata', function () {
		expect(scope.data instanceof Object).toBe(true);
		expect(scope.data.usdata instanceof Object).toBe(true);
	});

	it('should evaluate smart routes', inject(function() {
		expect(1).toEqual(1);
		expect(scope.data.slug).toEqual('test-matter');
	}));

	// selectItem
	it('should set selected checklist item', inject(function() {
		var dte = new Date();

		scope.selectItem( { 'date_due': dte }, 'My Category' );

		expect(scope.data.selectedItem.date_due).toEqual(dte);
		expect(scope.data.selectedCategory).toEqual('My Category');
	}));

	// initialiseMatter
	it('should initialise matter', inject(function() {
		scope.initialiseMatter( { 'items': [ { 'category': 'My Category', 'slug': '123' } ], 'categories': [ 'My Category' ] } );

		expect(scope.data.categories.length).toEqual(2); // 2 because of the null category
		expect(scope.data.matter.items.length).toEqual(1);
	}));

	//deleteCommentIsEnabled
	it('should determine comment enabled', inject(function() {
		//data.comment
		scope.data.usdata.current= { 'user_class': 'lawyer' };
		var enabled = scope.deleteCommentIsEnabled( { 'data': {'comment': 'Hello' } } );
		expect(enabled).toEqual(true); // 2 because of the null category
		
		scope.data.usdata.current= { 'user_class': 'customer' };
		enabled = scope.deleteCommentIsEnabled( { 'data': {'comment': {}} } );
		expect(enabled).toEqual(false); // 2 because of the null category
	}));

	// new date selected
	it('should change selected item`s date', inject(function() {
		var dte = new Date();
		// $scope.data.selectedItem
		scope.data.selectedItem = { 'date_due': new Date() };
		scope.data.dueDatePickerDate = dte;

		expect(scope.data.selectedItem.date_due).toEqual(dte);
	}));

	// show catgegory form
	it('should set show category form by index', inject(function() {
		scope.showEditCategoryForm(1);
		expect(scope.data.showEditCategoryForm).toEqual(1);
	}));
});