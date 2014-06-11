describe('activityService', function() {
  beforeEach(module('toolkit-gui'));

  var checker;
  var activityService;
  var $httpBackend;
  var $q;
  beforeEach(inject(function (_activityService_, _$httpBackend_, _$q_) {
    activityService = _activityService_;
    $httpBackend = _$httpBackend_;
    $q = _$q_;
  }));

  it('should be defined', function () {
    expect(activityService).toBeDefined();
  });

  it('should be defined', function () {
    expect(typeof activityService).toBe('object');
  });

  it('should have method:matterstream', inject([ function() {
	expect(typeof activityService.matterstream).toBe('function');
  }]));

  it('should have method:itemstream', inject([ function() {
	expect(typeof activityService.itemstream).toBe('function');
  }]));

  it('should have an API_BASE', inject([ 'API_BASE_URL', function( API_BASE_URL ) {
	expect(API_BASE_URL).toEqual('/api/v1/');
  }]));

  it('should make API call: matters/:slug/activity', inject([ 'API_BASE_URL', function( API_BASE_URL ) {
	$httpBackend.expect( 'GET', API_BASE_URL + 'matters/matter-slug/activity' ).respond( { 'results': [{'title':'test title'}] } );

	var resultPromise,
        deferred = $q.defer(),
        promise = deferred.promise;

    activityService.matterstream('matter-slug').then(function (result) {
      resultPromise=result;
    });

	$httpBackend.flush();

	expect(resultPromise.length).toEqual(1);
	expect(resultPromise[0].title).toEqual('test title');
  }]));

  it('should make API call: matters/:matterSlug/items/:itemSlug/activity', inject([ 'API_BASE_URL', function( API_BASE_URL ) {
	$httpBackend.expect( 'GET', API_BASE_URL + 'matters/matter-slug/items/item-slug/activity' ).respond( { 'results': [{'title':'test title'}] } );

	var resultPromise,
        deferred = $q.defer(),
        promise = deferred.promise;

    activityService.itemstream('matter-slug', 'item-slug').then(function (result) {
      resultPromise=result;
    });

	$httpBackend.flush();

	expect(resultPromise.length).toEqual(1);
	expect(resultPromise[0].title).toEqual('test title');
  }]));
});