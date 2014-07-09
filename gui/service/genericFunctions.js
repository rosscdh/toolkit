/* Generic Services */
angular.module('toolkit-gui')
.factory("genericFunctions", [ '$sanitize', 'Intercom', 'INTERCOM_APP_ID', function( $sanitize, Intercom, INTERCOM_APP_ID ) {
 return {
	'cleanHTML': function( str ) {
		if( typeof(str)==='string' ) {
			return str.replace(/(<([^>]+)>)/ig, '');
		} else {
			return '';
		}
	},

	/**
	 * Inits the intercom interface
	 *
	 * @name	initialiseIntercom
	 * @param  {Object} Current user object
	 * @private
	 * @memberof			genericFunctions
	 * @method			initialiseIntercom
	 */
	'initialiseIntercom': function(currUser){
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
	}
 };
}]);