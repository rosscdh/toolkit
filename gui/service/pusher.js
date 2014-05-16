angular.module('toolkit-gui')
.factory('PusherService', ['$rootScope', 'pusher_api_key', function($rootScope, pusher_api_key) {
	'use strict';
	var pusher;
	var channel;
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
		subscribe: function (channelName, eventName, callback) {
			pusher = pusher||new Pusher(pusher_api_key); // Initialise pusher if not already
			channel = pusher.subscribe(channelName);
			/**
			 * connectionError - called if unable to bind to channel
			 */
			channel.bind('pusher:subscription_error', function connectionError() {
				console.error('connection FAILED!!! pusher:subscription_error');
			});
			/**
			 * eventCaptured - called when pusher send an event to this channel
			 * @private
			 * @method				eventCaptured
			 * @memberof			PusherService
			 */
			channel.bind('pusher:subscription_succeeded', function eventCaptured() {	
				console.log('success to subscribe...');	
				channel.bind(eventName, function(msg) {
					$rootScope.$apply(function (){
						callback(msg);	
					});			 
				});
			});
		}
	};
}]);