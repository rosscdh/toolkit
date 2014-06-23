/* Generic Services */
angular.module('toolkit-gui')
.factory("genericFunctions", [ '$sanitize', function($sanitize) {
 return {
	'cleanHTML': function( str ) {
		if( typeof(str)==='string' ) {
			return str.replace(/(<([^>]+)>)/ig, '');
		} else {
			return '';
		}
	}
 };
}]);