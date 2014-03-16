angular.module('toolkit-gui')
/**
 * @class RequestreviewCtrl
 * @classdesc 		                      Responsible for managing and requesting the API to request a new revision
 * @param  {Object} $scope                Contains the scope of this controller
 * @param  {Function} $modalInstance      Provides access to close and cancel methods
 * @param  {Array} participants           List of participants within a matter
 * @param  {Object} currentUser           The current user
 * @param  {Object} revision              A specific revision object, upon which to execute request for review
 * @param  {Object} matter                The matter for which participants will be invited
 * @param  {Object} participantService    Contains methods to make participant related requests to the API
 * @param  {Function} toaster             Provides a handle to show/hide UI toasters
 * @param  {Function} anon                Controller function
 */
.controller('RequestreviewCtrl',[
	'$scope',
	'$modalInstance',
	'participants',
	'currentUser',
	'matter',
	'revision',
	'participantService',
	'toaster',
	function($scope, $modalInstance, participants, currentUser, matter, revision, participantService, toaster){


		/**
		 * In scope variable containing a list of participants within this matter. This is passed through from the originating controller.
		 * This object is cloned, and therefore changes to this object will not be refected in thr originating object.
		 * 
		 * @memberof RequestreviewCtrl
		 * @type {Array}
		 * @private
		 */
		$scope.participants = angular.copy(participants);
		/**
		 * In scope variable containing details about the current user. This is passed through from the originating controller.
		 * @memberof RequestreviewCtrl
		 * @type {Object}
		 * @private
		 */
		$scope.currentUser = currentUser;
		/**
		 * In scope variable containing details about the matter. This is passed through from the originating controller.
		 * @memberof RequestreviewCtrl
		 * @type {Object}
		 * @private
		 */
		$scope.matter = matter;

		/**
		 * In scope variable containing details about the specific checklist item, with which to make the request
		 * @memberof RequestreviewCtrl
		 * @type {Object}
		 * @private
		 */
		$scope.revision = revision;

		/**
		 * Scope based data for this controller
		 * @memberof			RequestreviewCtrl
		 * @private
		 * @type {Object}
		 */
		$scope.data = {
			'inviteExternal': false,
			'request': {
				'person': null,
				'email': null,
				'message': null
			}
		};

		/**
		 * Close dialog on afirmative user initiated event (.e.g. click's OK button).
		 * Returns updated participants array.
		 *
		 * @name				ok
		 * 
		 * @private
		 * @method				ok
		 * @memberof			RequestreviewCtrl
		 */
		$scope.ok = function () {
			$modalInstance.close( $scope.participants );
		};

		/**
		 * Close dialog on afirmative user initiated event (.e.g. click's OK button).
		 * Returns nothing
		 *
		 * @name				cancel
		 * 
		 * @private
		 * @method				cancel
		 * @memberof			RequestreviewCtrl
		 */
		$scope.cancel = function () {
			$modalInstance.dismiss('cancel');
		};

          /**
		 * Checks if a user exists with the entered mailaddress and activates the input
         * fields for first and last name if not.
		 *
		 * @name				checkIfUserExists
		 *
		 * @private
		 * @method				checkIfUserExists
		 * @memberof			ParticipantInviteCtrl
		 */
        $scope.checkIfUserExists = function () {
            if ($scope.data.request.email != null && $scope.data.request.email.length>0) {
                $scope.data.validationError = false;

                participantService.getByEmail( $scope.data.request.email ).then(
                    function success(response) {
                        if (response.count===1){
                            $scope.data.request.isNew = false;
                            $scope.data.request.participant = response.results[0];
                        } else {
                            $scope.data.request.isNew = true;
                            $scope.data.request.participant = null;
                        }
                    },
                    function error() {
                        toaster.pop('error', "Error!", "Unable to load participant");
                    }
                );
            } else {
                $scope.data.validationError = true;
                $scope.data.request.isNew = false;
                $scope.data.request.participant = null;
                jQuery("#requestParticipant").attr('disabled','');
            }
        };

		/**
		 * Initiates request to invite and receive the user.
		 *
		 * @name				request
		 * 
		 * @param  {Object} person	User object
		 * @private
		 * @method				request
		 * @memberof			RequestreviewCtrl
		 */
		$scope.request = function() {
			var person = $scope.data.request.person&&$scope.data.request.person!==''?$scope.data.request.person:null;

            var result = { 'email': $scope.data.request.email,
                           'username': person,
                           'first_name': $scope.data.request.first_name,
                           'last_name': $scope.data.request.last_name,
                           'message': $scope.data.request.message };

            $modalInstance.close( result );

            /**
            if (email != null && email.length > 0) {
                participantService.invite($scope.matter.slug, $scope.data.request).then(
                    function success(response){
                        participantService.getByURL(response.url).then(
                            function success(participant){
                                $modalInstance.close( { 'participant': participant, 'message': message } );
                            },
                            function error(err){
                                toaster.pop('error', "Error!", "Unable to receive participant");
                            }
                        );
                    },
                    function error(err){
                        toaster.pop('error', "Error!", "Unable to invite participant");
                    }
                );
            } else {
                participantService.getByUsername(person).then(
                    function success(participant){
                        $modalInstance.close( { 'participant': participant, 'message': message } );
                    },
                    function error(err){
                        toaster.pop('error', "Error!", "Unable to receive participant");
                    }
                );
            }*/
		};

		/**
		 * Determines if request revision for is valid or not.
		 * This is a little complex as the end user can select an existing user or enter an email address
		 *
		 * @name				invalid
		 * 
		 * @private
		 * @method				invalid
		 * @memberof			RequestreviewCtrl
		 */
		$scope.invalid = function() {
			return !$scope.data.request.person&&!$scope.data.request.email;
		};
	}
]);