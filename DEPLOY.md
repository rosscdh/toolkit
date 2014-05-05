Deployment actions by branch
----------------------------

[authy-integration]

1. install -e git+https://github.com/rosscdh/django-authy.git#egg=django-authy
2. ./manage.py syncdb add the authy table

--------------------------------------------------------------------------------
** DEPLOYED 29 April 2014
--------------------------------------------------------------------------------

[matter-search]

1. need to install npm -g install yuglify on prod servers
2. pip install django-pipeline PyReact

--------------------------------------------------------------------------------
** DEPLOYED 29 April 2014
--------------------------------------------------------------------------------

[activity-stream-update]

1. ./manage.py migrate review 0001 --fake # setup the base
2. ./manage.py migrate review # add the crocodoc uuid field
3. ./manage.py migrate attachment # add is_deleted to revision
4. ensure the latest version of django-crocodoc is installed (pip_install in fab)
5. ensure that angular (bower) has "angular-sanitize": "~1.2.16",

--------------------------------------------------------------------------------
** DEPLOYED 18 April 2014
--------------------------------------------------------------------------------

[choices-names]

1. git co master;./manage.py migrate attachment 0003
must first run this data migration to ensure we catch all the current
item statuses

2. ./manage.py migrate attachment 0004  # removal of the status field


[celery]

2. manage.py migrate djcelery


--------------------------------------------------------------------------------
** DEPLOYED 6 April 2014 - celery tasks are preset but not enabled
--------------------------------------------------------------------------------

[celery]

2. manage.py migrate djcelery


--------------------------------------------------------------------------------
** DEPLOYED 6 April 2014 - celery tasks are preset but not enabled
--------------------------------------------------------------------------------

[celery]

2. manage.py migrate djcelery


--------------------------------------------------------------------------------
** DEPLOYED 6 April 2014 - celery tasks are preset but not enabled
--------------------------------------------------------------------------------

[celery]

2. manage.py migrate djcelery


--------------------------------------------------------------------------------
** DEPLOYED 4 April 2014 - fix a massive slowdown when larger matters were in
use; such as https://app.lawpal.com/matters/lawpal-corporate-setup/#/checklist
changed item.latest_revision from a property to an actual FKField reducing by a
larger query
--------------------------------------------------------------------------------

[large-matter-optimisation]

1. ./manage.py migrate item 0001 --fake
2. ./manage.py migrate item 0002 # apply the latest_revision FK which optimises the lookups
3. ./manage.py migrate item 0003 # convert all the existing data


--------------------------------------------------------------------------------
** DEPLOYED 4 April 2014
--------------------------------------------------------------------------------

[email-validation] - apply a degree of email validation
@TODO needs tests - this is a patch

1. ./manage.py migrate default  # will apply the validated_email = True to existing users


--------------------------------------------------------------------------------
** DEPLOYED 2 April 2014
--------------------------------------------------------------------------------

[sign-app] - Phase 1, done because the sign-app branch was very old and getting difficult to keep up to date with master
note that when the sign app is completed we need to hook up the urls and things

1. ./manage.py syncdb
1. ./manage.py migrate attachment 0001 --fake  # intial
2. ./manage.py migrate attachment  # signatories to signers
3. update the hellosign callback url on hellosign

--------------------------------------------------------------------------------
** DEPLOYED 29 March 2014
--------------------------------------------------------------------------------

1. pip install mixpanel-py - using mixpanel for analytics

--------------------------------------------------------------------------------
** DEPLOYED 29 March 2014
--------------------------------------------------------------------------------

1. update pip install -e git+https://github.com/rosscdh/django-hello_sign.git#egg=django-hello_sign - changed the url namespace


--------------------------------------------------------------------------------
** DEPLOYED 27 March 2014 - chicago (early morn) (rosscdh)
--------------------------------------------------------------------------------

[review-app]

1. pip install -e git+https://github.com/rosscdh/django-crocodoc.git#egg=django-crocodoc --upgrade #new .generate() on service
2.  ./manage.py migrate dj_crocodoc 0001 --fake # initial
3.  ./manage.py migrate dj_crocodoc 0002 # added reviewer field


--------------------------------------------------------------------------------
** DEPLOYED 21 March 2014 - base deploy (rosscdh)
--------------------------------------------------------------------------------
[master]

pip install djangorestframework==2.3.13  ## to have access to the is_success from status

1. ./manage.py syncdb
1. ./manage.py migrate default 0001 --fake  # intial
2. ./manage.py migrate default  # do the rest (User.username and User.email indexes)

[gui/checklist]

1. ./manage.py migrate workspace 0001 --fake  # intial
2. ./manage.py migrate workspace 0002  # workspace matter_numer
3. ./manage.py migrate workspace 0003  # workspace description
3. ./manage.py migrate workspace 0004  # workspace add matter key to Invite model
3. ./manage.py migrate workspace 0005  # ensure workspace.data is a {}
3. ./manage.py migrate workspace 0006  # matter_code max_length was 50 should be at least 128

__Item__
1. syncdb will add item app

[review-app]

1. pip install django-uuidfield --upgrade : were using hyphenate=True
2. pip install -r requirements/base.txt : added crocodoc modules

[review-requests]

1. syncdb will add attachment app
2. syncdb will add review app

[activity stream]

1. ./manage.py migrate actstream


1. Ensure crocdoc url webhook in production is set
2. ensure crocodoc account is paid for
3. ensure hellosign account is paid for and keys are for right account
