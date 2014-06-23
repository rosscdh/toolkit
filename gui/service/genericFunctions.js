/* Generic Services */
angular.module('toolkit-gui')
.factory("genericFunctions", [ '$sanitize', function($sanitize) {
 return {
	'cleanHTML': function( str ) {
		if( typeof(str)==='string' ) {
			return str.replace(/(<([^>]+)>)/ig, '');
		} else {
			return '';
		}
	},
	/*
	 * Given an array of items select the first item if one is not already selected
	 * @param	{Object}	existingItem	the existing selected item, which may be undefined or null or an object
	 * @param	{Array}		items			array of items to select from
	 * @param	{Object}	category		category object, which contains the item and the category
	 *
	 * @return	{Object}					either the selected object or null
	 */
	'selectFirstitem': function( existingItem, items, category ) {
		if(typeof(existingItem)==='object') {
			return existingItem;
		} else if( angular.isArray(items) && items.length > 0 ) {
			return { 'item': items[0], 'category': category };
		} else {
			return null;
		}
	}
 };
}]);