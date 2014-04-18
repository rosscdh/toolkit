LawPal - Toolkit
================

Toolkit is a simplified interface for adding tools and users to a generic
workspace.


Getting started
---------------

1. mkvirtualenv toolkit (assume you have virtualenv and virtualenvwrapper installed)
2. pip install -r requirements/dev.txt
3. fab rebuild_local (will download and install "stamp" - ruby rest api)
4. honcho start (starts runserver_plus in threaded mode as well as the stamp service)


Pandoc
------

__Installing__

1. Mac: https://code.google.com/p/pandoc/downloads/detail?name=pandoc-1.12.3.pkg.zip&can=2&q= install the osx package
2. Ubuntu: apt-get install pandoc should do it

__PDF Latext__

In order to use the pandoc conversion of html to pdf you need to install latex

1. Mac: http://tug.org/mactex/
2. Ubuntu: http://java.dzone.com/articles/installing-latex-ubuntu


Testing
-------

### CasperJS && PhantomJS ###

__currently we dont use phantom but once angularjs arrives this will change__

__OSX__

Should be >= casperjs: 1.1.0-DEV
Should be >= phantomjs: 1.9.0

1. ```brew update```
2. ```brew install phantomjs```
2. ```brew install casperjs --devel```


__UBUNTU__

1. ```sudo apt-get install libxml2-dev libxslt1-dev```


GUI Development Mode
--------------------

To run the service in gui mode

1. honcho start : will get everythign running (remember to be in the toolkit virtualenv) and have installed the requirements

or

1. ./manage.py runserver_plus --threaded
2. cd gui;grunt django : will start the grunt in dev mode


GUI Production Mode
-------------------

Enabling these settings will allow you to build commit and test the production
version of the gui application.


__toolkit.local_settings.py__

```
DEBUG = False
TEST_PREPROD = True

if TEST_PREPROD is True:
    STATICFILES_DIRS = (
        # These are the production files
        # not that static is in gui/dist/static *not to be confused with the django {{ STATIC_URL }}ng/ which will now point correctly
        ("ng", os.path.join(SITE_ROOT, 'gui', 'dist')),
```

1. fab build_gui



Celery Control
--------------

Will start with a worker name of __"worker.1"__ which can be overridden

```
fab :environment celery_start

fab :environment celery_stop

fab :environment celery_restart
```

__with customer worker name__

```
fab :environment celery_start:name='custom_name.1'

fab :environment celery_stop:name='custom_name.1'

fab :environment celery_restart:name='custom_name.1'
```

# Unit Tests

## Runnig the tests

# If karma not installed:

```bash
npm install
npm install -g karma-cli
```

# to run Karma:

```bash
karma start karma.conf.js
```