// Karma configuration
// http://karma-runner.github.io/0.10/config/configuration-file.html

module.exports = function(config) {
  config.set({
    // base path, that will be used to resolve files and exclude
    basePath: '',

    // testing framework to use (jasmine/mocha/qunit/...)
    frameworks: ['jasmine'],

    // list of files / patterns to load in the browser
    files: [
	   //components
	  'bower_components/jquery/jquery.js', 
      'bower_components/angular/angular.js',
	  'bower_components/angular-!(scenario)/angular-!(.min).js',
      'bower_components/angular-bootstrap/ui-bootstrap-tpls.js',
	  'bower_components/angular-ui-utils/ui-utils.js',
	  'bower_components/angular-ui-sortable/sortable.js',
      'bower_components/ez-confirm/src/ez-confirm.js',
	  'bower_components/AngularJS-Toaster/toaster.js',	 
	  'bower_components/angular-ui-router/release/angular-ui-router.js',
	  'bower_components/ng-file-upload/angular-file-upload.js',
	  'bower_components/angular-markdown-directive/markdown.js',
	  'bower_components/angular-elastic/elastic.js',	  
	  
	  //templates
	  'bower_components/ez-confirm/src/ez-confirm-tpl.html',
	  
	  //app files
	  'js/setup.js',
	  
	  //service
	  'service/matter.js',
	  'service/matterItem.js',
	  'service/mattercategory.js',
	  'service/participants.js',
	  'service/search.js',
	  'service/smartRoutes.js',
	  'service/activity.js',
	  'service/user.js',
	  'service/comment.js',
	  
	  //controllers
	  'partial/authentication-required/authentication-required.js',
	  'partial/checklist/checklist.js',
	  'partial/home/home.js',
	  'partial/closing/closing.js',
	  'partial/navigation/navigation.js',
	  'partial/participant-invite/participant-invite.js',
	  'partial/request-review/request-review.js',
	  'partial/request-revision/request-revision.js',
	  'partial/request-signing/request-signing.js',
	  'partial/searchCtrl/searchCtrl.js',
	  'partial/view-document/view-document.js',
	  'partial/view-review/view-review.js',
	  
      //test      
	  'partial/authentication-required/authentication-required-spec.js',
	  'partial/checklist/checklist-spec.js',
	  'partial/home/home-spec.js',
	  'partial/closing/closing-spec.js',
	  'partial/navigation/navigation-spec.js',
	  'partial/participant-invite/participant-invite-spec.js',
	  'partial/request-review/request-review-spec.js',
	  'partial/request-revision/request-revision-spec.js',
	  'partial/request-signing/request-signing-spec.js',
	  'partial/searchCtrl/searchCtrl-spec.js',
	  'partial/view-document/view-document-spec.js',
	  'partial/view-review/view-review-spec.js'

    ],
    // coverage reporter generates the coverage
    reporters: ['progress', 'coverage'],

    // optionally, configure the reporter
    coverageReporter: {
      type : 'html',
      dir : 'coverage/'
    },
    // list of files / patterns to exclude
    exclude: [],
    preprocessors: {
	  'partial/**/*.js': ['coverage'],
      'bower_components/ez-confirm/src/ez-confirm-tpl.html': ['ng-html2js']
    },
    /*ngHtml2JsPreprocessor: {
      // strip this from the file path
      stripPrefix: 'app/',
	  moduleName: 'templates'
    },*/

    // web server port
    port: 8080,

    // level of logging
    // possible values: LOG_DISABLE || LOG_ERROR || LOG_WARN || LOG_INFO || LOG_DEBUG
    logLevel: config.LOG_INFO,


    // enable / disable watching file and executing tests whenever any file changes
    autoWatch: true,


    // Start these browsers, currently available:
    // - Chrome
    // - ChromeCanary
    // - Firefox
    // - Opera
    // - Safari (only Mac)
    // - PhantomJS
    // - IE (only Windows)
    browsers: ['Chrome'],

    plugins : [        
            'karma-chrome-launcher',
            'karma-firefox-launcher',
            'karma-jasmine',
			'karma-coverage',
			'karma-ng-html2js-preprocessor'
    ],
    // Continuous Integration mode
    // if true, it capture browsers, run tests and exit
    singleRun: false
  });
};
