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
        if (txt != null) {
            return txt.replace(/\n/g, '<br/>');
        } else {
            return '';
        }
    };
});