web: python manage.py runserver_plus --threaded
grunt: cd gui;grunt django
abridge: cd ../abridge/abridge/;workon abridge;./manage.py runserver_plus 8001 --threaded
celery_worker: celery -A toolkit worker -l info
web_pdf: cd ../Stamp;foreman start
