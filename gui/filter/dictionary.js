
angular.module('toolkit-gui').filter('valueforkey', function () {
    return function (dict, myval) {
        if (myval != null) {
            var result = "";
            jQuery.each(dict, function( key, value ) {
              if(value === myval) {
                  result = key;
                  return;
              }
            });
            return result;
        } else {
            return '';
        }
    };
});

angular.module('toolkit-gui').filter('setValueAsArrayIndex', function () {
    return function (dict) {
        if (dict != null) {
            var result = [];
            jQuery.each(dict, function( key, value ) {
               result[value] = key;
            });
            return result;
        } else {
            return '';
        }
    };
});

