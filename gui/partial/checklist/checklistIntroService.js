angular.module('toolkit-gui')
.factory('ChecklistIntroService', [ 'IntroService', '$timeout', function( IntroService, $timeout ) {
	'use strict';

	var config = {
		'steps': [

		{
			'element': '#nav-home',
			'intro': "Click here to return to the main list of your matters.",
			'position': 'bottom'
		},
		{
			'element': 'body > div.navbar.navbar-inverse.checklist-nav.ng-scope > div.navbar-header > ul:nth-child(3) > li > a',
			'intro': "Click here to switch to another of your matters.",
			'position': 'bottom'
		},
		{
			'element': '#checklist-nav',
			'intro': "Click here to view the current matter checklist.",
			'position': 'bottom'
		},

		{
			'element': '#discussion-nav',
			'intro': "Private discussions can be undertaken in the discussions section found by clicking here.",
			'position': 'bottom'
		},
		{
			'element': '.checklist-members',
			'intro': "Click here to invite people to participate in this Matter as well as manage current participants.",
			'position': 'bottom'
		},
		{
			'element': '.navbar input[type=search]',
			'intro': "Looking for a specific checklist Item? Find it quickly by using the search tool to search for its name.",
			'position': 'bottom'
		},
		{
			'element': '.navbar .doc-outline-status-',
			'intro': "You can also filter checklist items by their status.",
			'position': 'bottom'
		},
		{
			'element': '.navbar .notifications',
			'intro': "Click here to see your Matter notifications.",
			'position': 'bottom'
		},
		{
			'element': '#nav-requests',
			'intro': "Click here to see outstanding items that have been requested of you.",
			'position': 'bottom'
		},
		{
			'element': '#nav-support',
			'intro': "Click here to start this tutorial again or to contact us.",
			'position': 'bottom'
		},
		{
			'element': '#nav-account',
			'intro': "Click here to manage your account.",
			'position': 'left'
		},

		{
			'element': '#step1',
			'intro': "Checklist items can be organized into categories."
		},
		{
			'element': '#step1 .dropdown-toggle',
			'intro': "Click here to add a new category."
		},
		{
			'element': '#step1 .btn-new-item',
			'intro': "Click here to create a new checklist Item."
		},
		{
			'element': '#checklist-items > span:nth-child(1) > div.categories-list.ng-pristine.ng-valid.ui-sortable > div:nth-child(2) > span:nth-child(2) > ul > li.ng-scope.item-open.ui-sortable-handle.selected > div > div.col-xs-6.item-title',
			'intro': "The currently selected Item is blue in color. Click on another item in any of the other categories to view that item's details."
		},

		{
			'element': '#checklist-detail > div:nth-child(1) > h3.checklist-detail-title > a > span',
			'intro': "Click here to change the name of this item."
		},
		{
			'element': '#checklist-detail > div:nth-child(1) > h3.checklist-detail-title > div.item-description-toggle > small > a > span',
			'intro': "Click here to update the description of this item."
		},
		{
			'element': '#intro-upload-file-menu',
			'intro': "You can upload a file from your local machine or from one of the various cloud providers. These docs should be a .doc .docx or .pdf file",
			'position': 'right'
		},
		{
			'element': '#request-file-button',
			'intro': "Request a document from a matter participant or from an external 3rd-party."
		},
		{
			'element': '#checklist-item-options > a',
			'intro': "Click here to see a menu that allows you to set a Due date for this item or to Delete this item."
		},
		{
			'element': '#close-item > span:nth-child(1)',
			'intro': "Click here to mark this item as Closed."
		},
		{
			'element': '#checklist-detail > div:nth-child(1) > div.ng-scope > div > h4',
			'intro': 'You can drag and drop a document from your local computer here.'
		},
		{
			'element': '#checklist-detail > div.tasks-wrapper.ng-isolate-scope > div.item-subheading > a',
			'intro': "Click here to create a Task and assign it to a matter participant. You can also set due dates."
		},
		{
			'element': '#checklist-detail > div.attachments-wrapper.ng-isolate-scope > div.item-subheading > a',
			'intro': "Click here to upload a supporting Attachment for this item. Attachments can be any file type."
		},


		{
			'element': '#checklist-activity > h4.nav-activity-panel > a:nth-child(1)',
			'intro': "Click here to view activity for this Item."
		},
		{
			'element': '#checklist-activity > h4.nav-activity-panel > a:nth-child(2)',
			'intro': "Click here to view all activity that has taken place within the matter."
		},
		{
			'element': '#checklist-activity .new-message',
			'intro': "Chat with participants about items, documents and revisions."
		}
		]
	};

	return {
		/**
		 * Displays intro
		 * @public
		 * @method				showIntro
		 * @memberof			PusherService
		 */

		 'showIntro': function( reloadLess ) {
		 	IntroService.show( config, 1 );
		 	$timeout(function(){
		 		if(reloadLess && less) {
		 			less.refresh();
		 		}
		 	},100);
		 }
		};
	}]);