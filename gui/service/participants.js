angular.module('toolkit-gui').factory('participantService', [
	'$q',
	'$resource',
	'API_BASE_URL',
	function($q, $resource, API_BASE_URL) {

        function userAPI() {
            return $resource( API_BASE_URL + 'users/:username', {}, {
				'get': { 'method': 'GET', 'headers': { 'Content-Type': 'application/json'/*, 'token': token.value*/ } }
			});
        }

		function participantAPI() {
			return $resource( API_BASE_URL + 'matters/:matterSlug/participant/:id', {}, {
				'list': { 'method': 'GET', 'headers': { 'Content-Type': 'application/json'/*, 'token': token.value*/ }, 'isArray': true },
				'get': { 'method': 'GET', 'headers': { 'Content-Type': 'application/json'/*, 'token': token.value*/ } },
				'invite': { 'method': 'POST', 'headers': { 'Content-Type': 'application/json'/*, 'token': token.value*/ } },
				'update': { 'method': 'PATCH', 'headers': { 'Content-Type': 'application/json'/*, 'token': token.value*/ } },
				'revoke': { 'method': 'DELETE', 'headers': { 'Content-Type': 'application/json'/*, 'token': token.value*/ } }
			});
		}

        var data = {
            loadedParticipants: {}
        };

		return {
            /**
			 * Returns object containing 'loaded Participants'.
			 * This data lives beyond the life of a single view.
			 *
			 * @name				data
			 *
			 * @example
		 	 * participantService.data()
			 *
			 * @public
			 * @method				data
			 * @memberof			participantService
			 *
			 * @return {Object}     { 'items': [], 'selected': {} }
		 	 */
			'data': function() {
				return data;
			},

            /**
			 * Stores the loaded participant in data.
			 *
			 * @name				setParticipant
			 *
			 * @example
		 	 * participantService.setParticipant( mySParticipant );
			 *
			 * @public
			 * @method				setParticipant
			 * @memberof			participantService
		 	 */
			'setParticipant': function( participanturl, participant ) {
				data.loadedParticipants[participanturl] = participant;
                console.log(data.loadedParticipants[participanturl]);
			},


             /**
			 * Calls the API with the given participant URL and receives a user object.
			 *
			 * @name				getByURL
			 *
			 * @example
		 	 * participantService.getByURL( mySParticipantURL );
			 *
			 * @public
			 * @method				getByURL
			 * @memberof			participantService
		 	 */
            'getByURL': function(participanturl) {
                var deferred = $q.defer();

                var api = $resource(participanturl, {}, {
                        'get': { 'method': 'GET', 'headers': { 'Content-Type': 'application/json' }}
                });

                api.get({},
                    function success( response ) {
                        deferred.resolve( response );
                    },
                    function error( err ) {
                        deferred.reject( err );
                    }
                );

                return deferred.promise;
             },

             /**
			 * Calls the API with the given participant username and receives a user object.
			 *
			 * @name				getByUsername
			 *
			 * @example
		 	 * participantService.getByUsername( mySParticipantUsername );
			 *
			 * @public
			 * @method				getByUsername
			 * @memberof			participantService
		 	 */
            'getByUsername': function(username) {
                var deferred = $q.defer();

				var api = userAPI();

				api.get({'search': username},
					function success( response ) {
						deferred.resolve( response );
					},
					function error( err ) {
						deferred.reject( err );
					}
				);

				return deferred.promise;
            },

             /**
			 * Calls the API with the given participant email address and receives a user object.
			 *
			 * @name				getByEmail
			 *
			 * @example
		 	 * participantService.getByEmail( mySParticipantMailaddress );
			 *
			 * @public
			 * @method				getByEmail
			 * @memberof			participantService
		 	 */
            'getByEmail': function(email) {
                var deferred = $q.defer();

				var api = userAPI();

				api.get({'search': email},
					function success( response ) {
						deferred.resolve( response );
					},
					function error( err ) {
						deferred.reject( err );
					}
				);

				return deferred.promise;
            },

             /**
			 * Requests the API to invite a user with the given email-address.
             * If the user doesnt exist yet, he will be created.
			 *
			 * @name				invite
			 *
			 * @example
		 	 * participantService.invite( {} );
			 *
			 * @public
			 * @method				invite
			 * @memberof			participantService
		 	 */
			'invite': function( matterSlug, details ) {
				var deferred = $q.defer();
				var api = participantAPI();

				api.invite( { 'matterSlug': matterSlug }, details,
					function success( response ) {
						deferred.resolve( response );
					},
					function error( err ) {
						deferred.reject( err );
					}
				);

				return deferred.promise;
			},

             /**
			 * Requests the API to revoke a user with the given email-address.
			 *
			 * @name				revoke
			 *
			 * @example
		 	 * participantService.revoke( MyMailAddress );
			 *
			 * @public
			 * @method				revoke
			 * @memberof			participantService
		 	 */
			'revoke': function( matterSlug, details ) {
				var deferred = $q.defer();
				var api = participantAPI();

				api.revoke( { 'matterSlug': matterSlug, 'id': details.email },
					function success() {
						deferred.resolve();
					},
					function error( err ) {
						deferred.reject( err );
					}
				);

				return deferred.promise;
			},

             /**
			 * Updates the participant object.
			 *
			 * @name				update
			 *
			 * @example
		 	 * participantService.update( {} );
			 *
			 * @public
			 * @method				update
			 * @memberof			participantService
		 	 */
			'update': function( matterSlug, person ) {
				var deferred = $q.defer();
				var api = participantAPI();

				api.update( { 'matterSlug': matterSlug, 'id': person.email }, person,
					function success( response ) {
						deferred.resolve( response );
					},
					function error( err ) {
						deferred.reject( err );
					}
				);

				return deferred.promise;
			}
		};
	}
]);