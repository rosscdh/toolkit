angular.module('toolkit-gui').directive("filepicker", function($location){
	return {
		'scope': {
			'callback': '&',
			'btnclasses': '='
		},
		/*'transclude': true,*/
		'restrict': "A",
		/*'template': "<a href='' class='{{btnclasses}}' ng-click='pickFiles()' ng-transclude></a>",*/
		'link': function(scope, element, attrs) {

			element.bind("click", function(e){
				scope.pickFiles();
			});

			scope.pickFiles = function () {
				var picker_options = {
					'container': 'modal',
					'services': ['BOX','COMPUTER','DROPBOX','EVERNOTE','FTP','GITHUB','GOOGLE_DRIVE','SKYDRIVE','WEBDAV']
				};

				if(attrs.multiple === 'true'){
					picker_options['multiple'] = true;
				}

				if(attrs.apikey) {
					filepicker.setKey(attrs.apikey);
				}

				if(attrs.extensions) {
					/**
					* Waiting on feedback from filepicker.io
					* seems to error out.
					* 1. had an error in our backedn
					* 2. fp.io seems to have cached that response and now errors out all the time
					* 3. you MUST pass the extensions in as LOWERCASE not uppercase
					*/
					//picker_options.extensions = attrs.extensions.toLowerCase().split(',');
				}

				var path = attrs.path ? attrs.path : '/uploads/';

				var store_options = {
					'location': 'S3',
					'path': path
				};

				filepicker.pickAndStore(picker_options, store_options, function (fpfiles) {
					scope.$apply(function(){
						scope.callback({'files':fpfiles});
					});
				});
			};
		}
	};
});