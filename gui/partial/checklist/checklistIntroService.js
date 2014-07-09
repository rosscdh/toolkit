angular.module('toolkit-gui')
.factory('ChecklistIntroService', [ 'IntroService', '$timeout', function( IntroService, $timeout ) {
	'use strict';

	var config = {
		'steps': [
			{
				'element': '#step1',
				'intro': "Checklist items are organised into categories."
			},
			{
				'element': '#step1 .dropdown-toggle',
				'intro': "Add new categories."
			},
			{
				'element': '#step1 .btn-new-item',
				'intro': "Create new checklist items."
			},
			{
				'element': '.checklist-members',
				'intro': "Invite people to participate in your workspace."
			},
			{
				'element': '.navbar input[type=search]',
				'intro': "Find checklist items quickly with search."
			},
			{
				'element': '.navbar .doc-outline-status-',
				'intro': "Filter checklist items by status."
			},
			{
				'element': '.navbar .notifications span',
				'intro': "See when things change."
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