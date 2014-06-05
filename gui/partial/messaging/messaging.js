angular.module('toolkit-gui')
/**
 * @class MessagingCtrl
 * @classdesc                           Controller for retreiving and display checklists
 *
 * @param  {Object} $scope                Contains the scope of this controller
 * @param  {Object} $rootScope            Rootscope variable
 * @param  {Object} $routeParams          Object that provides access to Angular route parameters
 * @param  {Function} ezConfirm           A wrapper that simulates the native confirm dialog
 * @param  {Function} toaster             A directive that provides the ability to show status messages to the end user
 * @param  {Function} $modal              A directive that provides a wrapper for displaying and managing dialogs
 * @param  {Object} matterService         An angular service designed to work with MATTER API end-points
 * @param  {Object} participantService    A custom angular service designed to work with USER end-points
 * @param  {Object} activityService       A custom angular service designed to work with ACTIVITY end-points
 * @param  {Object} userService           A custom angular service designed to work with USER end-points
 * @param  {Object} itemCommentService        A custom angular service designed to work with COMMENT end-points
 * @param  {Function} $timeout            An angular wrapper for setTimeout that allows angular to keep track of when to update views
 */
.controller('MessagingCtrl', [
    '$scope',
    '$rootScope',
    '$routeParams',
    '$state',
    '$location',
    '$sce',
    '$compile',
    '$route',
    'smartRoutes',
    'ezConfirm',
    'toaster',
    '$modal',
    'baseService',
    'matterService',
    'participantService',
    'userService',
    'matterCommentService',
    '$timeout',
    '$log',
    '$window',
    '$q',
    'Intercom',
    'INTERCOM_APP_ID',
    function($scope,
             $rootScope,
             $routeParams,
             $state,
             $location,
             $sce,
             $compile,
             $route,
             smartRoutes,
             ezConfirm,
             toaster,
             $modal,
             baseService,
             matterService,
             participantService,
             userService,
             matterCommentService,
             $timeout,
             $log,
             $window,
             $q,
             Intercom,
             INTERCOM_APP_ID){
        'use strict';
        /**
         * Scope based data for the checklist controller
         * @memberof            MessagingCtrl
         * @private
         * @type {Object}
         */
        var routeParams = smartRoutes.params();
        $scope.data = {
            'slug': routeParams.matterSlug,
            'matter': null,
            'comment_list': [],
            'users': [],
            'usdata': userService.data(),
            'streamType': 'matter',
            'history': {},
            'page': 'messaging'
        };
        //debugger;


        if( $scope.data.slug && $scope.data.slug!=='' && $scope.data.matterCalled==null) {
            $scope.data.matterCalled = true;

            matterService.get( $scope.data.slug ).then(
                function success( singleMatter ){
                    $scope.data.matter = singleMatter;
                    //set matter in the services
                    matterService.selectMatter(singleMatter);
                    $scope.initialiseMatter( singleMatter );

                    userService.setCurrent( singleMatter.current_user, singleMatter.lawyer );

                    $scope.initialiseIntercom(singleMatter.current_user);
                },
                function error(/*err*/){
                    toaster.pop('error', 'Error!', 'Unable to load matter',5000);
                    // @TODO: redirect user maybe?
                }
            );
        }

        /**
         * Handles the event when the URL params changes inside the ng app
         *
         * @private
         * @memberof            MessagingCtrl
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
         * @memberof            MessagingCtrl
         * @method              handleUrlState
         */
        $scope.handleUrlState = function () {
        };


        /**
         * Splits the matter items into seperate arrays for the purpose of displaying seperate sortable lists, where items can be dragged
         * @name    initialiseMatter
         * @param  {Object} matter Full matter object as recieved from API
         * @private
         * @memberof            MessagingCtrl
         * @method          initialiseMatter
         */
        $scope.initialiseMatter = function( matter ) {
            var /*i, */categoryName = null, categories = [], items = [];

            // Items with blank category name
            if( matter && matter.categories ) {
                $scope.data.matter = matter;

                matterCommentService.list( matter.slug ).then(
                     function success( result ){
                        $scope.data.comment_list = result;
                     },
                     function error(/*err*/){
                        if( !toaster.toast || !toaster.toast.body || toaster.toast.body!== 'Unable to read activity matter stream.') {
                            toaster.pop('error', 'Error!', 'Unable to read activity matter stream.',5000);
                        }
                     }
                );

                $scope.handleUrlState();
            } else {
                // Display error
                toaster.pop('warning', 'Unable to load matter details',5000);
            }
        };


        /**
         * Inits the intercom interface
         *
         * @name    initialiseIntercom
         * @param  {Object} Current user object
         * @private
         * @memberof            MessagingCtrl
         * @method          initialiseIntercom
         */
        $scope.initialiseIntercom = function(currUser){
            $log.debug(currUser);

            Intercom.boot({
                user_id: currUser.username,
                email: currUser.email,
                first_name: currUser.first_name,
                last_name: currUser.last_name,
                firm_name: currUser.firm_name,
                verified: currUser.verified,
                type: currUser.user_class,
                app_id: INTERCOM_APP_ID,
                created_at: (new Date(currUser.date_joined).getTime()/1000),
                matters_created: currUser.matters_created,
                user_hash: currUser.intercom_user_hash,
                widget: {
                    activator: '.intercom',
                    use_counter: true
                }
            });

            //Intercom.show();
        };

}]);
