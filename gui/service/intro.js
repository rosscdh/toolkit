angular.module('toolkit-gui')
.factory('IntroService', [ function($rootScope, pusher_api_key) {
	'use strict';
	return {
		/**
		 * subscribe - angular wrapper for pusher
		 * @param  {String}   channelName name of channel to subscribe to
		 * @param  {String}   eventName   [description]
		 * @param  {Function} callback    [description]
		 * @private
		 * @method				eventCaptured
		 * @memberof			PusherService
		 */
		show: function (steps, delayTime) {
			var delay = delayTime?delayTime:2000;
			setTimeout(function(){
				$.when(
					// Retrieve intro script
					$.getScript( "//cdnjs.cloudflare.com/ajax/libs/intro.js/0.5.0/intro.min.js" ),
					$.Deferred(function( deferred ){
					    $( deferred.resolve );
					})
				).done(function(){
					// Start intro
					var intro = introJs();
					intro.setOptions( steps );
          			intro.start();
				});
			}, delay);
		}
	};
}]);



    introJs().setOptions({
        'showBullets': 'false',
        'showLabel': 'false',
        'showStepNumbers': 'false',
        'KeyboardNavigation': 'false',
        steps: [
          {
            element: 'col-xs-8',
            intro: "This is your project navigation bar. It allows you to quickly access features, like editing your project page, messaging your backers, or creating a new project."
          }
        ]
      }); // close project_intro