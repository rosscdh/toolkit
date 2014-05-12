angular.module('skyhatchApp')
.factory('PusherService', ['$rootScope', 'pusher_app_key', function($rootScope, app_key) {
	var pusher = new Pusher(app_key);	//'caa2a556c09ad11d95f2'//, {authEndpoint: 'http://localhost:5000/api/user' }
	var channel;
	return {
		subscribe: function (channelName, eventName, callback) {
			channel = pusher.subscribe(channelName);			
			channel.bind('pusher:subscription_error', function() {
				console.error('connection FAILED!!! pusher:subscription_error')
			});
			channel.bind('pusher:subscription_succeeded', function() {	
				console.log('success to subscribe...')			
				channel.bind(eventName, function(msg) {
					$rootScope.$apply(function (){
						callback(msg);	
					})				 
				});
			});
		},        
		push:function( msg){
			channel.trigger(eventName, msg);				
		}
	};
}]);