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
	'use strict';
	return {
		'scope': {
			'scrollelement': '=',
			'tolerance': '='
		},
		'restrict': "A",
		'link': function(scope, element/*, attrs*/) {
			var scrollerNode = document.getElementById(scope.scrollelement)||$window;
			var parent = element.parent();
			var tolerance = scope.tolerance||57;

			angular.element(scrollerNode).bind("scroll", function() {
				var elementHeight = element.height();
				var parentHeight = parent.height();
				var currentParentOffset = parent.offset().top - elementHeight;
				var elementOffset = element.offset().top;
				var zero = tolerance;

				scope.data = {
					'element': { 'offset': elementOffset },
					'parent': { 'offset': currentParentOffset, 'height': parentHeight },
					'tolerance': tolerance
				};

				// If parent within the height of the top then stick element to top
				if( currentParentOffset > (-1 * parentHeight) && (currentParentOffset) < zero ) {
					element.addClass('sticky-fixed');
					parent.css('padding-top', elementHeight + 'px');
				} else {
					element.removeClass('sticky-fixed');
					parent.css('padding-top', 0);
				}
			});

			// Remove event bindings on scroll
			scope.$on('$destroy', function() {
				angular.element(scrollerNode).unbind("scroll");
			});

		}
	};
}]);