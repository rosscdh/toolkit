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
 * @param  {Function} $timeout            An angular wrapper for setTimeout that allows angular to keep track of when to update views
 */
.controller('ChecklistCtrl', [
	'$scope',
	'$rootScope',
	'$routeParams',
	'smartRoutes',
	'ezConfirm',
	'toaster',
	'$modal',
	'matterService',
	'matterItemService',
	'matterCategoryService',
	'participantService',
	'$timeout',
	function($scope, $rootScope, $routeParams, smartRoutes, ezConfirm, toaster, $modal, matterService, matterItemService, matterCategoryService, participantService, $timeout){
		/**
		 * Scope based data for the checklist controller
		 * @memberof			ChecklistCtrl
		 * @private
		 * @type {Object}
		 */
		
		var routeParams = smartRoutes.params();
		$scope.data = {
			'slug': routeParams.matterSlug,
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
					$scope.initialiseMatter( singleMatter );
				},
				function error(err){
					toaster.pop('error', "Error!", "Unable to load matter");
					// @TODO: redirect user maybe?
				}
			);
		}

		/**
		 * Spilts the matter items into seperate arrays for the purpose of displaying seperate sortable lists, where items can be dragged
		 * @name	initialiseMatter
		 * @param  {Object} matter Full matter object as recieved from API
		 * @private
		 * @memberof			ChecklistCtrl
		 * @method			initialiseMatter
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
		$scope.submitNewItem = function(category) {
		   var matterSlug = $scope.data.slug;

		   if ($scope.data.newItemName) {
			 matterItemService.create(matterSlug, $scope.data.newItemName, category.name).then(
				 function success(item){
					category.items.unshift(item);
					$scope.data.newItemName = '';
				 },
				 function error(err){
					toaster.pop('error', "Error!", "Unable to create new item");
				 }
			 );
		   }
		};

		/**
		 * Sets the currently selected item to the one passed through to this method
		 * 
		 * @param  {Object}	item		Category object contains category name (String)
		 * @param {Object}	category	object representing the category of the item to select
		 * @private
		 * @method						selectItem
		 * @memberof					ChecklistCtrl
		 */
		$scope.selectItem = function(item, category) {
			$scope.data.selectedItem = item;
			$scope.data.selectedCategory = category;

			//Reset controls
			$scope.data.showEditItemDescriptionForm = false;
			$scope.data.showEditItemTitleForm = false;
            $scope.data.showPreviousRevisions = false;
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

			if ($scope.data.selectedItem) {
				matterItemService.update(matterSlug, $scope.data.selectedItem).then(
					function success(item){
						//do nothing
					},
					function error(err){
						toaster.pop('error', "Error!", "Unable to update item");
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
        $scope.getParticipantByUrl = function (participanturl, showOnlyInitials){
             if ($scope.data.loadedParticipants == null) {
                 $scope.data.loadedParticipants = {};
             }

             function printUser(participant){
                 if (showOnlyInitials === true && participant.initials != null && participant.initials.length>0) {
                     return '(' + participant.initials + ')';
                 } else if (showOnlyInitials === true && participant.initials == null) {
                     return '';
                 }

                 if (participant.last_name != null && participant.last_name.length >0) {
                     return participant.first_name + ' ' + participant.last_name;
                 } else {
                     return participant.email;
                 }
             }

             //only load user from api, if not already loaded
             if (participanturl != null && $scope.data.loadedParticipants[participanturl] == null) {
                 $scope.data.loadedParticipants[participanturl] = {};

                 participantService.getByURL(participanturl).then(
                     function success(participant){
                         //store user in dict with url as key
                         $scope.data.loadedParticipants[participanturl] = participant;
                         return printUser(participant);
                     },
                     function error(err){
                         return '';
                     }
                 );
             } else if (participanturl != null && $scope.data.loadedParticipants[participanturl] != null){
                 return printUser($scope.data.loadedParticipants[participanturl]);
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
		$scope.deleteCategory = function(cat) {
			var matterSlug = $scope.data.slug;

			matterCategoryService.delete(matterSlug, cat).then(
				function success(){
					var index = jQuery.inArray( cat, $scope.data.categories );
					if( index>=0 ) {
						// Remove item from in RAM array
						$scope.data.categories.splice(index,1);
					}

					if (cat === $scope.data.selectedCategory){
						$scope.data.selectedItem = null;
					}
				},
				function error(err){
					toaster.pop('error', "Error!", "Unable to delete category");
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
				function error(err){
					toaster.pop('error', "Error!", "Unable to edit category");
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

			matterItemService.uploadRevision( matterSlug, itemSlug, files ).then(
				function success( revision ) {
					revision.uploaded_by = matterService.data().selected.current_user;
					item.latest_revision = revision;

                    $scope.data.uploading = false;
                    //Reset previous revisions
                    item.previousRevisions = null;
                    $scope.data.showPreviousRevisions = false;
				},
				function error(err) {
                    $scope.data.uploading = false;
					toaster.pop('error', "Error!", "Unable to upload revision");
				}
			);
		};

		/**
		 * Initiate the file upload process
		 * @param  {Array} $files HTML5 files object
		 * @param  {Object} item   Matter checklist item object
		 */
		$scope.onFileDropped = function( $files, item ) {
			var matterSlug = $scope.data.slug;
			var itemSlug = item.slug;

			item.uploading = true;

			matterItemService.uploadRevisionFile( matterSlug, itemSlug, $files ).then(
				function success( revision ) {
					revision.uploaded_by = matterService.data().selected.current_user;
					item.latest_revision = revision;

					//Reset previous revisions
					item.previousRevisions = null;
					$scope.data.showPreviousRevisions = false;
					item.uploadingPercent = 0;
					item.uploading = false;
				},
				function error(err) {
					toaster.pop('error', "Error!", "Unable to upload revision");
					item.uploading = false;
				},
				function progress( num ) {
					item.uploadingPercent = num;
				}
			);
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
					function success(item){
						//do nothing
					},
					function error(err){
						toaster.pop('error', "Error!", "Unable to update revision");
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
									//First revision in array is the latest one
									matterItemService.loadRevision(matterSlug, item.slug, item.latest_revision[0]).then(
										function success(revision){
											item.latest_revision = revision;
										},
										function error(err){
											toaster.pop('error', "Error!", "Unable to set new current revision");
										}
									);
								} else {
									item.latest_revision = null;
								}

								//Reset previous revisions
								item.previousRevisions = null;
								$scope.data.showPreviousRevisions = false;
							},
							function error(err){
								toaster.pop('error', "Error!", "Unable to delete revision");
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
                var aDate = moment(a.date_created, "YYYY-MM-DDTHH:mm:ss.SSSZ");
                var bDate = moment(b.date_created, "YYYY-MM-DDTHH:mm:ss.SSSZ");
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
                        function error(err){
                            toaster.pop('error', "Error!", "Unable to load previous revision");
                        }
                    );
				});
			}
            $scope.data.showPreviousRevisions = true;
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


		/**
		 * Initiate the process of requesting reviews from existing participants or new participants
		 * 
		 * @param {Object} checklistItem checklist item to perform action upon
		 * 
		 * @private
		 * @method				requestRevision
		 * @memberof			ChecklistCtrl
		 */
		$scope.requestRevision = function( checklistItem ) {
            var matterSlug = $scope.data.slug;
			var item = $scope.data.selectedItem;

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
						return checklistItem;
					}
				}
			});

			modalInstance.result.then(
				function ok(result) {
                    var requestdata = {
                        'responsible_party': result.participant.url,
                        'note': result.message
                    };

                    matterItemService.requestRevision(matterSlug, item.slug, requestdata).then(
							function success(response){
                                item.status = response.status;
                                item.responsible_party = response.responsible_party;
							},
							function error(err){
								toaster.pop('error', "Error!", "Unable to request a revision.");
							}
                    );
				},
				function cancel() {
					//
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
            var matterSlug = $scope.data.slug;
			var item = $scope.data.selectedItem;

			var modalInstance = $modal.open({
				'templateUrl': '/static/ng/partial/view-document/view-document.html',
				'controller': 'ViewDocumentCtrl',
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
				function ok(result) {
					//
				},
				function cancel() {
					//
				}
			);
		};

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
		 * UI.sortable options for checklist items
		 * @memberof			ChecklistCtrl
		 * @private
		 * @type {Object}
		 */
		$scope.checklistItemSortableOptions = {
			'stop':  recalculateCategories, /* Fires once the drag and drop event has finished */
			'connectWith': ".group",
			'axis': 'y',
			'distance': 15,
			'delay': 100
		};

		/**
		 * UI.sortable options for checklist categories
		 * @memberof			ChecklistCtrl
		 * @private
		 * @type {Object}
		 */
		$scope.checklistCategorySortableOptions = {
			'stop':  recalculateCategories, /* Fires once the drag and drop event has finished */
			'axis': 'y',
			'distance': 15,
			'delay': 100
		};

}]);
