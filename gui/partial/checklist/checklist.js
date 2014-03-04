angular.module('toolkit-gui').controller('ChecklistCtrl', [ '$scope', '$routeParams', 'matterService', 'matterItemService', function($scope, $routeParams, matterService, matterItemService){
	$scope.data = {
		'slug': $routeParams.matterSlug,
		'matter': {},
		'showAddForm': null,
        'showItemDetailsOptions': false,
        'selectedItem': null,
        'selectedCategory': null,
		'categories': [],
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
                //set matter in the services
                matterService.selectMatter(singleMatter);
                matterItemService.selectMatter(singleMatter);
				$scope.initialiseMatter( singleMatter );
			},
			function error(err){

			}
		);
	}

	/**
	 * initialiseMatter: spilts the matter items into seperate arrays for the purpose of displaying seperate sortable lists, where items can be dragged
	 * @param  {Object} matter Full matter object as recieved from API
	 */
	$scope.initialiseMatter = function( matter ) {
		var i, categoryName = null, categories = [], items = [];

		// Items with blank category name
		items = jQuery.grep( matter.items, function( item ){ return item.category===categoryName; } );
		categories.push(
			{ 'name': categoryName, 'items': items }
		);
		
		if( matter && matter.categories ) {
			// Allocate items to specific categories to make multiple arrays
			jQuery.each( matter.categories, function( index, cat ) {
				var categoryName = cat;
				var items = jQuery.grep( matter.items, function( item ){ return item.category===categoryName; } );
				categories.push( { 'name': categoryName, 'items': items } );
			});

			$scope.data.matter = matter;
			$scope.data.categories = categories;

			window.categories = $scope.data.categories;
		} else {
			// Display error
		}
	};


	$scope.submitNewItem = function(category) {
	   if ($scope.data.newItemName) {
		 matterItemService.create($scope.data.newItemName, category.name).then(
			 function success(item){
				category.items.push(item);
				$scope.data.newItemName = '';
			 },
			 function error(err){
				// @TODO: Show error message
			 }
		 );
		 $scope.data.showAddForm = null;
	   }
	};

    $scope.selectItem = function(item, category) {
        $scope.data.selectedItem = item;
        $scope.data.selectedCategory = category;
    };

    $scope.deleteItem = function() {
       if ($scope.data.selectedItem) {
		 matterItemService.delete($scope.data.selectedItem).then(
			 function success(){
                var index = $scope.data.selectedCategory.items.indexOf($scope.data.selectedItem);
                $scope.data.selectedCategory.items.splice(index,1);
                $scope.data.selectedItem = null;
			 },
			 function error(err){
				// @TODO: Show error message
			 }
		 );
	   }
    };

	$scope.showAddItemForm = function(index) {
		if ($scope.data.showAddForm !== index) {
			$scope.data.showAddForm = index;
		}
		else {
			$scope.data.showAddForm = null;
		}
	};

	function recalculateCategories( evt, ui ) {
		var cats = $scope.data.categories;
		var categoryName, items = [], item, i;
		var APIUpdate = {
            'categories': [],
            'items': []
        };
        var itemToUpdate = null;

		function getItemIDs( item ) {
			return item.slug;
		}

		for(i =0;i<cats.length;i++) {
			categoryName=cats[i].name;
			items=cats[i].items;

			// Create API message
            if(cats[i].name != null) {
                APIUpdate.categories.push(cats[i].name);
            }
            jQuery.merge(APIUpdate.items, jQuery.map( items, getItemIDs ));

			// Update local data, setting category name
			jQuery.each( items, function( index, item ){
                if (item.category != categoryName){
				    item.category = categoryName;
                    itemToUpdate = item;
                }
			});
		}

		matterService.saveSortOrder(APIUpdate).then(
			 function success(){
                //if category changed for an item, save that
                if (itemToUpdate != null){
                    matterItemService.update(itemToUpdate).then(
                        function success(){
                            // do nothing
                        },
                        function error(err){
                            // @TODO: Show error message
                        }
                );
                }
			 },
			 function error(err){
				// @TODO: Show error message
			 }
		);
	}

	// UI.sortable options
	$scope.sortableOptions = {
		'stop':  recalculateCategories, /* Fires once the drag and drop event has finished */
		'connectWith': ".group",
		'axis': 'y'
	};
}]);