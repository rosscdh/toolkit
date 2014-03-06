


angular.module('toolkit-gui').filter('newlines', function () {
    return function(txt) {
        if (txt != null) {
            return txt.replace(/\n/g, '<br/>');
        } else {
            return '';
        }
    };
});