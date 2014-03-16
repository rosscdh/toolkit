angular.module('toolkit-gui')
/**
 * @class ParticipantInviteCtrl
 * @classdesc 		                      Responsible for managing and requesting the API to invite participants into a matter
 * @param  {Object} $scope                Contains the scope of this controller
 * @param  {Function} $modalInstance      Provides access to close and cancel methods
 * @param  {Array} participants           List of participants within a matter
 * @param  {Object} currentUser           The current user
 * @param  {Object} matter                The matter for which participants will be invited
 * @param  {Object} participantService    Contains methods to make participant related requests to the API
 * @param  {Function} toaster             Provides a handle to show/hide UI toasters
 * @param  {Function} anon                Controller function
 */
.controller('ParticipantInviteCtrl',[
	'$scope',
	'$modalInstance',
	'participants',
	'currentUser',
	'matter',
	'participantService',
	'toaster',
	function($scope, $modalInstance, participants, currentUser, matter, participantService, toaster){
		/**
		 * In scope variable containing a list of participants within this matter. This is passed through from the originating controller.
		 * @memberof ParticipantInviteCtrl
		 * @type {Array}
		 * @private
		 */
		$scope.participants = participants;
		/**
		 * In scope variable containing details about the current user. This is passed through from the originating controller.
		 * @memberof ParticipantInviteCtrl
		 * @type {Object}
		 * @private
		 */
		$scope.currentUser = currentUser;
		/**
		 * In scope variable containing details about the matter. This is passed through from the originating controller.
		 * @memberof ParticipantInviteCtrl
		 * @type {Object}
		 * @private
		 */
		$scope.matter = matter;

		/**
		 * Scope based data for this controller
		 * @memberof			ParticipantInviteCtrl
		 * @private
		 * @type {Object}
		 */
		$scope.data = {
			'invitee': { 'email': '', 'message': '', 'isNew': false }
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
            if ($scope.data.invitee.email != null && $scope.data.invitee.email.length>0) {
                $scope.data.validationError = false;

                participantService.getByEmail( $scope.data.invitee.email ).then(
                    function success(response) {
                        if (response.count===1){
                            $scope.data.invitee.isNew = false;
                            $scope.data.invitee.participant = response.results[0];

                            jQuery("#addParticipant").removeAttr('disabled');
                        } else {
                            $scope.data.invitee.isNew = true;
                            $scope.data.invitee.participant = null;

                            jQuery("#addParticipant").removeAttr('disabled');
                        }
                    },
                    function error() {
                        toaster.pop('error', "Error!", "Unable to load participant");
                    }
                );
            } else {
                $scope.data.validationError = true;
                $scope.data.invitee.isNew = false;
                $scope.data.invitee.participant = null;
                jQuery("#addParticipant").attr('disabled','');
            }
        };

		/**
		 * Initiates request to API to invite a person or an already registered user
		 *
		 * @name				invite
		 * 
		 * @private
		 * @method				invite
		 * @memberof			ParticipantInviteCtrl
		 */
		$scope.invite = function () {
			participantService.invite( matter.selected.slug, $scope.data.invitee ).then(
				function success(response) {
                    participantService.getByURL(response.url).then(
                        function success(participant){
                            $scope.participants.push(participant);
                        },
                        function error(err){
                            toaster.pop('error', "Error!", "Unable to load participant");
                        }
                    );
				},
				function error() {
					toaster.pop('error', "Error!", "Unable to invite this person to particpate, please try again in a few moments");
				}
			);
		};

		/**
		 * Initiates request to API to revoke access for an already registered user
		 *
		 * @name				revoke
		 * 
		 * @param  {Object} person	User object
		 * @private
		 * @method				revoke
		 * @memberof			ParticipantInviteCtrl
		 */
		$scope.revoke = function ( person ) {
			participantService.revoke( matter.selected.slug, person ).then(
				function success() {
					var index = jQuery.inArray( person, $scope.participants );
                    if( index>=0 ) {
                        // Remove user from in RAM array
                        $scope.participants.splice(index,1);
                    }
				},
				function error() {
					toaster.pop('error', "Error!", "Unable to revoke the access of this person");
				}
			);
		};

		/**
		 * Close dialog on afirmative user initiated event (.e.g. click's OK button).
		 * Returns updated participants array.
		 *
		 * @name				ok
		 * 
		 * @private
		 * @method				ok
		 * @memberof			ParticipantInviteCtrl
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
		 * @memberof			ParticipantInviteCtrl
		 */
		$scope.cancel = function () {
			$modalInstance.dismiss('cancel');
		};

		/*
		$scope.compareUrls = function( urla, urlb ) {
			console.log(urla, urlb, urla.indexOf(urlb)>=0||urlb.indexOf(urla)>=0);
			return urla.indexOf(urlb)>=0||urlb.indexOf(urla)>=0;
		};
		*/
	}
]);

// $modalInstance, items