


angular.module('toolkit-gui').directive('ngEnter', function () {
    return function (scope, element, attrs) {
        element.bind("keydown keypress", function (event) {
            if(event.which === 13) {
                scope.$apply(function (){
                    scope.$eval(attrs.ngEnter);
                });

                event.preventDefault();
            }
        });
    };
});


angular.module('toolkit-gui').directive('focusOn', ['$log', function($log) {
   return function(scope, elem, attr) {
      scope.$on('focusOn', function(e, name) {
        if(name === attr.focusOn) {
          elem[0].focus();
        }
      });
   };
}]);


angular.module('toolkit-gui').directive('dropdownKeepOpen', ['$log', function($log) {
   return function(scope, element, attrs) {
      jQuery(element).on({
            "click":             function() { $log.debug("clicked");  },
            "hide.bs.dropdown":  function() {
                if(scope.data.showRevisionStatusDropdown===true) {
                    return false;
                } else {
                    return true;
                }
            }
      });
   };
}]);
