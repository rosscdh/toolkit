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

            'getByUsername': function(username) {
                var deferred = $q.defer();

				var api = userAPI();

				api.get({'username': username},
					function success( response ) {
						deferred.resolve( response );
					},
					function error( err ) {
						deferred.reject( err );
					}
				);

				return deferred.promise;
            },

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

			'revoke': function( matterSlug, details ) {
				var deferred = $q.defer();
				var api = participantAPI();

				api.revoke( { 'matterSlug': matterSlug, 'id': details.email },
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