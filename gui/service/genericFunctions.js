/* Generic Services */                                                                                                                                                                                                    
angular.module('toolkit-gui')                                                                                                                                                                     
.factory("genericFunctions", [ '$sanitize', function($sanitize) {                                                                                                                                                   
 return {                                                                                                                                                                                                              
   'cleanHTML': function( str ) {
		return str.replace(/(<([^>]+)>)/ig, '');
    }
 }
}]);