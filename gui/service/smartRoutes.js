angular.module('toolkit-gui').factory('smartRoutes', [ '$routeParams', '$state', function($routeParams, $state) {

	var paths = [
		{ 'pattern': '/matters/:matterSlug', 'match': /^\/matters/i }
	];

	function parseUrl( url ) {
		var a = document.createElement('a');
		a.href = url;
		return a;
	}

	var smartRoutes = {
		'params': function() {
			var urlPath = parseUrl(window.location).pathname;
			var pathEls = [];
			var urlPathEls = [];
			var matchingPath = jQuery.grep( paths, function( path ) {
				return urlPath.match( path.match ); 
			});

			if( matchingPath && matchingPath.length>0 ) {
				pathEls = matchingPath[0].pattern.split('/');
				urlPathEls = urlPath.split('/');

				for(var i=0;i<pathEls.length;i++) {
					if( pathEls[i].indexOf(':')===0 ) {
						$routeParams[ pathEls[i].replace(':','') ] = urlPathEls[i];
					}
				}
			}

			for(var key in $state.params) {
				$routeParams[key] = $state.params[key];
			}

			return $routeParams;
		}
	};

	return smartRoutes;
}]);