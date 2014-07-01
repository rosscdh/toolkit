angular.module('toolkit-gui')
.factory('PusherService', ['$rootScope', 'pusher_api_key', '$log', function($rootScope, pusher_api_key, $log) {
	'use strict';
	var pusher;
	var notificationchannel;
	var eventchannel;
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
		subscribeUser: function (channelName, eventName, callback) {
			pusher = pusher||new Pusher(pusher_api_key); // Initialise pusher if not already
			notificationchannel = pusher.subscribe(channelName);
			/**
			 * connectionError - called if unable to bind to channel
			 */
			notificationchannel.bind('pusher:subscription_error', function connectionError() {
				console.error('connection FAILED!!! pusher:subscription_error');
			});
			/**
			 * eventCaptured - called when pusher send an event to this channel
			 * @private
			 * @method				eventCaptured
			 * @memberof			PusherService
			 */
			notificationchannel.bind('pusher:subscription_succeeded', function eventCaptured() {
				console.log('success to subscribe to userchannel...');
				notificationchannel.bind(eventName, function(msg) {
					$rootScope.$apply(function (){
						callback(msg);	
					});			 
				});
			});

		},

        subscribeMatterEvents: function(matterSlug, callback){
            pusher = pusher||new Pusher(pusher_api_key); // Initialise pusher if not already
            eventchannel = pusher.subscribe(matterSlug);

            /**
			 * connectionError - called if unable to bind to channel
			 */
			eventchannel.bind('pusher:subscription_error', function connectionError() {
				console.error('connection FAILED!!! pusher:subscription_error');
			});
			/**
			 * eventCaptured - called when pusher send an event to this channel
			 * @private
			 * @method				eventCaptured
			 * @memberof			PusherService
			 */
			eventchannel.bind('pusher:subscription_succeeded', function eventCaptured() {
				console.log('success to subscribe to eventchannel for matter: ' + matterSlug);
                eventchannel.bind('create', function(msg) {
					$rootScope.$apply(function (){
                        $log.debug("received pusher signal for create");
						callback(msg);
					});
				});
                eventchannel.bind('update', function(msg) {
					$rootScope.$apply(function (){
                        $log.debug("received pusher signal for update");
						callback(msg);
					});
				});
                eventchannel.bind('delete', function(msg) {
                    $log.debug("received pusher signal for delete");
					$rootScope.$apply(function (){
						callback(msg);
					});
				});
			});
        }
	};
}]);