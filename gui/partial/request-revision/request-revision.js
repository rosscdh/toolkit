angular.module('toolkit-gui')
/**
 * @class RequestrevisionCtrl
 * @classdesc 		                      Responsible for managing and requesting the API to request a new revision
 * @param  {Object} $scope                Contains the scope of this controller
 * @param  {Function} $modalInstance      Provides access to close and cancel methods
 * @param  {Array} participants           List of participants within a matter
 * @param  {Object} currentUser           The current user
 * @param  {Object} checklistItem         A specific checklist item, upon which to execute requeest for new revision
 * @param  {Object} matter                The matter for which participants will be invited
 * @param  {Object} participantService    Contains methods to make participant related requests to the API
 * @param  {Function} toaster             Provides a handle to show/hide UI toasters
 * @param  {Function} anon                Controller function
 */
.controller('RequestrevisionCtrl',[
	'$scope',
	'$modalInstance',
	'participants',
	'currentUser',
	'matter',
	'checklistItem',
	'participantService',
	'toaster',
	function($scope, $modalInstance, participants, currentUser, matter, checklistItem, participantService, toaster){


		/**
		 * In scope variable containing a list of participants within this matter. This is passed through from the originating controller.
		 * This object is cloned, and therefore changes to this object will not be refected in thr originating object.
		 * 
		 * @memberof RequestrevisionCtrl
		 * @type {Array}
		 * @private
		 */
		$scope.participants = angular.copy(participants);
		/**
		 * In scope variable containing details about the current user. This is passed through from the originating controller.
		 * @memberof RequestrevisionCtrl
		 * @type {Object}
		 * @private
		 */
		$scope.currentUser = currentUser;
		/**
		 * In scope variable containing details about the matter. This is passed through from the originating controller.
		 * @memberof RequestrevisionCtrl
		 * @type {Object}
		 * @private
		 */
		$scope.matter = matter;

		/**
		 * In scope variable containing details about the specific checklist item, with which to make the request
		 * @memberof RequestrevisionCtrl
		 * @type {Object}
		 * @private
		 */
		$scope.checklistItem = checklistItem;

		/**
		 * Scope based data for this controller
		 * @memberof			RequestrevisionCtrl
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
		 * @memberof			RequestrevisionCtrl
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
		 * @memberof			RequestrevisionCtrl
		 */
		$scope.cancel = function () {
			$modalInstance.dismiss('cancel');
		};

		/**
		 * Initiates request to API to request a revision
		 *
		 * @name				request
		 * 
		 * @param  {Object} person	User object
		 * @private
		 * @method				request
		 * @memberof			RequestrevisionCtrl
		 */
		$scope.request = function() {
			var email = $scope.data.request.email;
			var message = $scope.data.request.message;
			var person = $scope.data.request.person&&$scope.data.request.person!==''?$scope.data.request.person:null;

			$modalInstance.close( { 'email': email, 'message': message, 'username': person } );
		};

		/**
		 * Determines if request revision for is valid or not.
		 * This is a little complex as the end user can select an existing user or enter an email address
		 *
		 * @name				invalid
		 * 
		 * @private
		 * @method				invalid
		 * @memberof			RequestrevisionCtrl
		 */
		$scope.invalid = function() {
			return !$scope.data.request.person&&!$scope.data.request.email;
		};
	}
]);