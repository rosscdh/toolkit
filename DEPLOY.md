Deployment actions by branch
----------------------------

[master]

pip install djangorestframework==2.3.13  ## to have access to the is_success from status

1. manage.py migrate default 0001 --fake  # intial

[gui/checklist]

1. manage.py migrate workspace 0001 --fake  # intial
2. manage.py migrate workspace 0002  # workspace matter_numer
3. manage.py migrate workspace 0003  # workspace description
4. manage.py migrate item # does not exist in live yet

[review-app]

1. pip install django-uuidfield --upgrade : were using hyphenate=True
2. pip install -r requirements/base.txt : added crocodoc modules
