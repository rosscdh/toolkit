/**
 * @class activity
 * @classdesc                             Directive for handling activity events
 *
 * @param  {Object} $scope                Contains the scope of this controller
 * @param  {Object} commentService        An angular service designed to work with the COMMENT end-point
 * @param  {Object} ngModel               The activity event object
 * @param  {Object} matterSlug            The slug of the matter
 * @param  {Object} itemSlug              The slug of the currently selected item
 * @param  {Object} user                  The current user object
 */
angular.module('toolkit-gui').directive("sticky", [ '$window', function($window){
	return {
		'scope': {
			'scrollelement': '='
		},
		'restrict': "A",
		'link': function(scope, element, attrs) {
			var scrollerNode = document.getElementById(scope.scrollelement)||$window;
			var parent = element.parent();
			var tolerance = 20;
			var parentOffset = parent.offset().top;

			var scollerOffset = scrollerNode.offsetTop;

			angular.element(scrollerNode).bind("scroll", function() {
				var elementHeight = element.height();
				var parentHeight = parent.height();
				var currentParentOffset = parent.offset().top - elementHeight - tolerance;

				// If parent within the height of the top then stick element to top
				if( currentParentOffset > (-1 * parentHeight + elementHeight) && currentParentOffset < 0 ) {
					element.addClass('sticky-fixed');
				} else {
					element.removeClass('sticky-fixed');
				}
			});
			
		}
	};
}]);