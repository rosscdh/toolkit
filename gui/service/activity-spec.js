describe('activityService', function() {
  beforeEach(module('toolkit-gui'));

  var checker;
  beforeEach(inject(function (_activityService_, _$httpBackend_, _$q_) {
    activityService = _activityService_;
    $httpBackend = _$httpBackend_;
    $q = _$q_;
  }));

  it('should have matterstream', inject([ 'activityService', function() {
	//expect(matter.doSomething()).toEqual('something');
	expect(typeof activityService.matterstream).toBe('function');
  }]));

  it('should have itemstream', inject([ 'activityService', function() {
	//expect(matter.doSomething()).toEqual('something');
	expect(typeof activityService.itemstream).toBe('function');
  }]));

  it('should have an API_BASE', inject([ 'activityService', 'API_BASE_URL', function( activityService, API_BASE_URL ) {
	//expect(matter.doSomething()).toEqual('something');
	expect(API_BASE_URL).toEqual('/api/v1/');
  }]));

  it('should make API', inject([ 'API_BASE_URL', function( API_BASE_URL ) {
	//expect(matter.doSomething()).toEqual('something');
	//
	$httpBackend.expectGET( API_BASE_URL + 'matters/test/activity')
        .respond([{
        'username': 'tester'
    }]);
	// matterstream
	var result = activityService.matterstream('test');

	$httpBackend.flush();

	expect(result.username).toEqual('tester');
  }]));
});

/**
 * $httpBackend.expectGET('/api/index.php/users/test')
                .respond([{
                username: 'test'
            }]);
 */