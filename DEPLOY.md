Deployment actions by branch
----------------------------

--------------------------------------------------------------------------------
** DEPLOYED 27 August 2014
--------------------------------------------------------------------------------

[integration/dropbox]

1. pip install dropbox

--------------------------------------------------------------------------------
** DEPLOYED 20 August 2014
--------------------------------------------------------------------------------

[integration/goclio]

1. pip install -e git+https://github.com/rosscdh/python-box.git#egg=python-box
2. pip install -e git+https://github.com/rosscdh/python-social-auth.git@backends/goclio#egg=python-social-auth
3. pip install -e git+https://github.com/rosscdh/django-box.git#egg=django-box
4. ./manage.py syncdb --migrate

--------------------------------------------------------------------------------
** DEPLOYED 10(?) August 2014
--------------------------------------------------------------------------------

[fix/rt-item-update-on-crocodoc-webhook]

1. pip install -e git+https://github.com/rosscdh/django-crocodoc.git#egg=django-crocodoc -U  # upgrade to latest 0.1.4 (previously sha: 9cbc679f2d109083a0f6df8bf3e58078a8ed5c7a)


--------------------------------------------------------------------------------
** DEPLOYED 01 August 2014
--------------------------------------------------------------------------------

[feature/item-discussions]

1. ./manage.py migrate discussion 0001 --fake
2. ./manage.py migrate discussion 0002  # update older matter discussion comments
3. ./manage.py migrate discussion 0003  # bring across item comments from actstream


--------------------------------------------------------------------------------
** DEPLOYED 25 July 2014
--------------------------------------------------------------------------------

[feature/tasks]

1. ./manage.py syncdb


[feature/item-attachments]

1. ./manage.py migrate attachment


[feature/completed-requests]

1. ./manage.py syncdb


--------------------------------------------------------------------------------
** DEPLOYED 2 July 2014
--------------------------------------------------------------------------------

[request-count-migration]

1. ./manage.py migrate default 0006


--------------------------------------------------------------------------------
** DEPLOYED 30 June 2014
--------------------------------------------------------------------------------

[feature/matter-discussions]

1. pip install django-threadedcomments==0.9.0
2. ./manage.py syncdb --migrate


--------------------------------------------------------------------------------
** DEPLOYED 26 June 2014
--------------------------------------------------------------------------------

[fix/matter-db-load-improvement]

1. ./manage.py migrate workspace


--------------------------------------------------------------------------------
** DEPLOYED 24 June 2014 - allow owners to assign granular permissions to matters
*NOTES* had to ensure that existing flows are not iterrupted but setting clients by default
to have manage_items permission; all new matters do not have this permission and if the user
is updated in the matter they will lose the permission.
--------------------------------------------------------------------------------

[feature/matter-permissions-global]

1. pip install django-permission
2. ./manage.py syncdb  # add the permissions tables
3. ./manage.py migrate default  # extend the max_length of auth_permission.name(50) to (128) for our long assed permission names
4. ./manage.py update_permissions  # add our set of permissions
5. ./manage.py migrate workspace  # migrate the through table and its settings


--------------------------------------------------------------------------------
** DEPLOYED 17 June 2014
--------------------------------------------------------------------------------

[two-factor-sms]

1. pip install -e git+https://github.com/rosscdh/django-authy.git#egg=django-authy -U

[feature/signing-progress-indicator]

1. pip install -e git+https://github.com/rosscdh/django-hello_sign.git#egg=django-hello_sign -U # upgrade the HelloSign object


--------------------------------------------------------------------------------
** DEPLOYED 10 June 2014
--------------------------------------------------------------------------------

[signing-unclaimed-draft]

1. pip install -e git+https://github.com/rosscdh/django-hello_sign.git#egg=django-hello_sign -U
2. pip install -e git+https://github.com/rosscdh/hellosign.git#egg=hellosign -U
3. pip install hellosign-python-sdk -U
4. pip install django-jsonify
5. ./manage.py migrate hello_sign 0001 --fake
6. ./manage.py migrate hello_sign
7. ./manage.py migrate attachment
8. ./manage.py migrate sign 0001 --fake
9. ./manage.py migrate sign


--------------------------------------------------------------------------------
** DEPLOYED 17 May 2014
--------------------------------------------------------------------------------

[authy-integration]

1. pip install -e git+https://github.com/rosscdh/django-authy.git#egg=django-authy
2. ./manage.py syncdb --migrate

--------------------------------------------------------------------------------
** DEPLOYED 15 May 2014
--------------------------------------------------------------------------------

[feature/pusher-integration]

1. pip install pusher
2. pip install django -U # upgraded to https://www.djangoproject.com/weblog/2014/may/14/security-releases-issued/

--------------------------------------------------------------------------------
** DEPLOYED 06 May 2014
--------------------------------------------------------------------------------

[stripe-payments]

1. pip install django-stripe-payments==2.0b34
2. ./manage.py syncdb --migrate


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
