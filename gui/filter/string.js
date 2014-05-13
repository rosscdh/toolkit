/**
 * @class newlines
 * @classdesc 							Convert newline characters to &lt;br&gt; tags
 *
 * @example
 * &lt;div ng-bind="description | newlines"&gt;&lt;/div&gt;
 *
 * @return {String} Reformatted text
 */
angular.module('toolkit-gui').filter('newlines', function () {
    return function(txt) {
        txt = "" + txt;
        if (txt != null) {
            return txt.replace(/\n/g, '<br/>');
        } else {
            return '';
        }
    };
});


angular.module('toolkit-gui').filter('unsafe', function($sce) {
    return function(val) {
        return $sce.trustAsHtml(val);
    };
});

