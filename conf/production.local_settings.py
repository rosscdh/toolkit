# -*- coding: utf-8 -*-
LOCAL_SETTINGS = True
from settings import *

PROJECT_ENVIRONMENT = 'prod'

SITE_ID = 2

SECRET_KEY = 'i6=)1=4in#zyp&amp;g)^9nqodjgjru134)@2)^$ox5w7ac*uhml!uy-5'

DEBUG = False
TEST_PREPROD = False  # MUST be false in production
TEMPLATE_DEBUG = DEBUG

TEMPLATE_LOADERS = (
    ('django.template.loaders.cached.Loader', (
        'django.template.loaders.filesystem.Loader',
        'django.template.loaders.app_directories.Loader',
    )),
)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'toolkit_production',
        'USER': 'postgres',
        'PASSWORD': 'p7vgff9h197gnres0kj13btoos4',
        'HOST': 'ec2-50-18-97-221.us-west-1.compute.amazonaws.com',
        'PORT': 5432
    }
}

USE_ETAGS = True

# Additional locations of static files
STATICFILES_DIRS = (
    # These are the production files
    # not that static is in gui/dist/static *not to be confused with the django {{ STATIC_URL }}ng/ which will now point correctly
    ("ng", os.path.join(SITE_ROOT, 'gui', 'dist')),
)

MEDIA_URL = '/m/'
STATIC_URL = '/s/'

STATIC_ROOT = '/var/apps/toolkit/static/'
MEDIA_ROOT = '/var/apps/toolkit/media/'

ALLOWED_HOSTS = ['*']

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.sendgrid.net'
EMAIL_HOST_USER = 'lawpal'
EMAIL_HOST_PASSWORD = '0113633alex'
# EMAIL_PORT = 587
# EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = 'noreply@lawpal.com'
SERVER_EMAIL = 'toolkit@lawpal.com'

AWS_STORAGE_BUCKET_NAME = AWS_FILESTORE_BUCKET = 'prod-toolkit-lawpal-com'

CROCDOC_API_KEY = 'GT9FRcpXVs61rgauSjCIzb3Y'

RAVEN_CONFIG = {
    'dsn': 'https://b5a6429d03e2418cbe71cd5a4c9faca6:ddabb51af47546d1ac0e63cb453797ba@app.getsentry.com/6287',
}


CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': '127.0.0.1:11211'
    },
    'session_cache': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': '127.0.0.1:11211',
        'TIMEOUT': 3600
    },
    'fallback': {
        'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
        'LOCATION': '/tmp/glynt.production.cache',
    }
}

SPLUNKSTORM_ENDPOINT = 'logs2.splunkstorm.com'
SPLUNKSTORM_PORT = 20824

CROCDOC_API_KEY = '27FXmeRJ3StkMZGxi46UTwWH'

AUTHY_API_KEY = 'e19afad3c1c207a03ef6a1dcb2adb0c3'

#
# Abridge mailout service
#
ABRIDGE_ENABLED = True  # disabled by default
ABRIDGE_API_URL = 'https://abridge.lawpal.com/'
ABRIDGE_PROJECT = 'lawpal-digest'

ABRIDGE_ACCESS_KEY_ID = 'e4b38a5758caf486e21c'
ABRIDGE_SECRET_ACCESS_KEY = '2a2c7c6104c80855a12d53bd846e117fbf81f41c'
ABRIDGE_USERNAME = 'lawpal-production'
ABRIDGE_PASSWORD = 'production123'
