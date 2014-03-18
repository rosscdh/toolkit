'use strict';
var path = require('path');

var folderMount = function folderMount(connect, point) {
  return connect.static(path.resolve(point));
};

module.exports = function (grunt) {

  // load all grunt tasks
  require('load-grunt-tasks')(grunt);

  // Project configuration.
  grunt.initConfig({
    connect: {
      main: {
        options: {
          port: 9001,
          middleware: function(connect, options) {
            return [folderMount(connect, options.base)]
          }
        }
      }
    },
    /**
    * Constants for the Gruntfile so we can easily change the path for our environments.
    */
    // where to find our data provider
    API_SERVER: '/api/v1/',
    // root static path to allow us to load normal django files
    DJANGO_STATIC_BASE_PATH: '/static/',
    // path to the django integrated namespace for static (/static/ng/)
    APP_STATIC_PATH: '/static/ng/',
    // path to build the dist files
    PRODUCTION_PATH: 'dist/',

    /**
    * Allows us to pass in variables to files that have place holders so we can similar files with different data.
    * This plugin works with the 'env' plugin above.
    * @example <!-- @echo appVersion --> or <!-- @echo filePath -->
    */
    preprocess : {
        // Task to create the index.html file that will be used during development.
        // Passes the app version and creates the /index.html
        django : {
            src : 'config.html',
            dest : 'index.html',
            options : {
                context : {
                    staticBase : '<%= DJANGO_STATIC_BASE_PATH %>',
                    staticPath : '<%= APP_STATIC_PATH %>',
                    apiBaseUrl : '/api/v1/'
                }
            }
        },
        djangoProd : {
            src : 'config.html',
            dest : 'index.html',
            options : {
                context : {
                    staticBase : '<%= DJANGO_STATIC_BASE_PATH %>',
                    staticPath : '',
                    apiBaseUrl : '/api/v1/'
                }
            }
        },
        gruntserver : {
            src : 'config.html',
            dest : 'index.html',
            options : {
                context : {
                    staticBase : '',
                    staticPath : '/static/',
                    apiBaseUrl : '/api/v1/'
                }
            }
        }
    },
    watch: {
      main: {
        options: {
            livereload: true,
            spawn: false
        },
        files: ['js/**/*','css/**/*','img/**/*','partial/**/*','service/**/*','filter/**/*','directive/**/*','index.html'],
        tasks: [] //all the tasks are run dynamically during the watch event handler
      }
    },
    jshint: {
      main: {
        options: {
            jshintrc: '.jshintrc'
        },
        src: ['js/**/*.js','partial/**/*.js','service/**/*.js','filter/**/*.js','directive/**/*.js']
      }
    },
    clean: {
      before:{
        src:['<%= PRODUCTION_PATH %>','temp']
      },
      after: {
        src:['temp']
      }
    },
    less: {
      production: {
        options: {
        },
        files: {
          "temp/app.css": "css/app.less"
        }
      }
    },
    ngtemplates: {
      main: {
        options: {
            module:'toolkit-gui',
            htmlmin: {
              collapseBooleanAttributes: true,
              collapseWhitespace: true,
              removeAttributeQuotes: true,
              removeComments: true,
              removeEmptyAttributes: true,
              removeRedundantAttributes: true,
              removeScriptTypeAttributes: true,
              removeStyleLinkTypeAttributes: true
            }
        },
        src: [ 'partial/**/*.html','directive/**/*.html' ],
        dest: 'temp/templates.js'
      }
    },
    replace: {
      template_paths: {
        src: ['temp/templates.js'],
        overwrite: true,                 // overwrite matched source files
        replacements: [{
          from: 'partial/',
          to: '<%= PRODUCTION_PATH %>' + 'partial/'
        }]
      }
    },
    copy: {
      main: {
        files: [
          {src: ['index.html'], dest: '<%= PRODUCTION_PATH %>'},
          {src: ['img/**'], dest: '<%= PRODUCTION_PATH %>'},
          {src: ['fonts/**'], dest: '<%= PRODUCTION_PATH %>'},
          {src: ['partial/**'], dest: '<%= PRODUCTION_PATH %>'},
          {src: ['bower_components/jquery/**'], dest: '<%= PRODUCTION_PATH %>'},
          {src: ['bower_components/jquery-ui/**'], dest: '<%= PRODUCTION_PATH %>'},
          {src: ['bower_components/bootstrap/**'], dest: '<%= PRODUCTION_PATH %>'},
          {src: ['bower_components/angular/**'], dest: '<%= PRODUCTION_PATH %>'}
          // {src: ['bower_components/select2/*.png','bower_components/select2/*.gif'], dest:'dist/css/',flatten:true,expand:true},
          // {src: ['bower_components/angular-mocks/angular-mocks.js'], dest: 'dist/'}
        ]
      }
    },
    dom_munger:{
      readscripts: {
        options: {
          read:{selector:'script[data-build!="exclude"]',attribute:'src',writeto:'appjs'}
        },
        src:'index.html'
      },
      readcss: {
        options: {
          read:{selector:'link[rel="stylesheet"]',attribute:'href',writeto:'appcss'}
        },
        src:'index.html'
      },
      removescripts: {
        options:{
          remove:'script[data-remove!="exclude"]',
          append:{selector:'head',html:'<script src="' + '<%= APP_STATIC_PATH %>' + 'app.full.min.js"></script>'}
        },
        src:'<%= PRODUCTION_PATH %>' + 'index.html'
      },
      //add verbatim and endverbatim to prohibit conflicts with the django template tags
      addscript: {
        options:{
              append:{selector:'#landmine',html:'<script src="' + '<%= DJANGO_PRODUCTION_ASSET_SERVER %><%= APP_STATIC_PATH %>' + 'app.full.min.js"></script>'}
            },/* <%= DJANGO_PRODUCTION_ASSET_SERVER => */
            src:'<%= PRODUCTION_PATH %>' + 'index.html'
      },
      addverbatimprod:{
        options:{
          prepend:{selector:'body',html:'{% verbatim %}'},
          append:{selector:'body',html:'{% endverbatim %}'}
        },
        src:'<%= PRODUCTION_PATH %>' + 'index.html'
      },
      addverbatim:{
        options:{
          prepend:{selector:'body',html:'{% verbatim %}'},
          append:{selector:'body',html:'{% endverbatim %}'}
        },
        src:'index.html'
      },
      removecss: {
        options:{
          remove:'link',
          append:{selector:'head',html:'<link rel="stylesheet" href="' + '<%= DJANGO_PRODUCTION_ASSET_SERVER %><%= APP_STATIC_PATH %>' + 'css/app.full.min.css">'}
        },
        src:'<%= PRODUCTION_PATH %>' + 'index.html'
      },
      addcss: {
        options:{
          append:{selector:'head',html:'<link rel="stylesheet" href="' + '<%= DJANGO_PRODUCTION_ASSET_SERVER %><%= APP_STATIC_PATH %>' + 'css/app.full.min.css">'}
        },
        src:'<%= PRODUCTION_PATH %>' + 'index.html'
      }
    },
    cssmin: {
      main: {
        src:['temp/app.css','<%= dom_munger.data.appcss %>'],
        dest:'<%= PRODUCTION_PATH %>' + 'css/app.full.min.css'
      }
    },
    concat: {
      main: {
        src: ['<%= dom_munger.data.appjs %>','<%= ngtemplates.main.dest %>'],
        dest: 'temp/app.full.js'
      }
    },
    ngmin: {
      main: {
        src:'temp/app.full.js',
        dest: 'temp/app.full.ngmin.js'
      }
    },
    uglify: {
      main: {
        src: 'temp/app.full.ngmin.js',
        dest:'<%= PRODUCTION_PATH %>' + 'app.full.min.js'
      }
    },
    htmlmin: {
      main: {
        options: {
          collapseBooleanAttributes: true,
          collapseWhitespace: true,
          removeAttributeQuotes: true,
          removeComments: true,
          removeEmptyAttributes: true,
          removeRedundantAttributes: true,
          removeScriptTypeAttributes: true,
          removeStyleLinkTypeAttributes: true
        },
        files: {
          'dist/index.html': '<%= PRODUCTION_PATH %>' + 'index.html'
        }
      }
    },
    imagemin: {
      main:{
        files: [{
          expand: true, cwd:'<%= PRODUCTION_PATH %>' + 'static/',
          src:['**/{*.png,*.jpg}'],
          dest: '<%= PRODUCTION_PATH %>'
        }]
      }
    },
    jasmine: {
      unit: {
        src: ['<%= dom_munger.data.appjs %>','bower_components/angular-mocks/angular-mocks.js'],
        options: {
          keepRunner: true,
          specs: ['js/**/*-spec.js','partial/**/*-spec.js','service/**/*-spec.js','filter/**/*-spec.js','directive/**/*-spec.js']
        }
      }
    },
     jsdoc : {
        dist : {
            src: ['partial/**/*.js', '!partial/**/*-spec.js', 'filter/**/*.js', '!filter/**/*-spec.js', 'service/**/*.js', '!service/**/*-spec.js', 'README.md'], 
            options: {
                destination: 'doc',
                template: "node_modules/ink-docstrap/template",
                configure: "node_modules/ink-docstrap/template/jsdoc.conf.json"
            }
        }
    }
  });

  grunt.registerTask('django', ['preprocess:django','dom_munger:readscripts','dom_munger:addverbatim', 'jshint', 'watch']);
  grunt.registerTask('server', ['preprocess:gruntserver','dom_munger:readscripts','jshint','connect', 'watch']);
  grunt.registerTask('makedoc', ['jsdoc']);
  grunt.registerTask('validate', ['jshint']);
  grunt.registerTask('test',['dom_munger:readscripts','jasmine']);


  grunt.registerTask('build', 'Deploys the app in the dist folder. Target django as option.', function(n) {
    var target = grunt.option('target');

    console.log('>> target', target);


    //djangoProd
    grunt.task.run('preprocess:djangoProd','jshint','clean:before','less','dom_munger:readcss','dom_munger:readscripts','ngtemplates','replace:template_paths','cssmin','concat','ngmin','uglify','copy','dom_munger:removecss','dom_munger:addcss','dom_munger:removescripts','dom_munger:addscript');

    grunt.task.run('htmlmin'/*,'imagemin'*//*,'clean:after'*/);
  });

  grunt.event.on('watch', function(action, filepath) {
    //https://github.com/gruntjs/grunt-contrib-watch/issues/156

    if (filepath.lastIndexOf('.js') !== -1 && filepath.lastIndexOf('.js') === filepath.length - 3) {

      //lint the changed js file
      grunt.config('jshint.main.src', filepath);
      grunt.task.run('jshint');

      //find the appropriate unit test for the changed file
      var spec = filepath;
      if (filepath.lastIndexOf('-spec.js') === -1 || filepath.lastIndexOf('-spec.js') !== filepath.length - 8) {
        var spec = filepath.substring(0,filepath.length - 3) + '-spec.js';
      }

      //if the spec exists then lets run it
      if (grunt.file.exists(spec)) {
        //grunt.config('jasmine.unit.options.specs',spec);
        //grunt.task.run('jasmine:unit');
      }
    }

    //if index.html changed, we need to reread the <script> tags so our next run of jasmine
    //will have the correct environment
    if (filepath === 'index.html') {
      grunt.task.run('dom_munger:readscripts');
    }

  });

};
