/**
 * @class iframeEvents
 * @classdesc 							Provides a way to add events and watches to iframe dom nodes
 *
 * @return {Object} Angular directive
 */
angular.module('toolkit-gui').directive("iframeEvents", function(){
	return {
		'scope': {
			'pgload': '&'
		},
		'restrict': "A",
		'link': function(scope, element, attrs) {

			scope.isLoading = true;
			scope.element = element[0];

			/**
			 * bindLoading - binds an onload event to iframe
			 * @private
			 * @type {Function}
			 */
			element.bind('load', function bindLoading(evt) {
				element.removeClass('loading');
				element.parent().removeClass('iframe-loader');
			});

			/**
			 * changeSrc - binds to events when the iframe src changes
			 * @private
			 * @type {Function}
			 */
			scope.$watch('element.src', function changeSrc(value){
				element.addClass('loading');
				element.parent().addClass('iframe-loader');
			});
		}
	};
});