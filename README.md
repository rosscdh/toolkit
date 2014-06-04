LawPal - Toolkit
================

Toolkit is a simplified interface for adding tools and users to a generic
workspace.


Requirements
------------

1. mkvirtualenv toolkit (assume you have virtualenv and virtualenvwrapper installed)
2. pip install -r requirements/dev.txt *
3. copy dev.local_settings.py to /toolkit/local_setting.py
4. fab rebuild_local (will download and install "stamp" - ruby rest api)
5. honcho start (starts runserver_plus in threaded mode as well as the stamp service)

*If you are running XCode 5.1 and run into errors such as
  "Compile failed with error code 1 in /private/tmp/pip_build_root/"

Update to the newest version, or run:

ARCHFLAGS=-Wno-error=unused-command-line-argument-hard-error-in-future pip install NAME

http://stackoverflow.com/questions/22716854/os-x-pillow-installation-error/22727537#22727537


```
easy_isntall pip
pip install virtualenvwrapper
...
$ export WORKON_HOME=~/.virtualenvs
$ mkdir -p $WORKON_HOME
$ source /usr/local/bin/virtualenvwrapper.sh
$ mkvirtualenv toolkit
```

this line goes in your .bashrc .zshrc or whatever your flavour is:

```
source /usr/local/bin/virtualenvwrapper.sh
```

it gives you access to mkvirtualenv rmvirtualenv etc


Getting started
---------------

1. mkvirtualenv toolkit (assume you have virtualenv and virtualenvwrapper installed)
2. pip install -r requirements/dev.txt
3. install yuglify ('npm install -g yuglify')
4. fab rebuild_local (will download and install "stamp" - ruby rest api)
5. honcho start (starts runserver_plus in threaded mode as well as the stamp service)
6. or just ./manage.py runserver_plus --threaded


Testing
-------

### CasperJS && PhantomJS ###

__currently we dont use phantom but will do soon__

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


Development Process
-------------------

__"The most important thing in communication is hearing what isn't said."__ - *Peter Drucker*

With that in mind, please adhere to the following subtle-communication requirements.


### Trello ###

Ensure that you put guistimates in all of your tickets.. (0, 0.5, 1, 2, 3, 5, 8, 13, ...) __fibonacci sequence__

**Required Name Format:**

```
(:guesstimate) [:branch_name] Short Description
```

Install this chrome extension as it makes the guestimates look better: 

[Scrum for Trello plugin](https://chrome.google.com/webstore/detail/scrum-for-trello/jdbcdblgjdpmfninkoogcfpnkjmndgje?hl=en)



### Github ###

Ensure that you create Pull Requests for every branch that you work on. At the beginning not the end (this allows everyone a birds eye view of whats going on)

**Required Name Format:**

When working on it.

```
[WIP] Short Name
```

When ready for review.

```
[REVIEW] Short Name
```
