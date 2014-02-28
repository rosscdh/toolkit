angular.module('toolkit-gui').controller('ChecklistCtrl', [ '$scope', '$routeParams', 'matterService', 'matterItemService', function($scope, $routeParams, matterService, matterItemService){
	$scope.data = {
		'slug': $routeParams.matterSlug,
		'matter': {},
		'items': [],
        'showAddForm': -1,
		'categories': {},
		'users': [
			{ 'name': 'Sam Jackson', 'img': 'https://fbcdn-profile-a.akamaihd.net/hprofile-ak-ash3/t1/c0.0.100.100/p100x100/1014416_10100118438650161_136799916_a.jpg' },
			{ 'name': 'Bob Jackson', 'img': 'https://fbcdn-profile-a.akamaihd.net/hprofile-ak-ash2/t1/c12.12.155.155/314032_10150303812474864_594285312_a.jpg' },
			{ 'name': 'Hugh Jackson', 'img': 'https://fbcdn-profile-a.akamaihd.net/hprofile-ak-frc3/t1/c42.26.328.328/s320x320/229934_10150955684263644_890325486_n.jpg' }
		]
	};

	//$scope.matter = matterService.data();
	/*
	if( $scope.data.slug && $scope.data.slug!=='' ) {
		matterService.get( $scope.data.slug );
	}
	*/

	if( $scope.data.slug && $scope.data.slug!=='' ) {
		matterService.get( $scope.data.slug ).then(
			function success( singleMatter ){
				$scope.data.matter = singleMatter;
			},
			function error(err){

			}
		);
	}


    $scope.submitNewItem = function(category) {
       if ($scope.data.newItemName) {
         matterItemService.create($scope.data.newItemName, category).then(
             function success(item){
                $scope.data.matter.items.push(item);
                $scope.data.newItemName = '';
             },
             function error(err){
                $scope.data.matter.items.push({'name':$scope.data.newItemName, 'category':'FIRST CATEGORY'});
                $scope.data.showAddForm = true;
             }
         );
         $scope.data.showAddForm = false;
       }
    };

    $scope.showAddItemForm = function(index) {
        if ($scope.data.showAddForm != index)
            $scope.data.showAddForm=index;
        else
            $scope.data.showAddForm=-1;
        console.log($scope.data.showAddForm);
    };
}]);