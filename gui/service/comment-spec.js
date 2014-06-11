describe('itemCommentService', function() {
  beforeEach(module('toolkit-gui'));

  var checker;
  var commentService;
  beforeEach(inject(function (_commentService_) {
    commentService = _commentService_;
  }));

  it('should have create method', inject([ 'commentService', function() {
	//expect(matter.doSomething()).toEqual('something');
	expect(typeof commentService.create).toBe('function');
  }]));

  it('should have delete method', inject([ 'commentService', function() {
	//expect(matter.doSomething()).toEqual('something');
	expect(typeof commentService.delete).toBe('function');
  }]));
});
