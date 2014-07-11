angular.module('JSONedit', []).directive('jsoneditor', function($compile, $timeout) {
  return {
    'restrict': 'A',
    'scope': {
      'schema': '='
    },
    'controller': ['$scope', '$element', '$attrs', function($scope, $element, $attrs) {
        console.log('Am here', $scope.details);

        var options = {
            'schema': {},
            'theme': 'bootstrap3',
            'disable_edit_json': true,
            'disable_collapse':true
        };
        var editor;

        $scope.$watch('schema', function(nv) {
            if(nv && !editor) {
                options.schema = nv;
                editor = new JSONEditor($element[0], options);
            }
        });
    }]
  };
});