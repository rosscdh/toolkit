angular.module('toolkit-gui')
/**
 * @class RequestreviewCtrl
 * @classdesc                              Responsible for managing and requesting the API to request a new revision
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
    .controller('RequestsigningCtrl', [
        '$scope',
        '$modalInstance',
        'participants',
        'currentUser',
        'matter',
        'checklistItem',
        'revision',
        'knownSigners',
        'participantService',
        'matterItemService',
        'baseService',
        'toaster',
        '$log',
        function ($scope, $modalInstance, participants, currentUser, matter, checklistItem, revision, knownSigners, participantService, matterItemService, baseService, toaster, $log) {
            'use strict';

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
            $scope.checklistItem = checklistItem;

            /**
             * In scope variable containing details about the specific checklist item, with which to make the request
             * @memberof RequestreviewCtrl
             * @type {Object}
             * @private
             */
            $scope.revision = revision;


            /**
             * A list of all already known sliders in this session
             * @memberof RequestreviewCtrl
             * @type {Object}
             * @private
             */
            $scope.knownSigners = knownSigners;

            /**
             * Scope based data for this controller
             * @memberof            RequestreviewCtrl
             * @private
             * @type {Object}
             */
            $scope.data = {
                'showAddSigner': false,
                'selectedUsers': {},
                'invitee': {},
                'participant': null,
                'requestLoading': false,
                'request': {
                    'signers': [],
                    'message': null
                }
            };

            /**
             * Close dialog on afirmative user initiated event (.e.g. click's OK button).
             * Returns updated participants array.
             *
             * @name                ok
             *
             * @private
             * @method                ok
             * @memberof            RequestreviewCtrl
             */
            $scope.ok = function () {
                $modalInstance.close($scope.participants);
            };

            /**
             * Close dialog on afirmative user initiated event (.e.g. click's OK button).
             * Returns nothing
             *
             * @name                cancel
             *
             * @private
             * @method                cancel
             * @memberof            RequestreviewCtrl
             */
            $scope.cancel = function () {
                $modalInstance.dismiss('cancel');
            };

            /**
             * Checks if a user exists with the entered mailaddress and activates the input
             * fields for first and last name if not.
             *
             * @name                checkIfUserExists
             *
             * @private
             * @method                checkIfUserExists
             * @memberof            RequestsigningCtrl
             */
            $scope.checkIfUserExists = function () {
                if ($scope.data.invitee.email != null && $scope.data.invitee.email.length > 0) {
                    $scope.data.validationError = false;
                    $scope.data.requestLoading = true;

                    participantService.getByEmail($scope.data.invitee.email).then(
                        function success(response) {
                            $scope.data.requestLoading = false;
                            if (response.count === 1) {
                                $scope.data.isNew = false;
                                $scope.data.participant = response.results[0];
                            } else {
                                $scope.data.isNew = true;
                                $scope.data.participant = null;
                            }
                        },
                        function error() {
                            $scope.data.requestLoading = true;
                            toaster.pop('error', 'Error!', 'Unable to load participant', 5000);
                        }
                    );
                } else {
                    $scope.data.validationError = true;
                    $scope.data.isNew = false;
                    $scope.data.participant = null;
                }
            };

            $scope.toggleUser = function (user) {
                if (!(user.username in $scope.data.selectedUsers)) {
                    $scope.data.selectedUsers[user.username] = user;
                } else {
                    delete $scope.data.selectedUsers[user.username];
                }
            };

            $scope.init = function () {
                $scope.data.requestLoading = true;
                $scope.iterator = 1;
                var len = -1;

                //preload/preselect old requested signers
                if ($scope.revision.signers && $scope.revision.signers.length > 0) {
                    len = $scope.revision.signers.length;
                    jQuery.each($scope.revision.signers, function (index, signer) {
                        var users = jQuery.grep($scope.participants, function (p) {
                            return p.username === signer.username;
                        });

                        if (users.length > 0) {
                            $scope.toggleUser(users[0]);
                            $scope.iterator++;
                        } else {
                            //user not in list of participants
                            //must be an external member
                            baseService.loadObjectByUrl(signer.url).then(
                                function success(obj) {
                                    $scope.participants.push(obj);
                                    $scope.toggleUser(obj);
                                    $scope.iterator++;
                                },
                                function error(/*err*/) {
                                    toaster.pop('error', 'Error!', 'Unable to load external member', 5000);
                                }
                            );
                        }
                    });
                } else {
                    len = 0;
                    $scope.iterator = 2;
                }


                //wait till all former signers are initiated to avoid duplicates
                $scope.$watch('iterator', function () {
                    $log.debug("i: " + $scope.iterator + ", length: " + len);
                    if (($scope.iterator > 1 && $scope.iterator >= len + 1) || len === 0) {
                        $log.debug("starting");
                        //add known external signers from this session
                        if ($scope.knownSigners) {
                            jQuery.each($scope.knownSigners, function (index, signer) {
                                var users = jQuery.grep($scope.participants, function (p) {
                                    return p.username === signer.username;
                                });

                                if (users.length === 0) {
                                    //add external user to the list of participants
                                    baseService.loadObjectByUrl(signer.url).then(
                                        function success(obj) {
                                            $scope.participants.push(obj);
                                        },
                                        function error(/*err*/) {
                                            toaster.pop('error', 'Error!', 'Unable to load external member', 5000);
                                        }
                                    );
                                }
                            });
                        }
                        $scope.data.requestLoading = false;
                    }
                });
            };

            $scope.init();

            /**
             * Adds a new person to be selectable as signer
             *
             * @name                invite
             *
             * @private
             * @method                invite
             * @memberof            RequestsigningCtrl
             */
            $scope.invite = function () {
                var invitee;
                if ($scope.data.participant) {
                    invitee = $scope.data.participant;
                } else {
                    invitee = $scope.data.invitee;
                }

                var results = jQuery.grep($scope.participants, function (p) {
                    return p.email === invitee.email;
                });
                if (results.length === 0) {
                    $scope.participants.push(invitee);
                    $scope.toggleUser(invitee);
                }

                //reset form
                $scope.data.invitee = {'email': '', 'first_name': '', 'last_name': '', 'message': ''};
                $scope.data.isNew = false;
                $scope.data.participant = null;
                $scope.data.validationError = false;
                $scope.data.showAddSigner = false;
            };


            /**
             * Initiates request to sign the document for the selected users.
             *
             * @name                request
             *
             * @param  {Object} person    User object
             * @private
             * @method                request
             * @memberof            RequestsigningCtrl
             */
            $scope.request = function () {
                $scope.data.request.signers = [];
                $scope.data.requestLoading = true;

                for (var key in $scope.data.selectedUsers) {
                    var usr = $scope.data.selectedUsers[key];
                    $scope.data.request.signers.push({'email': usr.email, 'first_name': usr.first_name, 'last_name': usr.last_name});
                }
                $log.debug($scope.data.request);
                matterItemService.requestSigner($scope.matter.slug, $scope.checklistItem.slug, $scope.data.request).then(
                    function success(response) {
                        $log.debug(response);
                        $modalInstance.close(response);
                        $scope.data.requestLoading = false;
                    },
                    function error(/*err*/) {
                        if (!toaster.toast || !toaster.toast.body || toaster.toast.body !== "Unable to request signers.") {
                            toaster.pop('error', "Error!", "Unable to request signers.");
                        }
                        $scope.data.requestLoading = false;
                    }
                );

            };

            /**
             * Determines if request signing for is valid or not.
             *
             * @name                invalid
             *
             * @private
             * @method                invalid
             * @memberof            RequestsigningCtrl
             */
            $scope.invalid = function () {
                return $scope.data.showAddSigner === true || jQuery.isEmptyObject($scope.data.selectedUsers) || $scope.data.requestLoading === true;
            };

            /**
             * Determines if the new user  is valid or not.
             *
             * @name                invalid
             *
             * @private
             * @method                invalid
             * @memberof            RequestsigningCtrl
             */
            $scope.invalidNewSigner = function () {
                return $scope.data.participant === null && !($scope.data.invitee.email && $scope.data.invitee.first_name && $scope.data.invitee.last_name);
            };
        }
    ]);