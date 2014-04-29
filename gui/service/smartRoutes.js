angular.module('toolkit-gui').factory('smartRoutes', [ '$routeParams', '$state', '$location', '$log', function($routeParams, $state, $location, $log) {

	var paths = [
		{ 'pattern': '/matters/:matterSlug', 'match': new RegExp('/matters', 'i') },
		{ 'pattern': '/matters/:matterSlug', 'match': new RegExp('matters/', 'i') }
	];

	function parseUrl( url ) {
		var path = '';
		var a = document.createElement('a');
		a.href = url;

		path = a.pathname;

		/* IE fix */
		if( path[0]!=='/' ) {
			path = '/' + path;
		}
		return path;
	}

	var smartRoutes = {
		'params': function() {
			var urlPath = parseUrl($location.absUrl());
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