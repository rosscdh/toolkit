angular.module('toolkit-gui').factory('searchService', ['matterService', '$log', function(matterService, $log) {

	var data = {
		'term': null,
		'matters': matterService.data(),
		'results': []
	};

	var search = {
		'filter': function( term ) {
			var results = []; var reg;
			data.term = term;
			// perform search
			if( term && term.length>0) {
				reg = new RegExp( term, "i");
				results = jQuery.grep( data.matters.items, function( item ) {
					return item.name.match(reg) && item.name.match(reg).length;
				});
			}

            $log.debug(results);
			data.results = results;
		},
		'data': function() {
			return data;
		}
	};

	return search;
}]);