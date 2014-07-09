angular.module('toolkit-gui')
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