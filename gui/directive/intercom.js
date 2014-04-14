/**
 * https://github.com/gdi2290/angular-intercom/blob/master/example/index.html
 * Directive for intercom
 * Just needed if the current user might change without a page reload
 * NOT ACTIVATED AT THE MOMENT
 */
angular.module('toolkit-gui').directive("intercom",['$cookieStore', 'Intercom', 'INTERCOM_APP_ID', '$window', '$log',
    function ($cookieStore, Intercom, INTERCOM_APP_ID, $window, $log) {
        return {
        restrict: 'A',
        scope: {
            userId: '@',
            userEmail: '@'
        },
        link: function (scope, element, attrs) {
            scope.$watch('userId + userEmail', function (newVal, oldVal) {
                var userId = $cookieStore.get("userId");
                var accountId = $cookieStore.get("accountId");

                if (accountId && userId) {
                    $log.debug("intercom watcher got fired");
                    var userEmail = $cookieStore.get("userEmail");
                    var createdAt = $cookieStore.get("createdAt");
                    var hash = $window.CryptoJS.HmacSHA256(accountId + '_' + userId, INTERCOM_APP_ID);

                    Intercom.update({
                        email: userEmail,
                        user_id: accountId + '_' + userId,
                        created_at: createdAt,
                        app_id: INTERCOM_APP_ID,
                        user_hash: hash.toString()
                    });

                } //  end if
            }); // end watch


        } // end link
    }; // end return
}]);