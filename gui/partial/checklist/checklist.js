angular.module('toolkit-gui')
/**
 * @class ChecklistCtrl
 * @classdesc 							Controller for retreiving and display checklists
 *
 * @param  {Object} $scope                Contains the scope of this controller
 * @param  {Object} $rootScope            Rootscope variable
 * @param  {Object} $routeParams          Object that provides access to Angular route parameters
 * @param  {Function} ezConfirm           A wrapper that simulates the native confirm dialog
 * @param  {Function} toaster             A directive that provides the ability to show status messages to the end user
 * @param  {Function} $modal              A directive that provides a wrapper for displaying and managing dialogs
 * @param  {Object} matterService         An angular service designed to work with MATTER API end-points
 * @param  {Object} matterItemService     A custom angular service designed to work with MATTER ITEM API end-points
 * @param  {Object} matterCategoryService A custom angular service designed to work with MATTER CATEGORY end-points
 * @param  {Object} participantService    A custom angular service designed to work with USER end-points
 * @param  {Object} activityService       A custom angular service designed to work with ACTIVITY end-points
 * @param  {Object} userService           A custom angular service designed to work with USER end-points
 * @param  {Object} commentService        A custom angular service designed to work with COMMENT end-points
 * @param  {Function} $timeout            An angular wrapper for setTimeout that allows angular to keep track of when to update views
 */
.controller('ChecklistCtrl', [
	'$scope',
	'$rootScope',
	'$routeParams',
	'$state',
	'$location',
    '$sce',
    '$sanitize',
    '$compile',
    '$route',
	'smartRoutes',
	'ezConfirm',
	'toaster',
	'$modal',
	'baseService',
	'matterService',
	'matterItemService',
	'matterCategoryService',
	'participantService',
	'searchService',
	'activityService',
	'userService',
	'commentService',
	'genericFunctions',
	'$timeout',
	'$log',
	'$window',
	'$q',
	'Intercom',
	'INTERCOM_APP_ID',
	'PusherService',
	function($scope,
			 $rootScope,
			 $routeParams,
			 $state,
			 $location,
             $sce,
             $sanitize,
             $compile,
             $route,
			 smartRoutes,
			 ezConfirm,
			 toaster,
			 $modal,
			 baseService,
			 matterService,
			 matterItemService,
			 matterCategoryService,
			 participantService,
			 searchService,
			 activityService,
			 userService,
			 commentService,
			 genericFunctions,
			 $timeout,
			 $log,
			 $window,
			 $q,
			 Intercom,
			 INTERCOM_APP_ID,
             PusherService){
		'use strict';
		/**
		 * Scope based data for the checklist controller
		 * @memberof			ChecklistCtrl
		 * @private
		 * @type {Object}
		 */
		var routeParams = smartRoutes.params();

		/**
		 * In scope variable containing containing the currently selected matter
		 * @memberof ChecklistCtrl
		 * @type {Object}
		 * @private
		 */
		$scope.matter = matterService.data(); // Used to communicate between controllers

		$scope.data = {
			'slug': routeParams.matterSlug,
			'matter': null,
      'customers' : [],
			'showAddForm': null,
			'showItemDetailsOptions': false,
			'selectedItem': null,
			'selectedCategory': null,
			'categories': [],
			'users': [],
			'searchData': searchService.data(),
			'usdata': userService.data(),
			'streamType': 'matter',
			'history': {},
			'page': 'checklist',
			'statusFilter': null,
			'itemFilter': null,
			'knownSigners': [],
            'showPreviousRevisions': false
		};

		//debugger;
		// Basic checklist item format, used for placeholder checklist items
		var CHECKLISTITEMSKELETON = {
			"status": -1,
			"responsible_party": null,
			"review_percentage_complete": null,
			"name": "",
			"description": null,
			"parent": null,
			"children": [],
			"closing_group": null,
			"category": null,
			"latest_revision": null,
			"is_final": false,
			"is_complete": false,
			"is_requested": false,
			"date_due": null,
			"loading": true
		};

		function loadMatter() {
			matterService.get( $scope.data.slug ).then(
				function success( singleMatter ){
					$scope.data.matter = singleMatter;

					//set matter in the services
					matterService.selectMatter(singleMatter);
					$scope.initialiseMatter( singleMatter );
					$scope.initializeActivityStream( singleMatter );

					userService.setCurrent( singleMatter.current_user, singleMatter.lawyer );
					$scope.initialiseIntercom(singleMatter.current_user);
                    $scope.handleMatterEvents();
				},
				function error(/*err*/){
					toaster.pop('error', 'Error!', 'Unable to load matter',5000);
					// @TODO: redirect user maybe?
				}
			);
		}

		if( $scope.data.slug && $scope.data.slug!=='' && $scope.data.matterCalled==null) {
			$scope.data.matterCalled = true;
			loadMatter();
		}

		/**
		 * Handles the event when the URL params changes inside the ng app
		 *
		 * @private
		 * @memberof			ChecklistCtrl
		 */
		$rootScope.$on('$stateChangeSuccess', function () {
			$scope.handleUrlState();
		});


		/**
		 * This function activates the following states inside the app by the URL params:
		 * 1) Select a checklist item
		 * 2) Show a review in the review modal window
		 *
		 * @private
		 * @memberof			ChecklistCtrl
		 * @method              handleUrlState
		 */
		$scope.handleUrlState = function () {
			var itemSlug = $state.params.itemSlug;
			var revisionSlug = $state.params.revisionSlug;
			var reviewSlug = $state.params.reviewSlug;
			var itemToSelect = null;

			if (itemSlug && (!$scope.data.selectedItem || itemSlug !== $scope.data.selectedItem.slug)) {
				$log.debug('Selecting item because of url change');

				// find item
				itemToSelect = $scope.getItemBySlug(itemSlug);
				if (itemToSelect) {
					$scope.selectItem(itemToSelect, itemToSelect.category).then(
						function success(/*item*/) {
							//item is fully loaded
							if (revisionSlug && reviewSlug) {
								$scope.showReviewBySlug(revisionSlug, reviewSlug);
							}
						}
					);
				} else {
					toaster.pop('warning', 'Item not found' , 'Item does not exist anymore.',5000);
				}
			}

			if (revisionSlug && reviewSlug && !itemToSelect && $scope.data.selectedItem) {
				//item is already loaded
				$scope.showReviewBySlug(revisionSlug, reviewSlug);
			}
		};

        /**
         * Handles all pusher notifications
         *
		 * @private
		 * @memberof			ChecklistCtrl
		 * @method              handleMatterEvents
         */
        $scope.handleMatterEvents = function () {
            PusherService.subscribeMatterEvents($scope.data.slug, function (data) {
                $log.debug(data);

                //wait until we can be sure, that the changed data is stored in the DB
                $timeout(function () {
                    if (data.is_global === true || data.from_id !== $scope.data.usdata.current.username) {
                        if (data.model === 'item') {

                            //Event: Item updated
                            if (data.event === 'update') {
                                $log.debug("loading updated item");
                                matterItemService.load($scope.data.slug, data.id).then(
                                    function success(item) {
                                        replaceItem(item);

                                        if (item.slug !== $scope.data.selectedItem.slug) {
                                            toaster.pop('warning', 'Item ' + item.name + ' has been updated.', 'Click here to select the item.', 7000, null, function () {
                                                $scope.selectItem(item, category);
                                            });
                                        }
                                    }
                                );
                            //Event: item deleted
                            } else if (data.event === 'delete') {
                                var index = -1;
                                var category;
                                var foundItem;

                                //find and delete the item
                                jQuery.each($scope.data.matter.categories, function (index, cat) {
                                    jQuery.each(cat.items, function (i, item) {
                                        if (item.slug === data.id) {
                                            index = i;
                                            category = cat;
                                            foundItem = item;
                                        }
                                    });
                                });

                                if (item && category) {
                                    //remove item from category
                                    category.items.splice(index,1);

                                    //remove item from items list
                                    index = jQuery.inArray( foundItem, $scope.data.matter.items );
                                    if( index>=0 ) {
                                        $scope.data.matter.items.splice(index,1);
                                    }
                                }

                                if (data.id !== $scope.data.selectedItem.slug) {
                                    toaster.pop('warning', 'Item deleted', 'Item ' + foundItem.name + ' has been deleted.', 5000, null);
                                } else {
                                    $scope.data.selectedItem = null;
								    $scope.initializeActivityStream();
                                }

                            //Event: Item created
                            } else if (data.event === 'create') {
                                $log.debug("loading created item");
                                matterItemService.load($scope.data.slug, data.id).then(
                                    function success(newItem) {
                                        var category = findCategory(newItem.category);

                                        //insert item at the end
                                        category.items.push(newItem)

                                         toaster.pop('warning', 'Item ' + newItem.name + ' has been created.', 'Click here to select the item.', 7000, null, function () {
                                            $scope.selectItem(newItem, category);
                                        });
                                    }
                                );
                            }

                        } else if (data.model === 'matter') {
                            toaster.pop('warning', 'Matter has been updated.', 'Click here to refresh the matter.', 5000, null, function () {
                                window.location.reload();
                            });
                        }
                    }
                }, 2000);
            });
        };

		/**
		 * Splits the matter items into seperate arrays for the purpose of displaying seperate sortable lists, where items can be dragged
		 * @name	initialiseMatter
		 * @param  {Object} matter Full matter object as recieved from API
		 * @private
		 * @memberof			ChecklistCtrl
		 * @method			initialiseMatter
		 */
		$scope.initialiseMatter = function( matter ) {
			var /*i, */categoryName = null, categories = [], items = [];
			var firstItem, category;

			// Items with blank category name
			items = jQuery.grep( matter.items, function( item ){ return item.category===categoryName; } );
			category = { 'name': categoryName, 'items': items };
					
			categories.push(category);

			// First item if available, this will be used to open the first available checklist item by default
			firstItem = matterService.selectFirstitem( firstItem, items, category );

			if( matter && matter.categories ) {
				// Allocate items to specific categories to make multiple arrays
				jQuery.each( matter.categories, function( index, cat ) {
					var categoryName = cat, category;
					var items = jQuery.grep( matter.items, function( item ){ return item.category===categoryName; } );

					category = { 'name': categoryName, 'items': items };
					categories.push( category );

					// First item if available, this will be used to open the first available checklist item by default
					firstItem = matterService.selectFirstitem( firstItem, items, category );
				});

        jQuery.each( matter.participants, function( index, participant ) {
          if (participant.user_class === 'customer'){
            $scope.data.customers.push(participant);
          }

        });

				$scope.data.matter = matter;
				$scope.data.categories = categories;

				// If there is no state then select the first available item
				if(!$state.params.itemSlug && firstItem) {
					$location.path('/checklist/' + firstItem.item.slug);
				}
				$scope.handleUrlState();

			} else {
				// Display error
				toaster.pop('warning', 'Unable to load matter details',5000);
			}
		};

		/**
		 * Inits the intercom interface
		 *
		 * @name	initialiseIntercom
		 * @param  {Object} Current user object
		 * @private
		 * @memberof			ChecklistCtrl
		 * @method			initialiseIntercom
		 */
        $scope.initialiseIntercom = function(currUser){
            $log.debug(currUser);

            Intercom.boot({
                'user_id': currUser.username,
                'email': currUser.email,
                'first_name': currUser.first_name,
                'last_name': currUser.last_name,
                'firm_name': currUser.firm_name,
                'verified': currUser.verified,
                'type': currUser.user_class,
                'app_id': INTERCOM_APP_ID,
                'created_at': (new Date(currUser.date_joined).getTime()/1000),
                'matters_created': currUser.matters_created,
                'user_hash': currUser.intercom_user_hash,
                'widget': {
                    'activator': '.intercom',
                    'use_counter': true
                }
            });
			//Intercom.show();
		};


        $scope.editTextattribute = function(obj, context, attr) {
            $scope.data['show_edit_'+ context + '_' + attr] = true;

			if (obj['edit_'+ context + '_' + attr] && obj['edit_'+ context + '_'+ attr].length > 0){
				//do nothing
			} else {
				obj['edit_'+ context + '_' + attr] = obj[attr];
			}

			$scope.focus('event_edit_'+ context + '_' + attr);
		};

		/***
		 ___ _
		|_ _| |_ ___ _ __ ___  ___
		 | || __/ _ \ '_ ` _ \/ __|
		 | || ||  __/ | | | | \__ \
		|___|\__\___|_| |_| |_|___/
		 */
		/**
		 * Requests the checklist API to add a checklist item
		 *
		 * @name				submitNewItem
		 *
		 * @param  {Object} category	Category object contains category name (String)
		 * @private
		 * @method				submitNewItem
		 * @memberof			ChecklistCtrl
		 */
		$scope.getItemBySlug = function (itemSlug) {
			var matter = $scope.data.matter;

			if (matter) {
				var items = jQuery.grep( matter.items, function(item) {
					return item.slug === itemSlug;
				});

				if (items.length > 0){
					return items[0];
				}
			}
			return null;
		};

		$scope.submitNewItem = function(category) {
			var matterSlug = $scope.data.slug;
			var placeholderItem = angular.copy(CHECKLISTITEMSKELETON);
			var itemName = $scope.data.newItemName;

			if ($scope.data.newItemName) {

				placeholderItem.name = itemName;
				placeholderItem.category = category.name;

				// Add placeholder item
				category.items.push(placeholderItem);

				// Clean up GUI
				$scope.data.newItemName = '';

				matterItemService.create(matterSlug, itemName, category.name).then(
				function success(item){
					updateObject(placeholderItem /*originalItem*/, item /*item recieved from API*/);
					/* category.items.push(item); */
					/* $scope.data.newItemName = ''; */

					// Display item that has just been added
					$scope.selectItem( item, category );
				},
				function error(/*err*/){
					toaster.pop('error', 'Error!', 'Unable to create new item',5000);
				}
			);
			}
		};

		/**
		 * updateObject: given a checklist item placeholder, update properties given updated details from the API
		 * @param  {Object} originalItem placeholder checklist item
		 * @param  {Object} updatedItem  update object from API
		 */
		function updateObject( originalItem, updatedItem ) {
			delete originalItem.loading;

			// Updating the object this way does not interupt the referenced object in the array
			for(var key in updatedItem) {
				originalItem[key] = updatedItem[key];
			}
		}

		/**
		 * Sets the currently selected item to the one passed through to this method
		 *
		 * @param  {Object}	item		Category object contains category name (String)
		 * @param {Object}	category	object representing the category of the item to select
		 * @param {Object}	reviewSlug	slug to the
		 * @private
		 * @method						selectItem
		 * @memberof					ChecklistCtrl
		 */
		$scope.selectItem = function(item, category) {
			var deferred = $q.defer();

			$scope.data.selectedItem = item;
			$scope.data.selectedCategory = category;

			$scope.activateActivityStream('item');

            $scope.loadItemDetails(item).then(function success(item){
                deferred.resolve(item);
                $scope.data.itemIsLoading = false;
		    });

		    resetScopeState();

			$scope.displayDetails();	// @mobile

			return deferred.promise;
		};

		function resetScopeState() {
			$scope.data.itemIsLoading = true;
			$scope.data.showAddFileOptions = false;

			//Reset controls
			$scope.data.dueDatePickerDate = $scope.data.selectedItem.date_due;
			$scope.data.showEditItemTitleForm = false;
			$scope.data.showPreviousRevisions = false;

			$scope.data.show_edit_item_description = false;
			$scope.data.show_edit_revision_description = false;
		}

		/**
		 * Allows the GUI some time to update before incepting the request to load item details
		 * @param  {Object} item     Checklist item being loaded
		 * @param  {Object} category Category that the checklist item belongs to
		 * @private
		 * @method						delayselectItem
		 * @memberof					ChecklistCtrl
		 */
		$scope.delayselectItem = function(item, category) {
			$scope.data.itemIsLoading = true;

			$timeout(function(){
				$scope.selectItem(item, category);
			},10);
		};

		$scope.displayChecklist = function() {
			$scope.data.page = 'checklist';
		};

		$scope.displayDetails = function() {
			$scope.data.page = 'details';
		};

		$scope.displayActivity = function() {
			$scope.data.page = 'activity';
		};

		/**
		 * Listen for itemslected events (for example for search results)
		 * @param  {Event} evt
		 * @param  {Object} item Checklist item selected
		 */
		$scope.$on('itemSelected', function( evt, item ){
			var category = findCategory( item.category );
			$scope.selectItem( item, category );
		});

		/**
		 * Given a category string, findthe category object
		 * @param  {String} name category name
		 * @return {Object}      category object
		 */
		function findCategory(name) {
			var cats = jQuery.grep( $scope.data.categories, function(cat) {
				return cat.name === name;
			});

			if( cats.length===1) {
				return cats[0];
			} else {
				return null;
			}
		}

        function replaceItem(newItem){
            var category = findCategory(newItem.category);
            var i = -1;
            //find and replace the olditem
            jQuery.each(category.items, function (index, olditem) {
                if (olditem.slug === newItem.slug) {
                    i = index;
                }
            });

            if (i > -1) {
                category.items[i] = newItem;
            }
        }

		$scope.loadItemDetails = function(item){
			var deferred = $q.defer();

			//if(typeof(item.latest_revision.reviewers) === "string") {
			if(item.latest_revision && !item.latest_revision.reviewers) {
				baseService.loadObjectByUrl(item.latest_revision.url).then(
					function success(obj){
						item.latest_revision = obj;
						deferred.resolve(item);
					},
					function error(/*err*/){
						toaster.pop('error', 'Error!', 'Unable to load latest revision',5000);
					}
				);
			} else {
				deferred.resolve(item);
			}

			return deferred.promise;
		};


		/**
		 * Requests the checklist API to delete the currently selected checklist item
		 *
		 * @name 				deleteItem
		 * @private
		 * @method				deleteItem
		 * @memberof			ChecklistCtrl
		 */
		$scope.deleteItem = function() {
			var matterSlug = $scope.data.slug;

			if ($scope.data.selectedItem) {
				ezConfirm.create('Delete Item', 'Please confirm you would like to delete this item?',
					function yes() {
						// Confirmed- delete item
						matterItemService.delete(matterSlug, $scope.data.selectedItem).then(
							function success(){
								var index = jQuery.inArray( $scope.data.selectedItem, $scope.data.selectedCategory.items );
								if( index>=0 ) {
									// Remove item from in RAM array
									$scope.data.selectedCategory.items.splice(index,1);
								}

								index = jQuery.inArray( $scope.data.selectedItem, $scope.data.matter.items );
								if( index>=0 ) {
									$scope.data.matter.items.splice(index,1);
								}

								$scope.data.selectedItem = null;
								$scope.initializeActivityStream();
							},
							function error(/*err*/){
								toaster.pop('error', 'Error!', 'Unable to delete item', 5000);
							}
						);
					}
				);
			}
		};

		/**
		 * Changes index flag to display a specific add form
		 *
		 * @name 				showAddItemForm
		 *
		 * @param  {Number} index Index (starting at 0) of the group for which to display the add form
		 *
		 * @private
		 * @method				showAddItemForm
		 * @memberof			ChecklistCtrl
		 */
		$scope.showAddItemForm = function(index) {
			if ($scope.data.showAddForm !== index) {
				$scope.data.showAddForm = index;
				$scope.focus('eventNewItem-'+index);
			}
			else {
				$scope.data.showAddForm = null;
			}
		};

		/**
		 * Executes a save of the selected item, using the in scope variable selectedItem
		 *
		 * @name 				saveSelectedItem
		 *
		 * @private
		 * @method				saveSelectedItem
		 * @memberof			ChecklistCtrl
		 */
		$scope.saveSelectedItem = function () {
			var matterSlug = $scope.data.slug;
			var selectedItem = $scope.data.selectedItem;

			if (selectedItem) {
				selectedItem.name = genericFunctions.cleanHTML(selectedItem.name);
				selectedItem.description = genericFunctions.cleanHTML(selectedItem.description);

				selectedItem.edit_item_description = selectedItem.description;

				matterItemService.update(matterSlug, $scope.data.selectedItem).then(
					function success(/*item*/){
						//do nothing
					},
					function error(/*err*/){
						toaster.pop('error', 'Error!', 'Unable to update item',5000);
					}
				);
			}
		};

		/**
		 * Receives the user object from the API by the given URL and returns his full name if existing or
		 * the email address. When showOnlyInitials is set, then it just returns the initials of the user.
		 *
		 * @name 				getParticipantByUrl
		 *
		 * @param  {String}  API url of the participant
		 * @param  {Boolean} If set to true, just return the initials of the user
		 *
		 * @private
		 * @method				getParticipantByUrl
		 * @memberof			ChecklistCtrl
		 */
		$scope.getParticipantByUrl = function (participanturl){
			 if ($scope.data.loadedParticipants == null) {
				 $scope.data.loadedParticipants = {};
			 }

			 //only load user from api, if not already loaded
			 if (participanturl != null && $scope.data.loadedParticipants[participanturl] == null) {
				 $scope.data.loadedParticipants[participanturl] = {};

				 participantService.getByURL(participanturl).then(
					 function success(participant){
						 //store user in dict with url as key
						 $scope.data.loadedParticipants[participanturl] = participant;
						 return participant;
					 },
					 function error( /*err*/ ){
						 return '';
					 }
				 );
			 } else if (participanturl != null && $scope.data.loadedParticipants[participanturl] != null){
				 return $scope.data.loadedParticipants[participanturl];
			 } else {
				 return '';
			 }
		};
		/*** End item handling */

		/*
		  ____ ____  _   _ ____     ____      _
		 / ___|  _ \| | | |  _ \   / ___|__ _| |_ ___  __ _  ___  _ __ _   _
		| |   | |_) | | | | | | | | |   / _` | __/ _ \/ _` |/ _ \| '__| | | |
		| |___|  _ <| |_| | |_| | | |__| (_| | ||  __/ (_| | (_) | |  | |_| |
		 \____|_| \_\\___/|____/   \____\__,_|\__\___|\__, |\___/|_|   \__, |
													  |___/            |___/
		 */
		/**
		 * Return item due status
		 *
		 * @name 				submitNewCategory
		 *
		 * @private
		 * @method				submitNewCategory
		 * @memberof			ChecklistCtrl
		 */
		$scope.submitNewCategory = function() {
			var matterSlug = $scope.data.slug;

			if ($scope.data.newCatName) {
				matterCategoryService.create(matterSlug, $scope.data.newCatName).then(
					function success(){
						//IMPORTANT: Insert at pos 1, because pos 0 is for the null category
						$scope.data.categories.splice(1, 0, {'name': $scope.data.newCatName, 'items': []});
						$scope.data.newCatName = '';
					},
					function error(/*err*/){
						toaster.pop('error', 'Error!', 'Unable to create a new category',5000);
					}
				);
				$scope.data.showCategoryAddForm = null;
			}
		};

		/**
		 * Request the API to delete a specific category
		 *
		 * @name 				deleteCategory
		 *
		 * @param {Object} cat Catgory object
		 *
		 * @private
		 * @method				deleteCategory
		 * @memberof			ChecklistCtrl
		 */
		$scope.deleteCategory = function (cat) {
			var matterSlug = $scope.data.slug;

			ezConfirm.create('Delete Category', 'Please confirm you would like to delete this category?',
				function yes() {
					// Confirmed- delete category
					matterCategoryService.delete(matterSlug, cat).then(
						function success() {
							var index = jQuery.inArray(cat, $scope.data.categories);
							if (index >= 0) {
								// Remove item from in RAM array
								$scope.data.categories.splice(index, 1);
							}

							if (cat === $scope.data.selectedCategory) {
								$scope.data.selectedItem = null;
							}
						},
						function error(/*err*/) {
							toaster.pop('error', 'Error!', 'Unable to delete category',5000);
						}
					);
				}
			);
		};

		/**
		 * Sets an index value used to display/hide edit category form
		 *
		 * @name 				showEditCategoryForm
		 *
		 * @param {Object} cat Catgory object
		 *
		 * @private
		 * @method				showEditCategoryForm
		 * @memberof			ChecklistCtrl
		 */
		$scope.showEditCategoryForm = function(index) {
			if ($scope.data.showEditCategoryForm !== index) {
				$scope.data.showEditCategoryForm = index;
				$scope.focus('eventEditCategorytitle-'+index);
			}
			else {
				$scope.data.showEditCategoryForm = null;
			}
		};

		/**
		 * Sets an index value used to display/hide add category form
		 *
		 * @name 				showAddCategoryForm
		 *
		 * @param {Object} cat Catgory object
		 *
		 * @private
		 * @method				showEditCategoryForm
		 * @memberof			ChecklistCtrl
		 */
		$scope.showAddCategoryForm = function(index) {
			if ($scope.data.showAddCategoryForm !== index) {
				$scope.data.showAddCategoryForm = index;
				$scope.focus('eventAddCategory-'+index);
			}
			else {
				$scope.data.showAddCategoryForm = null;
			}
		};

		/**
		 * Request the API to update a specific category
		 *
		 * @name 				editCategory
		 *
		 * @param {Object} cat Catgory object
		 *
		 * @private
		 * @method				editCategory
		 * @memberof			ChecklistCtrl
		 */
		$scope.editCategory = function(cat) {
			var matterSlug = $scope.data.slug;

			matterCategoryService.update(matterSlug, cat.name, $scope.data.newCategoryName).then(
				function success(){
					cat.name = $scope.data.newCategoryName;
				},
				function error(/*err*/){
					toaster.pop('error', 'Error!', 'Unable to edit category',5000);
				}
			);
			$scope.data.showEditCategoryForm = null;
		};
		/* End CRUD Category */

		/*
		 ____            _     _
		|  _ \ _____   _(_)___(_) ___  _ __
		| |_) / _ \ \ / / / __| |/ _ \| '_ \
		|  _ <  __/\ V /| \__ \ | (_) | | | |
		|_| \_\___| \_/ |_|___/_|\___/|_| |_|

		 */

		/**
		 * Recieves file details from filepicker.io directive
		 *
		 * @name 				processUpload
		 *
		 * @param {Object} cat Catgory object
		 *
		 * @private
		 * @method				processUpload
		 * @memberof			ChecklistCtrl
		 */
		$scope.processUpload = function( files, item ) {
			var matterSlug = $scope.data.slug;
			var itemSlug = item.slug;
			$scope.data.uploading = true;
			item.uploading = true;

			matterItemService.uploadRevision( matterSlug, itemSlug, files ).then(
				function success( revision ) {
					revision.uploaded_by = matterService.data().selected.current_user;
					item.latest_revision = revision;

					// Update uploading status
					item.uploading = false;
					$scope.data.uploading = $scope.uploadingStatus( $scope.data.matter.items );

					//Reset previous revisions
					item.previousRevisions = null;
					$scope.data.showPreviousRevisions = false;
					$scope.calculateReviewPercentageComplete(item);
					toaster.pop('success', 'Success!', 'Document added successfully', 3000);
				},
				function error(/*err*/) {
					// Update uploading status
					item.uploading = false;
					$scope.data.uploading = $scope.uploadingStatus( $scope.data.matter.items );
					
					toaster.pop('error', 'Error!', 'Unable to upload revision', 5000);
				}
			);
		};

		$scope.uploadingStatus = function( allItems ) {
			for(var i=0;i<allItems.length;i++) {
				if(allItems[i].uploading) {
					return true;
				}
			}

			return false;
		};

		/**
		 * Initiate the file upload process
		 * @param  {Array} $files HTML5 files object
		 * @param  {Object} item   Matter checklist item object
		 */
		$scope.onFileDropped = function( $files, item ) {
			var matterSlug = $scope.data.slug;
			var itemSlug = item.slug;

			var user = userService.data().current;
			var promise;

			if( user.permissions.manage_items) {
				item.uploading = true;
				$scope.data.uploading = true;

				promise = matterItemService.uploadRevisionFile( matterSlug, itemSlug, $files );

				item.uploadHandle = promise.uploadHandle;

				promise.then(
					function success( revision ) {
						revision.uploaded_by = matterService.data().selected.current_user;
						item.latest_revision = revision;

						// Reset previous revisions
						item.previousRevisions = null;
						$scope.data.showPreviousRevisions = false;

						// Update uploading status
						item.uploadingPercent = 0;
						item.uploading = false;
						$scope.data.uploading = $scope.uploadingStatus( $scope.data.matter.items );
						toaster.pop('success', 'Success!', 'File added successfully',3000);
					},
					function error(err) {
						// Update uploading status
						item.uploading = false;

						$scope.data.uploading = $scope.uploadingStatus( $scope.data.matter.items );

						var msg = err&&err.message?err.message:'Unable to upload revision';
						var title = err&&err.title?err.title:'Error';

						toaster.pop('error', title, msg, 5000);
					},
					function progress( num ) {
						/* IE-Fix, timeout and force GUI update */
						setTimeout(function(){
							item.uploadingPercent = num;
							$scope.$apply();
						},10);
					}
				);
			}
		};

		//
		//
		$scope.cancelRevisionUpload = function(item) {
			item.uploadHandle.canceled = true;
			item.uploadHandle.abort();
		};

		/**
		 * Request API to create a new revision
		 *
		 * @name 				saveLatestRevision
		 *
		 * @private
		 * @method				saveLatestRevision
		 * @memberof			ChecklistCtrl
		 */
		$scope.saveLatestRevision = function () {
			var matterSlug = $scope.data.slug;
			var item = $scope.data.selectedItem;

			if (item && item.latest_revision) {
				matterItemService.updateRevision(matterSlug, item.slug, $scope.data.selectedItem.latest_revision).then(
					function success(/*item*/){
						//do nothing
					},
					function error(/*err*/){
						toaster.pop('error', 'Error!', 'Unable to update revision');
					}
				);
			}
		};


		/**
		 * Request API to delete latest revision
		 *
		 * @name 				deleteLatestRevision
		 *
		 * @private
		 * @method				deleteLatestRevision
		 * @memberof			ChecklistCtrl
		 */
		 $scope.deleteLatestRevision = function () {
			var matterSlug = $scope.data.slug;
			var item = $scope.data.selectedItem;

			if (item && item.latest_revision) {
				ezConfirm.create('Delete Revision', 'Please confirm you would like to delete this revision?',
					function yes() {
						matterItemService.deleteRevision(matterSlug, item.slug, $scope.data.selectedItem.latest_revision).then(
							function success(){
								//Set latest prev Revision as current if existing
								if(item.latest_revision.revisions != null && item.latest_revision.revisions.length>0){
									var revurl = item.latest_revision.revisions[item.latest_revision.revisions.length-1];
									var revslug = revurl.substring(revurl.lastIndexOf('/')+1, revurl.length);

									//First revision in array is the latest one
									matterItemService.loadRevision(matterSlug, item.slug, revslug).then(
										function success(revision){
											item.latest_revision = revision;
											$scope.calculateReviewPercentageComplete(item);
										},
										function error(/*err*/){
											toaster.pop('error', 'Error!', 'Unable to set new current revision',5000);
										}
									);
								} else {
									item.latest_revision = null;
									$scope.calculateReviewPercentageComplete(item);
								}

								//Reset previous revisions
								item.previousRevisions = null;
								$scope.data.showPreviousRevisions = false;
							},
							function error(/*err*/){
								toaster.pop('error', 'Error!', 'Unable to delete revision',5000);
							}
						);
					}
				);
			}
		};

		/**
		 * Request API to get all previous revisions of the item
		 *
		 * @name 				loadPreviousRevisions
		 *
		 * @private
		 * @method				loadPreviousRevisions
		 * @memberof			ChecklistCtrl
		 */
		 $scope.loadPreviousRevisions = function () {
			var matterSlug = $scope.data.slug;
			var item = $scope.data.selectedItem;

			function SortDescendingByCreationDate(a, b){
				var aDate = moment(a.date_created, 'YYYY-MM-DDTHH:mm:ss.SSSZ');
				var bDate = moment(b.date_created, 'YYYY-MM-DDTHH:mm:ss.SSSZ');
				return (aDate < bDate) ? 1 : -1;
			}

			if (item && item.previousRevisions) {
				//show the revisions from the local storage
			}
			else if (item && item.latest_revision && item.latest_revision.revisions) {
				if (item.previousRevisions == null) {
					item.previousRevisions = [];
				}

				jQuery.each( item.latest_revision.revisions, function( index, revurl ){
					var revslug = revurl.substring(revurl.lastIndexOf('/')+1, revurl.length);

					matterItemService.loadRevision(matterSlug, item.slug, revslug).then(
						function success(revision){
							//store revisisions locally
							item.previousRevisions.unshift(revision);
							//Sort array
							item.previousRevisions.sort(SortDescendingByCreationDate);
						},
						function error(/*err*/){
							if( !toaster.toast || !toaster.toast.body || toaster.toast.body!== 'Unable to load previous revision') {
								toaster.pop('error', 'Error!', 'Unable to load previous revision',5000);
							}
						}
					);
				});
			}
			$scope.data.showPreviousRevisions = true;
		};

		/**
		 * Initiate the process of requesting revisions from existing participants or new participants
		 *
		 * @param {Object} checklistItem checklist item to perform action upon
		 *
		 * @private
		 * @method				requestRevision
		 * @memberof			ChecklistCtrl
		 */
		$scope.requestRevision = function( item ) {
			/*var matterSlug = $scope.data.slug;*/

			var modalInstance = $modal.open({
				'templateUrl': '/static/ng/partial/request-revision/request-revision.html',
				'controller': 'RequestrevisionCtrl',
				'resolve': {
					'participants': function () {
						return $scope.data.matter.participants;
					},
					'currentUser': function () {
						return $scope.data.matter.current_user;
					},
					'matter': function () {
						return $scope.data.matter;
					},
					'checklistItem': function () {
						return item;
					}
				}
			});

			modalInstance.result.then(
				function ok(result) {
					item.is_requested = result.is_requested;
					item.responsible_party = result.responsible_party;
				},
				function cancel() {
					//
				}
			);
		};


		/**
		* Remind the responsible user to upload a revision document.
		*
		* @param {Object} The item with the current revision
		*
		* @private
		* @method		    remindRevisionRequest
		* @memberof			ChecklistCtrl
		*/
		$scope.remindRevisionRequest = function( item ) {
			var matterSlug = $scope.data.slug;

			matterItemService.remindRevisionRequest(matterSlug, item.slug).then(
					function success(){
						toaster.pop('success', 'Success!', 'The user has been successfully informed.');
					},
					function error(/*err*/){
						if( !toaster.toast || !toaster.toast.body || toaster.toast.body!== 'Unable to remind the participant.') {
							toaster.pop('error', 'Error!', 'Unable to remind the participant.',5000);
						}
					}
			);
		};


		/**
		* Delete the revision request for the item
		*
		* @param {Object} The item with the current revision
		*
		* @private
		* @method		    deleteRevisionRequest
		* @memberof			ChecklistCtrl
		*/
		$scope.deleteRevisionRequest = function( item ) {
			var matterSlug = $scope.data.slug;

			matterItemService.deleteRevisionRequest(matterSlug, item.slug).then(
					function success(response){
						item.is_requested = response.is_requested;
						item.responsible_party = response.responsible_party;
					},
					function error(/*err*/){
						if( !toaster.toast || !toaster.toast.body || toaster.toast.body!== 'Unable to delete the revision request.') {
							toaster.pop('error', 'Error!', 'Unable to delete the revision request.',5000);
						}
					}
			);
		};


		/**
		 * Initiates the view of a document as modal window.
		 *
		 * @param {Object} revision object to view
		 *
		 * @private
		 * @method				showRevisionDocument
		 * @memberof			ChecklistCtrl
		 */
		$scope.showRevisionDocument = function( revision ) {
			/*var matterSlug = $scope.data.slug;*/
			/*var item = $scope.data.selectedItem;*/

			var modalInstance = $modal.open({
				'templateUrl': '/static/ng/partial/view-document/view-document.html',
				'controller': 'ViewDocumentCtrl',
				'windowClass': 'modal-full',
				'resolve': {
					'matter': function () {
						return $scope.data.matter;
					},
					'checklistItem': function () {
						return $scope.data.selectedItem;
					},
					'revision': function () {
						return revision;
					}
				}
			});

			modalInstance.result.then(
				function ok(/*result*/) {
					//
				},
				function cancel() {
					//
				}
			);
		};

		/**
		 * Initiate the process of requesting reviews from existing participants or new participants
		 *
		 * @param {Object} Revision  object to perform action upon
		 *
		 * @private
		 * @method				requestReview
		 * @memberof			ChecklistCtrl
		 */
		$scope.requestReview = function( revision ) {
			/*var matterSlug = $scope.data.slug;*/
			var item = $scope.data.selectedItem;

			var modalInstance = $modal.open({
				'templateUrl': '/static/ng/partial/request-review/request-review.html',
				'controller': 'RequestreviewCtrl',
				'resolve': {
					'participants': function () {
						return $scope.data.matter.participants;
					},
					'currentUser': function () {
						return $scope.data.matter.current_user;
					},
					'matter': function () {
						return $scope.data.matter;
					},
					'checklistItem': function () {
						return item;
					},
					'revision': function () {
						return revision;
					}
				}
			});

			modalInstance.result.then(
				function ok(review) {
					if (!revision.reviewers) {
						revision.reviewers = [];
					}

					var results = jQuery.grep( revision.reviewers, function( rev ){ return rev.reviewer.username===review.reviewer.username; } );
					if( results.length===0 ) {
						revision.reviewers.push(review);
						$scope.calculateReviewPercentageComplete(item);
					}
				},
				function cancel() {
					//
				}
			);
		};

        /**
		 * Initiate the process of requesting signing from existing participants or new participants
		 *
		 * @param {Object} Revision object to perform action upon
		 *
		 * @private
		 * @method				requestSigning
		 * @memberof			ChecklistCtrl
		 */
		$scope.requestSigning = function( revision ) {
			//var matterSlug = $scope.data.slug;
			var item = $scope.data.selectedItem;

			var modalInstance = $modal.open({
				'templateUrl': '/static/ng/partial/request-signing/request-signing.html',
				'controller': 'RequestsigningCtrl',
				'resolve': {
					'participants': function () {
						return $scope.data.matter.participants;
					},
					'currentUser': function () {
						return $scope.data.matter.current_user;
					},
					'matter': function () {
						return $scope.data.matter;
					},
					'checklistItem': function () {
						return item;
					},
					'revision': function () {
						return revision;
					},
                    'knownSigners': function () {
						return $scope.data.knownSigners;
					}
				}
			});

			modalInstance.result.then(
				function ok(result) {
                    revision.signing = result;
                    revision.signers = result.signers;

                    jQuery.each(result.signers, function(index,signer){
                        var results = jQuery.grep($scope.data.knownSigners, function (s) {
                            return s.username === signer.username;
                        });

					    if( results.length===0 ) {
                             $scope.data.knownSigners.push(signer);
                        }
                    });

                    //$log.debug("Length known signers: " + $scope.data.knownSigners.length);

                    // Open signing dialog
                    $scope.showSigning(revision, null);
				},
				function cancel() {
					//
				}
			);
		};

		/**
		* Remind all review users who haven´t reviewed yet.
		*
		* @param {Object} The item with the current revision
		*
		* @private
		* @method		    remindRevisionReview
		* @memberof			ChecklistCtrl
		*/
		$scope.remindRevisionReview = function( item ) {
			var matterSlug = $scope.data.slug;

			matterItemService.remindRevisionReview(matterSlug, item.slug).then(
					function success(){
						toaster.pop('success', 'Success!', 'All reviewers have been successfully informed.');
					},
					function error(/*err*/){
						if( !toaster.toast || !toaster.toast.body || toaster.toast.body!== 'Unable to remind the participant.') {
							toaster.pop('error', 'Error!', 'Unable to remind the participant.',5000);
						}
					}
			);
		};

		/**
		* Delete the review request for a specific user
		*
		* @param {Object} The item with the current revision
		* @param {Object} The reviewer whos review request should be deleted
		*
		* @private
		* @method		    deleteRevisionReview
		* @memberof			ChecklistCtrl
		*/
		$scope.deleteRevisionReviewRequest = function( item, review ) {
			var matterSlug = $scope.data.slug;
			//var participant = $scope.getParticipantByUrl(participant_url);

			matterItemService.deleteRevisionReviewRequest(matterSlug, item.slug, review).then(
				function success(){
					var index = jQuery.inArray( review, item.latest_revision.reviewers );
					if( index>=0 ) {
						// Remove reviewer from list in RAM array
						item.latest_revision.reviewers.splice(index,1);
						$scope.calculateReviewPercentageComplete(item);
					}
				},
				function error(/*err*/){
					if( !toaster.toast || !toaster.toast.body || toaster.toast.body!== 'Unable to delete the revision review request.') {
						toaster.pop('error', 'Error!', 'Unable to delete the revision review request.',5000);
					}
				}
			);
		};

		/**
		 * Initiates the view of a review as modal window.
		 *
		 * @param {Object} revision object to view
		 * @param {Object} review object to view
		 *
		 * @private
		 * @method				showReview
		 * @memberof			ChecklistCtrl
		 */
		$scope.showReview = function( revision, review ) {
			/*var matterSlug = $scope.data.slug;*/
			var item = $scope.data.selectedItem;

			var modalInstance = $modal.open({
				'templateUrl': '/static/ng/partial/view-review/view-review.html',
				'controller': 'ViewReviewCtrl',
				'windowClass': 'modal-full',
				'resolve': {
					'matter': function () {
						return $scope.data.matter;
					},
					'checklistItem': function () {
						return $scope.data.selectedItem;
					},
					'revision': function () {
						return revision;
					},
					'review': function () {
						return review;
					},
                    'currentUser': function () {
						return $scope.data.usdata.current;
					}
				}
			});

			modalInstance.result.then(
				function ok(/*result*/) {
					$scope.calculateReviewPercentageComplete(item);
					// revert back to previous URL
					$location.path('/checklist/' + $state.params.itemSlug );
				},
				function cancel() {
					// revert back to previous URL
					$location.path('/checklist/' + $state.params.itemSlug );
				}
			);
		};

		$scope.showReviewBySlug = function (revisionSlug, reviewSlug) {
			var matterSlug = $scope.data.slug;
			var item = $scope.data.selectedItem;

			if (item) {
				matterItemService.loadRevision(matterSlug, item.slug, revisionSlug).then(
					function success(revision) {
						/*var reviewUrl;*/
						var reviews = jQuery.grep(revision.reviewers, function (r) {
							return r.slug === reviewSlug;
						});

						if (reviews.length > 0) {
							$scope.showReview(revision, reviews[0]);
						} else if (revision.user_review && revision.user_review.url) {
							// Generate review object
							var review = generateReviewObject( $scope.data.usdata.current, revision.item, revision.user_review);
							// Show review
							$scope.showReview(revision, review);
						} else {
							toaster.pop('warning', 'Review does not exist anymore.');
						}
					},
					function error(/*err*/) {
						toaster.pop('warning', 'Warning!', 'Revision does not exist anymore');
					}
				);
			}
		};

		/**
		 * Generate a user review object
		 * @param  {Object} user       Object representing the user
		 * @param  {String} itemId     Checklist item slug
		 * @param  {Object} userReview REview object containing slug and url
		 * @return {Object}            Review object
		 */
		function generateReviewObject( user, itemId, userReview ) {
			// generate custom review object
			var review = {
				'reviewer': angular.copy(user),
				'item': itemId
			};

			review.reviewer.user_review = userReview;

			return review;
		}

		$scope.calculateReviewPercentageComplete = function( item) {
			if(item && item.latest_revision && item.latest_revision.reviewers && item.latest_revision.reviewers.length>0) {
				var reviews = item.latest_revision.reviewers;
				var completed = 0;

				jQuery.each( reviews, function( index, r ){
					if (r.is_complete===true){
						completed += 1;
					}
				});
				item.review_percentage_complete = parseInt(completed / reviews.length * 100);
				$log.debug(item.review_percentage_complete);

			} else {
				item.review_percentage_complete = null;
			}
		};

        $scope.calculateSigningPercentageComplete = function( item) {
			if(item && item.latest_revision && item.latest_revision.signing && item.latest_revision.signing.signers.length>0) {
				var signers = item.latest_revision.signing.signers;
				var completed = 0;

				jQuery.each( signers, function( index, r ){
					if (r.has_signed===true){
						completed += 1;
					}
				});
				item.signing_percentage_complete = parseInt(completed / signers.length * 100);
				$log.debug(item.signing_percentage_complete);

			} else {
				item.signing_percentage_complete = null;
			}
		};

         $scope.editRevisionStatusTitles = function() {
            var matter = $scope.data.matter;

            var modalInstance = $modal.open({
                'templateUrl': '/static/ng/partial/edit-revision-status/edit-revision-status.html',
                'controller': 'EditRevisionStatusCtrl',
                'backdrop': 'static',
                'resolve': {
                    'currentUser': function () {
                        return matter.current_user;
                    },
                    'matter': function () {
                        return matter;
                    },
                    'customstatusdict': function () {
                        return $scope.data.matter._meta.item.custom_status;
                    },
                    'defaultstatusdict': function () {
                        return $scope.data.matter._meta.item.default_status;
                    }
                }
            });

            modalInstance.result.then(
                function ok(result) {
                    $scope.data.matter._meta.item.custom_status = result;
                }
            );
        };

        /**
		 * Initiates the view for signing as modal window.
		 *
		 * @param {Object} revision object to view
		 * @param {Object} signing object
		 *
		 * @private
		 * @method				showReview
		 * @memberof			ChecklistCtrl
		 */
		$scope.showSigning = function( revision, signer ) {
			var item = $scope.data.selectedItem;

			var modalInstance = $modal.open({
				'templateUrl': '/static/ng/partial/view-signing/view-signing.html',
				'controller': 'ViewSigningCtrl',
				'windowClass': 'modal-full',
				'resolve': {
					'matter': function () {
						return $scope.data.matter;
					},
					'checklistItem': function () {
						return $scope.data.selectedItem;
					},
					'revision': function () {
						return revision;
					},
                    'signer': function () {
						return signer;
					}
				}
			});

			modalInstance.result.then(
				function ok(obj) {
                    $log.debug(obj);

                    if(!revision.signing || revision.signing.is_claimed ===false) {
                        revision.signing = obj;
                        item.signing_percentage_complete = obj.percentage_complete;
                    }
                    //if not, then handled through the callback event from HS
				},
				function cancel() {
					// do nothing
				}
			);
		};

         /**
         * Called when the User signs a document in HelloSign and sets a processing flag the revision
         *
         */
        $("body").on("sign.signed", function (event, param1, param2) {
            $log.debug(event);
            var username = event.username;
            var item = $scope.data.selectedItem;
            var latest_revision = item.latest_revision;
            var signers = latest_revision.signing.signers;

            var results = jQuery.grep(signers, function (obj) {
                return obj.username === username;
            });

            if (results.length > 0) {
                latest_revision.sign_in_progress = true;
                $scope.saveLatestRevision();

                results[0].has_signed = true;
                $scope.calculateSigningPercentageComplete(item);
                $scope.$apply();

                toaster.pop('success', 'Success!', 'The document is being processed.', 5000);
            }
        });

        /**
        * Remind all review users who haven´t reviewed yet.
        *
        * @param {Object} The item with the current revision
        *
        * @private
        * @method           remindRevisionReview
        * @memberof         ChecklistCtrl
        */
        $scope.remindRevisionSigners = function( item ) {
            var matterSlug = $scope.data.slug;

            matterItemService.remindRevisionSigners(matterSlug, item.slug).then(
                    function success(){
                        toaster.pop('success', 'Success!', 'All outstanding signers have been reminded.');
                    },
                    function error(/*err*/){
                        if( !toaster.toast || !toaster.toast.body || toaster.toast.body!== 'Unable to remind the signers.') {
                            toaster.pop('error', 'Error!', 'Unable to remind the signers.',5000);
                        }
                    }
            );
        };

        $scope.deleteSigningRequest = function (revision) {
            if (revision.signing) {
                ezConfirm.create('Delete Signing Request', 'Please confirm you would like to delete this signing request?',
                    function yes() {
                        // Confirmed- delete item
                        matterItemService.deleteSigningRequest(revision.signing).then(
                            function success() {
                                revision.signing = null;
                            },
                            function error(/*err*/) {
                                if (!toaster.toast || !toaster.toast.body || toaster.toast.body !== 'Unable to delete the signing request.') {
                                    toaster.pop('error', 'Error!', 'Unable to delete the signing request.', 5000);
                                }
                            }
                        );
                    }
                );
            }
        };

		/* End revision handling */


		/**
		 * Called when dropping (after dragging) a checklist items or checklist categories.
		 * This method is responsible for getting the order of items within each categry formatted in a way that the API will beable to save the new order.  This medthod also initiates the request to the API to save the calculated order.
		 * Based on https://github.com/angular-ui/ui-sortable (ui-sortable) and http://jqueryui.com/draggable/ (jQuery-ui-draggable).
		 *
		 * @name 				recalculateCategories
		 *
		 * @param {Event} evt Event as passed through from jQuery-ui drag and drop
		 * @param {DOM} ui DOM element
		 *
		 * @private
		 * @method				recalculateCategories
		 * @memberof			ChecklistCtrl
		 */
		function recalculateCategories( /*evt, ui*/ ) {
			var matterSlug = $scope.data.slug;
			var cats = $scope.data.categories;
			var categoryName, items = [], /*item,*/ i;
			var APIUpdate = {
				'categories': [],
				'items': []
			};
			var itemToUpdate = null;

			$scope.data.dragging=false;

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

				items = jQuery.grep( items, function(item){ return item; });

				jQuery.merge(APIUpdate.items, jQuery.map( items, getItemIDs ));

				// Update local data, setting category name
				jQuery.each( items, function( index, item ){
					if (item.category !== categoryName){
						item.category = categoryName;
						itemToUpdate = item;
					}
				});
			}

			matterService.saveSortOrder(matterSlug, APIUpdate).then(
				 function success(){
					//if category changed for an item, save that
					if (itemToUpdate != null){
						matterItemService.update(matterSlug, itemToUpdate).then(
							function success(){
								// do nothing
							},
							function error(/*err*/){
								if( !toaster.toast || !toaster.toast.body || toaster.toast.body!== 'Unable to update the order of items, please reload the page.') {
									toaster.pop('error', 'Error!', 'Unable to update the order of items, please reload the page.', 5000);
								}
							}
					);
					}
				 },
				 function error(/*err*/){
					if( !toaster.toast || !toaster.toast.body || toaster.toast.body!== 'Unable to update the order of items, please reload the page.') {
						toaster.pop('error', 'Error!', 'Unable to update the order of items, please reload the page.', 5000);
					}
				 }
			);
		}


		/**
		 * Broadcasts the event with the given name to the scope. The focus directive is listening to this broadcast.
		 * Timeout is required, because the UI element has to visible to receive the focus. The rendering process
		 * takes a few milliseconds.
		 *
		 * @name 				focus
		 *
		 * @private
		 * @method				focus
		 * @memberof			ChecklistCtrl
		 */
		$scope.focus = function(name) {
			$timeout(function (){
			  $scope.$broadcast('focusOn', name);
			}, 300);
		};


		/**
		 * Receives the event, that the authentication failed and opens the modal to re-login.
		 *
		 * @private
		 * @memberof			ChecklistCtrl
		 */
		$rootScope.$on('authenticationRequired', function(e, isRequired) {
			if(isRequired===true && $scope.data.authenticationModalOpened!==true) {
				$log.debug('opening authentication modal');
				$scope.data.authenticationModalOpened = true;
				var matter = $scope.data.matter;

				var modalInstance = $modal.open({
					'templateUrl': '/static/ng/partial/authentication-required/authentication-required.html',
					'controller': 'AuthenticationRequiredCtrl',
					'backdrop': 'static',
					'resolve': {
						'currentUser': function () {
							return null;//matter.current_user;
						},
						'matter': function () {
							return matter;
						}
					}
				});

				modalInstance.result.then(
					function ok(/*result*/) {
						$scope.data.authenticationModalOpened = false;
					}
				);
			}
		});


		/**
		 * Listens for date changes in the datepicker and stores it in the item
		 *
		 * @memberof			ChecklistCtrl
		 * @private
		 *
		 * @param  newValue,oldValue of the datepicker
		 */
		$scope.$watch('data.dueDatePickerDate', function(newValue/*, oldValue*/) {
			if (newValue instanceof Date) {
				newValue = jQuery.datepicker.formatDate('yy-mm-ddT00:00:00', newValue);
			}
			$log.debug(newValue);

			if ($scope.data.selectedItem && newValue!==$scope.data.selectedItem.date_due) {
				$scope.data.selectedItem.date_due = newValue;
				$scope.saveSelectedItem();
			}
		});

		/**
		 * Default date control options
		 *
		 * @memberof			ChecklistCtrl
		 * @private
		 *
		 * @type {Object}
		 */
		$scope.dateOptions = {
			'year-format': '\'yy\'',
			'starting-day': 1
		};

		/**
		 * Toggle due date value between default (today) and null
		 *
		 * @memberof			ChecklistCtrl
		 * @private
		 *
		 * @param  {Object} item Item which to apply default date
		 */
		$scope.toggleDueDateCalendar = function(item) {
			if(!item.date_due) {
				$scope.data.dueDatePickerDate = new Date();
			} else {
				$scope.data.dueDatePickerDate = null;
			}
		};

		$scope.cancelEvent = function(evt) {
			evt.stopPropagation();
		};

		/**
		 * UI.sortable options for checklist items
		 * @memberof			ChecklistCtrl
		 * @private
		 * @type {Object}
		 */
		$scope.checklistItemSortableOptions = {
			'stop':  recalculateCategories, /* Fires once the drag and drop event has finished */
			'start': function() { $scope.data.dragging=true; $scope.$apply();},
			'connectWith': '.group',
			'dropOnEmpty': true,
			'axis': 'y',
			'distance': 15
		};

		/**
		 * UI.sortable options for checklist categories
		 * @memberof			ChecklistCtrl
		 * @private
		 * @type {Object}
		 */
		$scope.checklistCategorySortableOptions = {
			'update': function( e,ui ) {
				if( ui.item.scope().cat.name===null ) {
					ui.item.sortable.cancel();
				}
			},
			'stop':  recalculateCategories, /* Fires once the drag and drop event has finished */
			'axis': 'y',
			'distance': 15,
			'handle': 'h5'
		};

		var width = $( document ).width();
		if( width<=1200 ) {
			$scope.checklistItemSortableOptions.handle = '.fui-list-columned';
		}


		/**
		 *       _        _   _       _ _               _                              _                     _ _ _
		 *      / \   ___| |_(_)_   _(_) |_ _   _   ___| |_ _ __ ___  __ _ _ __ ___   | |__   __ _ _ __   __| | (_)_ __   __ _
		 *     / _ \ / __| __| \ \ / / | __| | | | / __| __| '__/ _ \/ _` | '_ ` _ \  | '_ \ / _` | '_ \ / _` | | | '_ \ / _` |
		 *    / ___ \ (__| |_| |\ V /| | |_| |_| | \__ \ |_| | |  __/ (_| | | | | | | | | | | (_| | | | | (_| | | | | | | (_| |
		 *   /_/   \_\___|\__|_| \_/ |_|\__|\__, | |___/\__|_|  \___|\__,_|_| |_| |_| |_| |_|\__,_|_| |_|\__,_|_|_|_| |_|\__, |
		 *                                  |___/                                                                        |___/
		 *
		 *
		 */


		 /**
		 * Activates the activity stream for the given type
		 *
		 * @memberof			ChecklistCtrl
		 * @private
		 * @type {Object}
		 */
		$scope.activateActivityStream = function(streamtype){
			if(streamtype === 'item' && $scope.data.selectedItem!==null) {
				$scope.data.streamType = 'item';
			} else {
				$scope.data.streamType = 'matter';
			}

			$scope.initializeActivityStream();
		};

		 /**
		 * Reads the matter activity stream from API.
		 * @memberof			ChecklistCtrl
		 * @private
		 * @type {Object}
		 */
		$scope.initializeActivityStream = function() {
			var matterSlug = $scope.data.slug;

			if ($scope.data.streamType==='matter' || $scope.data.selectedItem===null){
				activityService.matterstream(matterSlug).then(
					 function success(result){
						$scope.data.activitystream = result;
					 },
					 function error(/*err*/){
						if( !toaster.toast || !toaster.toast.body || toaster.toast.body!== 'Unable to read activity matter stream.') {
							toaster.pop('error', 'Error!', 'Unable to read activity matter stream.',5000);
						}
					 }
				);
			} else {
				var itemSlug = $scope.data.selectedItem.slug;

				activityService.itemstream(matterSlug, itemSlug).then(
					 function success(result){
						if($scope.data.selectedItem!==null) {
							$scope.data.activitystream = result;
						}
					 },
					 function error(/*err*/){
						if( !toaster.toast || !toaster.toast.body || toaster.toast.body!== 'Unable to read activity item stream.') {
							toaster.pop('error', 'Error!', 'Unable to read activity item stream.',5000);
						}
					 }
				);
			}

			/*
			//reload activity stream every 60seconds
			$timeout(function (){
				$scope.initializeActivityStream();
			}, 1000 * 60);*/
		};


		/**
		 *     ____                                     _         _                     _ _ _
		 *    / ___|___  _ __ ___  _ __ ___   ___ _ __ | |_ ___  | |__   __ _ _ __   __| | (_)_ __   __ _
		 *   | |   / _ \| '_ ` _ \| '_ ` _ \ / _ \ '_ \| __/ __| | '_ \ / _` | '_ \ / _` | | | '_ \ / _` |
		 *   | |__| (_) | | | | | | | | | | |  __/ | | | |_\__ \ | | | | (_| | | | | (_| | | | | | | (_| |
		 *    \____\___/|_| |_| |_|_| |_| |_|\___|_| |_|\__|___/ |_| |_|\__,_|_| |_|\__,_|_|_|_| |_|\__, |
		 *                                                                                          |___/
		 */

		/**
		 * Creates a new comment
		 *
		 * @memberof			ChecklistCtrl
		 * @private
		 * @type {Object}
		 */
		$scope.submitComment = function() {
			var matterSlug = $scope.data.slug;
			var item = $scope.data.selectedItem;

			item.newcomment = genericFunctions.cleanHTML(item.newcomment);

			// Show activity straight away
			appendActivity('item.comment', item.newcomment, item);

			// Post activity
			commentService.create(matterSlug, item.slug, item.newcomment).then(
				 function success( /*activityItem*/ ){
					// please note: do not refresh activity stream as the new item may not exist yet
					// clear form
					item.newcomment='';
				 },
				 function error(/*err*/){
					if( !toaster.toast || !toaster.toast.body || toaster.toast.body!== 'Unable to create item comment.') {
						toaster.pop('error', 'Error!', 'Unable to create item comment.',5000);
					}
				 }
			);
		};

		/**
		 * appendActivity - formats and inserts activity into activity stream
		 * @param  {String} activityType  template lookup _meta.templates
		 * @param  {String} comment       Comment entered by user
		 * @param  {Object} checklistItem Checlist item that comment is being inserted into
		 */
		function appendActivity( activityType, comment, checklistItem ) {
			var template = matterTemplate( activityType );
			var map = {
				'{{ actor_name }}': $scope.data.usdata.current.name,
				'{{ action_object_name }}': checklistItem.name,
				'{{ timesince }}': 'just now',
				'{{ comment }}': comment
			};
			var content = '<li>' + template + '</li>';

			// Just incase this is not initialised
			$scope.data.activitystream = $scope.data.activitystream || [];

			// Run map
			for( var key in map ) {
				content = content.replace( key, map[key] );
			}

			// Format item
			content = content
						.replace('<a href="">', '<a href="#/checklist/' +  checklistItem.slug + '">');

			// Insert into conversation
			$scope.data.activitystream.unshift( { 'event': content, 'id': null, 'timestamp': 'just now', 'status': 'awaiting' });
		}

		/**
		 * matterTemplate - returns the specific item template as provided by API
		 * @param  {String} templateName name of template
		 * @return {String}              template string as provided by API
		 */
		function matterTemplate( templateName ) {
			var templates = $scope.data.matter._meta.templates;
			var template = '';

			if(templates) {
				template = templates[templateName]||'';
			}

			return template;
		}

	    $scope.showMarkDownInfo = function() {
	      $modal.open({
	        'templateUrl': '/static/ng/partial/markdown/markdown-info.html',
	        'controller': 'MarkdownInfoCtrl'
	      });

	    };
		/* END COMMENT HANDLING */

		/*
		 _____ _ _ _                
		|  ___(_) | |_ ___ _ __ ___ 
		| |_  | | | __/ _ \ '__/ __|
		|  _| | | | ||  __/ |  \__ \
		|_|   |_|_|\__\___|_|  |___/
									
		 */
		/**
		 * applyStatusFilter  filters for checklist based on status 0-4
		 * @param  {Object} filter Filter to apply to latest_revision
		 */
		$scope.applyStatusFilter = function( filter ) {
			// Initialise status filter
			$scope.data.statusFilter = $scope.data.statusFilter||{};

			// Clear other filters
			$scope.data.itemFilter = null;

			if( filter ) {
				for(var key in filter) {
					// Convert { "0": "Draft" } to { "status": 0 }
					$scope.data.statusFilter[key] = parseInt(filter[key]);
				}
			} else {
				// Clear all filters
				$scope.data.itemFilter = null;
				$scope.data.statusFilter = null;
			}
		};
		$scope.clearFilters = function() {
			$scope.matter.itemFilter = null;
			$scope.matter.statusFilter = null;
			$scope.matter.selectedStatusFilter = null;
		};

		/* END COMMENT HANDLING */
}])

/**
 * itemStatusFilter
 * 		apply an item status filter to the array of checklist items within a matter
 * @param  {Array}  items    Array of checklist items
 * @param  {Object} filter   JSON object containing filters
 * @return {Array}  Filtered list of checklist items
 */
.filter('itemStatusFilter', function() {
	'use strict';
	return function(items, filter) {
		var tempClients = [];

		if(!filter) {
			return items;
		}

		angular.forEach(items, function (item) {
			for(var key in filter) {
				if( item.latest_revision && angular.equals( filter[key], item.latest_revision[key] ) ) {
					tempClients.push(item);
				}
			}
		});

		
		return tempClients;
	};
})

/**
 * itemFilter
 * 		apply an item filter to the array of checklist items within a matter (does not apply filter to nested properties)
 * @param  {Array}  items    Array of checklist items
 * @param  {Object} filter   JSON object containing filters
 * @return {Array}  Filtered list of checklist items
 */
.filter('itemFilter', function() {
	'use strict';
	return function(items, filter) {
		var tempClients = [];

		if(!filter) {
			return items;
		}

		angular.forEach(items, function (item) {
			for(var key in filter) {
				if( angular.equals( filter[key], item[key] ) ) {
					tempClients.push(item);
				}
			}
		});

		
		return tempClients;
	};
});
