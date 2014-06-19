describe('activity', function() {

    var
	$scope,
	ctrl,
	$rootScope,
	$controller,
	smartRoutes,
	$timeout,
	$q,
	toaster,
	ezConfirm,
	matterItemService,
	participantService,
	matterCategoryService,
	$modal,
	searchService,
	userService,
	baseService,
	activityService,
	AuthenticationRequiredCtrl,
	$modalInstance,
    matterService;

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

    beforeEach(inject(function($rootScope, $controller) {
      $scope = $rootScope.$new();
      ctrl = $controller('ClosingCtrl', {$scope: $scope});
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

});