Deployment actions by branch
----------------------------

--------------------------------------------------------------------------------
** DEPLOYED 27 March 2014 - chicago (early morn) (rosscdh)
--------------------------------------------------------------------------------

[review-app]

1. pip install -e git+https://github.com/rosscdh/django-crocodoc.git#egg=django-crocodoc --upgrade - new .generate() on service
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