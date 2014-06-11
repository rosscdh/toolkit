angular.module('ez.confirm').run(['$templateCache', function($templateCache) {
  'use strict';

  $templateCache.put('ez-confirm-tpl.html',
    "<div class=\"ez-confirm\">\n" +
    "  <div class=\"modal-header\">\n" +
    "    <a type=\"button\" class=\"close\" ng-click=\"cancel()\" aria-hidden=\"true\">&times;</a>\n" +
    "    <h4>{{ heading }}</h4>\n" +
    "  </div>\n" +
    "  <div class=\"modal-body\">\n" +
    "    <p class=\"lead\">{{ text }}</p>\n" +
    "  </div>\n" +
    "  <div class=\"modal-footer\">\n" +
    "    <a class=\"btn btn-default\" ng-click=\"cancel()\">Cancel</a>\n" +
    "    <button ng-click=\"ok()\" class=\"btn btn-inverse\">Confirm</button>\n" +
    "  </div>\n" +
    "</div>\n"
  );

}]);