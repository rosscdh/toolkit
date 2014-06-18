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
			'offset': '=',
			'debug': '='
		},
		'restrict': "A",
		'link': function(scope, element/*, attrs*/) {
			var scrollerNode = document.getElementById(scope.scrollelement)||$window;
			var parent = element.parent();
			var offset = scope.offset||55;

			function processPositions() {
				var borderHeight = parseInt(element.css('border-top-width')) + parseInt(element.css('border-bottom-width'));
				var marginHeight = parseInt(element.css('margin-bottom')) + parseInt(element.css('margin-top'));
				var elementHeight = element.height() + parseInt(element.css('padding-top')) + parseInt(element.css('padding-bottom')) + borderHeight;
				var parentHeight = parent.height() + parseInt(parent.css('padding-top')) + parseInt(parent.css('padding-bottom'));
				var currentParentOffset = parent.offset().top;
				var elementOffset = element.offset().top;
				var zero = elementHeight;

				if(scope.debug) {
					console.log(currentParentOffset);
				}

				// If parent within the height of the top then stick element to top
				if( currentParentOffset > (-1 * parentHeight) && (currentParentOffset) < zero ) {
					element.addClass('sticky-fixed');
					parent.css('padding-top', elementHeight + 'px');

					if( parentHeight + currentParentOffset - elementHeight < offset ) {
						// Scroll item up nicely
						element.css('top', (parentHeight + currentParentOffset - elementHeight - borderHeight) + 'px' );
					} else {
						// Set item position to top
						element.css('top', offset + 'px' );
					}
				} else {
					element.removeClass('sticky-fixed');
					parent.css('padding-top', 0);
					element.css('top', 0 );
				}
			}

			angular.element(scrollerNode).bind("scroll", function() {
				processPositions();
			});

			processPositions();
		}
	};
}]);