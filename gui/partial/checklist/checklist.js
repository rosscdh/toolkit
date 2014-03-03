angular.module('toolkit-gui').controller('ChecklistCtrl', [ '$scope', '$routeParams', 'matterService', 'matterItemService', function($scope, $routeParams, matterService, matterItemService){
	$scope.data = {
		'slug': $routeParams.matterSlug,
		'matter': {},
		/*'items': [],*/
		'showAddForm': -1,
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
				$scope.initialiseMatter( singleMatter );
				//$scope.data.matter = singleMatter;
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

			/*
			for(i =0;categoryName=matter.categories[i],i<matter.categories.length;i++) {
				items = [];
				items = jQuery.grep( matter.items, function( item ){ return item.category===categoryName; } );
				categories.push(
					{ 'name': categoryName, 'items': items }
				);
			}*/

			$scope.data.matter = matter;
			$scope.data.categories = categories;

			window.categories = $scope.data.categories;
		} else {
			// Display error
		}
	};


	$scope.submitNewItem = function(category) {
	   if ($scope.data.newItemName) {
		 matterItemService.create($scope.data.newItemName, category).then(
			 function success(item){
				$scope.data.matter.items.push(item);
				$scope.data.newItemName = '';
			 },
			 function error(err){
				$scope.data.matter.items.push( {'name':$scope.data.newItemName, 'category':'FIRST CATEGORY'} );
				$scope.data.showAddForm = true;
			 }
		 );
		 $scope.data.showAddForm = false;
	   }
	};

	$scope.showAddItemForm = function(index) {
		if ($scope.data.showAddForm !== index) {
			$scope.data.showAddForm = index;
		}
		else {
			$scope.data.showAddForm = -1;
		}
		console.log($scope.data.showAddForm);
	};

	function recalculateCategories( evt, ui ) {
		var cats = $scope.data.categories;
		var categoryName, items = [], item, i;
		var APIUpdate = {}, APIUpdates = [];

		function getItemIDs( item ) {
			return item.slug;
		}

		for(i =0;i<cats.length;i++) {
			categoryName=cats[i].name;
			items=cats[i].items;
			// Create API messages
			// @TODO Create exact API JSON data PATCH data
			APIUpdate = { 'category': cats[i].name, 'items': jQuery.map( items, getItemIDs ) };
			APIUpdates.push( APIUpdate );
			// Update local data, setting category name
			jQuery.each( items, function( index, item ){
				item.category = categoryName;
			});
		}

		// @TODO Post updates to API
	}

	// UI.sortable options
	$scope.checklistItemSortableOptions = {
		'stop':  recalculateCategories, /* Fires once the drag and drop event has finished */
		'connectWith': ".group",
		'axis': 'y'
	};

	$scope.checklistCategorySortableOptions = {
		'stop':  recalculateCategories, /* Fires once the drag and drop event has finished */
		'axis': 'y'
	};
}]);