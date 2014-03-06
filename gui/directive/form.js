


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


angular.module('toolkit-gui').directive('focusOn', function() {
   return function(scope, elem, attr) {
      scope.$on('focusOn', function(e, name) {
        console.log("received broadcast: " + name);
        console.log("waiting for broadcast: " + attr.focusOn);
        if(name === attr.focusOn) {
          elem[0].focus();
        }
      });
   };
});