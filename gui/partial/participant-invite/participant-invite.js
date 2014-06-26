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
	'$location',
	'$log',
	'$window',
	function($scope, $modalInstance, participants, currentUser, matter, participantService, toaster, $location, $log, $window){
		'use strict';

		/**
		 * In scope variable containing a list of participants within this matter. This is passed through from the originating controller.
		 * @memberof ParticipantInviteCtrl
		 * @type {Array}
		 * @private
		 */
		$scope.participants = participants;
        $scope.permissionsChanged = false;
        $scope.originalPermissions = null;


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
			'invitee': { 'email': '', 'message': '', permissions: {
                'manage_participants': false,
                'manage_document_reviews': false,
                'manage_items': false,
                'manage_signature_requests': false,
                'manage_clients': false
            }},
            'isNew': false,
            'selectedUser': null,
            'selectedUserPermissionsBackup': null,
            'requestLoading': false,
            'showAddButton': false

		};

        $scope.selectUser = function( person ) {
        	// Re-apply original permissions if required, the concept here is that if I don't click the 
        	if( $scope.data.selectedUser && $scope.data.selectedUserPermissionsBackup ) {
        		$scope.data.selectedUser.permissions = $scope.data.selectedUserPermissionsBackup; // Reset previosuly selected user permissions
        	}
        	// Update selected User with new selected user
        	$scope.data.selectedUser=person;
        	$scope.data.selectedUserPermissionsBackup = angular.copy(person.permissions);

        	// Permissions changed flag for GUI updates
        	$scope.permissionsChanged=false;
        };

        if (angular.isArray(participants) && (participants.length > 0)) {
        	$scope.selectUser(participants[0]);
        }

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
        $scope.checkIfUserExists = function (lawyerObligatory) {
            if ($scope.data.invitee.email != null && $scope.data.invitee.email.length>0) {
                $scope.data.validationError = false;
                $scope.data.requestLoading = true;

                participantService.getByEmail( $scope.data.invitee.email ).then(
                    function success(response) {
                        $scope.data.requestLoading = false;

                        if (response.count===1){
                            var p = response.results[0];

                            $scope.data.isNew = false;
                            $scope.data.isParticipant = false;
                            $scope.data.isLawyer = false;

                            $scope.data.participant = p;
                            $scope.data.invitee.first_name = p.first_name;
                            $scope.data.invitee.last_name = p.last_name;

                        } else {
                            $scope.data.isParticipant = false;
                            $scope.data.isLawyer = false;
                            $scope.data.isNew = true;
                            $scope.data.participant = null;
                        }
                    },
                    function error() {
                        $scope.data.requestLoading = false;
                        toaster.pop('error', 'Error!', 'Unable to load participant', 3000);
                    }
                );
            } else {
                $scope.data.validationError = true;
                $scope.data.isNew = false;
                $scope.data.participant = null;
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
            if($scope.data.showAddLawyer===true){
                $scope.data.invitee.user_class='lawyer';
                $scope.data.invitee.role='colleague';
            } else {
                $scope.data.invitee.user_class='customer';
                $scope.data.invitee.role='client';
            }
            $scope.data.requestLoading = true;

			participantService.invite( $scope.matter.slug, $scope.data.invitee ).then(
				function success(participant) {
                    $scope.data.requestLoading = false;
                    var results = jQuery.grep( $scope.participants, function( p ){ return p.username===participant.username; } );
                    if( results.length===0 ) {
                        $scope.participants.push(participant);
                    }

                    //reset form
                    $scope.data.invitee= {'email':'','first_name':'', 'last_name':'', 'message':''};
                    $scope.data.isNew = false;
                    $scope.data.isParticipant = false;
                    $scope.data.isLawyer = false;
                    $scope.data.participant = null;
                    $scope.data.validationError = false;
                    $scope.data.showAddLawyer=false;
                    $scope.data.showAddParticipant=false;
                    $scope.data.selectedUser=null;
                    $scope.data.showAddButton = false;

                    toaster.pop('success', 'Success!', 'User was added successfully',5000);
				},
				function error() {
                    $scope.data.requestLoading = false;
					toaster.pop('error', 'Error!', 'Unable to invite this person to particpate, please try again in a few moments',5000);
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
            $scope.data.requestLoading = true;

			participantService.revoke( $scope.matter.slug, person ).then(
				function success() {
                    $scope.data.requestLoading = false;
					var index = jQuery.inArray( person, $scope.participants );
                    if( index>=0 ) {
                        // Remove user from in RAM array
                        $scope.participants.splice(index,1);
                        $scope.data.selectedUser=null;
                    }

                    if(person.username===$scope.currentUser.username){
                        $window.location = '/';
                    }
				},
				function error() {
                    $scope.data.requestLoading = false;
					toaster.pop('error', 'Error!', 'Unable to revoke the access of this person',5000);
				}
			);
		};


        $scope.update = function( person ){
        	// Set updating flag, for GUI display
            $scope.data.requestLoading = true;

            // Set backup permissions, forr rollback
            $scope.data.selectedUserPermissionsBackup = angular.copy(person.permissions);

            // Request permissions update
            participantService.update( $scope.matter.slug, person ).then(
				function success() {
                    $scope.data.requestLoading = false;
					toaster.pop('success', 'Success!', 'User was updated successfully',5000);
				},
				function error() {
                    $scope.data.requestLoading = false;
					toaster.pop('error', 'Error!', 'Unable to update the user',5000);
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



        /**
		 * Determines if inputis valid or not.
		 *
		 * @name				invalid
		 *
		 * @private
		 * @method				invalid
		 * @memberof			ParticipantInviteCtrl
		 */
		$scope.invalid = function() {
            return $scope.data.validationError ||
                !($scope.data.invitee.email&&$scope.data.invitee.first_name&&$scope.data.invitee.last_name);
		};

		$scope.$watch('data.selectedUser.permissions', function( newVal, oldVal ) {
			if(newVal && oldVal ) {
				debugger;
				$scope.permissionsChanged;
			}
		});
	}
]);

// $modalInstance, items