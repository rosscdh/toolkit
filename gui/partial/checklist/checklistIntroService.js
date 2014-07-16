angular.module('toolkit-gui')
.factory('ChecklistIntroService', [ 'IntroService', '$timeout', function( IntroService, $timeout ) {
	'use strict';

	var config = {
		'steps': [
			{
				'element': '#step1',
				'intro': "Checklist items are organized into categories."
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
				'element': '.checklist-members',
				'intro': "Click here to invite people to participate in this Matter."
			},
			{
				'element': '.navbar input[type=search]',
				'intro': "Looking for a specific checklist Item? Find it quickly by using the search tool."
			},
			{
				'element': '.navbar .doc-outline-status-',
				'intro': "You can even filter checklist items by their status."
			},
			{
				'element': '.navbar .notifications span',
				'intro': "Click here to see your Matter notifications."
			},
			{
				'element': '#checklist-activity h4',
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