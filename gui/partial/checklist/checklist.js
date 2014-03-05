angular.module('toolkit-gui').controller('ChecklistCtrl', [
    '$scope',
    '$rootScope',
    '$routeParams',
    'ezConfirm',
	'toaster',
    'matterService',
    'matterItemService',
    'matterCategoryService',
    function($scope, $rootScope, $routeParams, ezConfirm, toaster, matterService, matterItemService, matterCategoryService){
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

		if( $scope.data.slug && $scope.data.slug!=='' ) {
			matterService.get( $scope.data.slug ).then(
				function success( singleMatter ){
					//set matter in the services
					matterService.selectMatter(singleMatter);
					matterItemService.selectMatter(singleMatter);
					matterCategoryService.selectMatter(singleMatter);
					$scope.initialiseMatter( singleMatter );
				},
				function error(err){
					toaster.pop('error', "Error!", "Unable to load matter");
					// @TODO: redirect user maybe?
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
				toaster.pop('warning', "Unable to load matter details");
			}
		};

        /* Begin item handling */
		$scope.submitNewItem = function(category) {
		   if ($scope.data.newItemName) {
			 matterItemService.create($scope.data.newItemName, category.name).then(
				 function success(item){
					category.items.push(item);
					$scope.data.newItemName = '';
				 },
				 function error(err){
					toaster.pop('error', "Error!", "Unable to create new item");
				 }
			 );
			 $scope.data.showAddForm = null;
		   }
		};

		$scope.selectItem = function(item, category) {
			$scope.data.selectedItem = item;
			$scope.data.selectedCategory = category;

            //Reset controls
            $scope.data.showEditItemDescriptionForm = false;
		};

		$scope.deleteItem = function() {
			if ($scope.data.selectedItem) {
				ezConfirm.create('Delete Item', 'Please confirm you would like to delete this item?',
					function yes() {
						// Confirmed- delete item
						matterItemService.delete($scope.data.selectedItem).then(
							function success(){
								var index = $scope.data.selectedCategory.items.indexOf($scope.data.selectedItem);
								$scope.data.selectedCategory.items.splice(index,1);
								$scope.data.selectedItem = null;
							},
							function error(err){
								toaster.pop('error', "Error!", "Unable to delete item");
							}
						);
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

        $scope.saveSelectedItem = function () {
            if ($scope.data.selectedItem) {
                matterItemService.update($scope.data.selectedItem).then(
                    function success(item){
                        //Reinitiate selected item
                        $scope.data.selectedItem = item;
                    },
                    function error(err){
                        toaster.pop('error', "Error!", "Unable to update item");
                    }
                );
            }
        };

        $scope.getItemDueDateStatus = function (item) {
            if (item.date_due) {
                var curr_date = new Date();
                var item_date = new Date(item.date_due);

                if (curr_date <= item_date){
                    return $rootScope.STATUS_LEVEL.OK;
                } else {
                    return $rootScope.STATUS_LEVEL.WARNING;
                }
            }

            return $rootScope.STATUS_LEVEL.OK;
        };
        /* End item handling */

        /* Begin CRUD Category */
        $scope.submitNewCategory = function() {
           if ($scope.data.newCatName) {
             matterCategoryService.create($scope.data.newCatName).then(
                 function success(){
                    $scope.data.categories.unshift({'name': $scope.data.newCatName, 'items': []});
                    $scope.data.newCatName = '';

                 },
                 function error(err){
                    toaster.pop('error', "Error!", "Unable to create a new category");
                 }
             );
             $scope.data.showCategoryAddForm = null;
           }
        };


        $scope.deleteCategory = function(cat) {
            matterCategoryService.delete(cat).then(
                function success(){
                    var index = $scope.data.categories.indexOf(cat);
                    $scope.data.categories.splice(index,1);

                    if (cat === $scope.data.selectedCategory){
                        $scope.data.selectedItem = null;
                    }
                },
                function error(err){
                    toaster.pop('error', "Error!", "Unable to delete category");
                }
            );
        };

        $scope.showEditCategoryForm = function(index) {
			if ($scope.data.showEditCategoryForm !== index) {
				$scope.data.showEditCategoryForm = index;
			}
			else {
				$scope.data.showEditCategoryForm = null;
			}
		};

        $scope.editCategory = function(cat) {
            matterCategoryService.update(cat).then(
                function success(){
                    //do nothing?
                },
                function error(err){
                    toaster.pop('error', "Error!", "Unable to edit category");
                }
            );
            $scope.data.showEditCategoryForm = null;
        };
        /* End CRUD Category */

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
                    if (item.category !== categoryName){
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
                                toaster.pop('error', "Error!", "Unable to update the order of items, please reload the page");
                            }
                    );
                    }
                 },
                 function error(err){
                    toaster.pop('error', "Error!", "Unable to update the order of items, please reload the page");
                 }
            );
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
