# -*- coding: utf-8 -*-
"""
LawPal - toolkit app
"""
import os, sys
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

SITE_ROOT = os.path.dirname(os.path.realpath(__file__+ '/../'))

IS_TESTING = False
for test_app in ['testserver','test']:
    if test_app in sys.argv[1:2]:
        IS_TESTING = True


SITE_ID = 1

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'lgi%*e=%s@y3-jos^uydhc5gz80m9ts&9io5xh6myf+$fuy7+n'

# List of callables that know how to import templates from various sources.
TEMPLATE_DIRS = (
    os.path.join(SITE_ROOT, 'templates'),
)

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/
STATIC_ROOT = os.path.join(SITE_ROOT, 'static')
STATIC_URL = '/static/'

# Additional locations of static files
STATICFILES_DIRS = (
)

MEDIA_ROOT = os.path.join(SITE_ROOT, 'media')
MEDIA_URL = '/m/'

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'compressor.finders.CompressorFinder',
)


ALLOWED_HOSTS = []


# Application definition

DJANGO_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.sites',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
)

PROJECT_APPS = (
    'toolkit.apps.api',
    'toolkit.apps.default',
    'toolkit.apps.dash',
    'toolkit.apps.workspace',
    'toolkit.apps.eightythreeb',
)

HELPER_APPS = (
    'django_extensions',
    'localflavor',
    'django_bootstrap_breadcrumbs',
    'rulez',
    'storages',

    # api
    'rest_framework',
    'rest_framework.authtoken',
    'rest_framework_swagger',

    # forms
    'parsley',
    'crispy_forms',

    # db migrations
    'south',
)

INSTALLED_APPS = DJANGO_APPS + PROJECT_APPS + HELPER_APPS

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'django.core.context_processors.static',
    'django.core.context_processors.tz',
    'django.contrib.messages.context_processors.messages',
    'django.core.context_processors.request',
    'toolkit.context_processors.EXPOSED_GLOBALS',
    'toolkit.context_processors.LAYOUT',
    'toolkit.context_processors.WORKSPACES',
)

ROOT_URLCONF = 'toolkit.urls'

WSGI_APPLICATION = 'toolkit.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'dev.db'),
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = False  # should always be False to enable dates accepted https://docs.djangoproject.com/en/dev/ref/forms/fields/#DateField

USE_TZ = True


LOGIN_URL          = '/start/'
LOGIN_REDIRECT_URL = '/dash/'
LOGIN_ERROR_URL    = '/login-error/'

AUTHENTICATION_BACKENDS = (
    'toolkit.auth_backends.EmailBackend',
    'django.contrib.auth.backends.ModelBackend',
    'toolkit.auth_backends.SecretKeyBackend',
)

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
TEMPLATED_EMAIL_BACKEND = 'templated_email.backends.vanilla_django'

AWS_STORAGE_BUCKET_NAME = AWS_FILESTORE_BUCKET = 'dev-toolkit-lawpal-com'

AWS_ACCESS_KEY_ID = 'AKIAIRFGFTRB4LRLWC3A'
AWS_SECRET_ACCESS_KEY = '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'
AWS_QUERYSTRING_AUTH = False # to stop 304 not happening and boto appending our info to the querystring
AWS_PRELOAD_METADATA = True
# see http://developer.yahoo.com/performance/rules.html#expires
AWS_HEADERS = {
    'Cache-Control': 'max-age=300',
    'x-amz-acl': 'public-read',
}

REST_FRAMEWORK = {
    # Use hyperlinked styles by default.
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.JSONPRenderer',
    ),
    # Only used if the `serializer_class` attribute is not set on a view.
    'DEFAULT_MODEL_SERIALIZER_CLASS':
        'rest_framework.serializers.HyperlinkedModelSerializer',

    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    ),

    'DEFAULT_FILTER_BACKENDS': (
        ('rest_framework.filters.DjangoFilterBackend',)
    ),
    # Use Django's standard `django.contrib.auth` permissions,
    # or allow read-only access for unauthenticated users.
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
        #'toolkit.apps.api.permissions.ApiObjectPermission',
    ],
    'PAGINATE_BY': 10,
}


SWAGGER_SETTINGS = {
    "exclude_namespaces": [], # List URL namespaces to ignore
    "api_version": '0.1',  # Specify your API's version
    "api_path": "/",  # Specify the path to your API not a root level
    "enabled_methods": [  # Specify which methods to enable in Swagger UI
        'get',
        'post',
        'put',
        'patch',
        'delete'
    ],
    "api_key": '', # An API key
    "is_authenticated": False,  # Set to True to enforce user authentication,
    "is_superuser": False,  # Set to True to enforce admin only access
}

CRISPY_TEMPLATE_PACK = 'bootstrap3'

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
        'LOCATION': '/tmp/toolkit.dev.cache',
    }
}

# See: https://docs.djangoproject.com/en/dev/ref/settings/#date-format
DATE_FORMAT = 'F j, Y'
JS_DATE_FORMAT = 'MM d, yy'

# See: https://docs.djangoproject.com/en/dev/ref/settings/#std:setting-SHORT_DATE_FORMAT
SHORT_DATE_FORMAT = 'm/d/Y'
JS_SHORT_DATE_FORMAT = 'mm/dd/yy'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'null': {
            'level': 'DEBUG',
            'class': 'django.utils.log.NullHandler',
        },
        'console':{
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
        },
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
        }
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'propagate': True,
            'level': 'INFO',
        },
        'django.request': {
            'handlers': ['mail_admins', 'console'],
            'level': 'ERROR',
            'propagate': False,
        },
        'django.request': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'django.test': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        }
    }
}

try:
    LOCAL_SETTINGS
except NameError:
    try:
        from local_settings import *
    except ImportError:
        print("Could not load local_settings")

if IS_TESTING:
    try:
        from test_settings import *
    except ImportError:
        print("Could not load test_settings")
