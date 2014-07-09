// Karma configuration
// http://karma-runner.github.io/0.10/config/configuration-file.html

module.exports = function(config) {
  config.set({
    // base path, that will be used to resolve files and exclude
    'basePath': '',

    // testing framework to use (jasmine/mocha/qunit/...)
    'frameworks': ['jasmine'],

    // list of files / patterns to load in the browser
    'files': [
      //components
      'bower_components/jquery/jquery.js', 
      'bower_components/angular/angular.js',
      'bower_components/angular-cookies/angular-cookies.js',
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
      'bower_components/html5-desktop-notifications/desktop-notify.js',

      //templates
      'bower_components/ez-confirm/src/ez-confirm-tpl.html',

      //main app file
      'js/setup.js',

      //services
      'service/!(*spec).js',

      //controllers
      'partial/**/!(*spec).js',

      //test ->controllers
      'partial/**/*-spec.js'
    ],
    // coverage reporter generates the coverage
    'reporters': ['progress', 'coverage'],

    // optionally, configure the reporter
    'coverageReporter': {
      'type' : 'html',
      'dir' : 'coverage/'
    },
    // list of files / patterns to exclude
    'exclude': [],
    'preprocessors': {
	  'partial/**/!(*spec).js': ['coverage'],
      'bower_components/ez-confirm/src/ez-confirm-tpl.html': ['ng-html2js']
    },
    /*ngHtml2JsPreprocessor: {
      // strip this from the file path
      stripPrefix: 'app/',
	  moduleName: 'templates'
    },*/

    // web server port
    'port': 8080,

    // level of logging
    // possible values: LOG_DISABLE || LOG_ERROR || LOG_WARN || LOG_INFO || LOG_DEBUG
    'logLevel': config.LOG_INFO,


    // enable / disable watching file and executing tests whenever any file changes
    'autoWatch': true,


    // Start these browsers, currently available:
    // - Chrome
    // - ChromeCanary
    // - Firefox
    // - Opera
    // - Safari (only Mac)
    // - PhantomJS
    // - IE (only Windows)
    'browsers': ['Chrome'],

    'plugins' : [        
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
