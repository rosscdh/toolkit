# -*- coding: utf-8 -*-
"""
LawPal - toolkit app
"""
import os, sys
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

SITE_ROOT = os.path.dirname(os.path.realpath(__file__+ '/../'))

IS_TESTING = False
for test_app in ['testserver','test', 'jenkins']:
    if test_app in sys.argv[1:2]:
        IS_TESTING = True


SITE_ID = 1

ADMINS = (
    ("Ross Crawford-dHeureuse", 'ross@lawpal.com'),
)

MANAGERS = ADMINS + (
    ("Alex Halliday", 'alex@lawpal.com'),
)

DEFAULT_FROM = (
 ("LawPal Support", 'support@lawpal.com'),
)

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'lgi%*e=%s@y3-jos^uydhc5gz80m9ts&9io5xh6myf+$fuy7+n'

# List of callables that know how to import templates from various sources.
TEMPLATE_DIRS = (
    os.path.join(SITE_ROOT, 'templates'),
    os.path.join(SITE_ROOT, 'gui'),
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
    # These are the dev files
    ("ng", os.path.join(SITE_ROOT, 'gui')),
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


ALLOWED_HOSTS = ['*']


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
    # Api
    'toolkit.api',

    # Core Apps
    'toolkit.core',
    'toolkit.apps.workspace',  # Matters
    'toolkit.core.client',
    'toolkit.core.item',
    'toolkit.core.attachment',

    # Module Apps
    'toolkit.apps.api',
    'toolkit.apps.default',
    'toolkit.apps.dash',
    'toolkit.apps.matter',
    'toolkit.apps.me',
    'toolkit.apps.request',
    'toolkit.apps.notification',
    # Main Workspace (matters)
    'toolkit.apps.workspace',
    # Core related apps
    'toolkit.apps.review',
    'toolkit.apps.sign',
    # Routine Apps
    'toolkit.apps.eightythreeb',
    'toolkit.apps.engageletter',

    # Lawpal Modules
    'hello_sign',
    'dj_crocodoc',
    'snowshoestamp',
)

HELPER_APPS = (
    'rulez',
    'storages',
    'localflavor',
    'ajaxuploader',
    'password_reset',
    'django_extensions',
    'django_bootstrap_breadcrumbs',
    'email_obfuscator',

    # getsentry.com
    'raven.contrib.django.raven_compat',

    # api
    'rest_framework',
    'rest_framework.authtoken',

    'sorl.thumbnail',

    # forms
    'parsley',
    'crispy_forms',
    'django_bleach',
    'summernote',

    # activity-stream
    'actstream',
    # notifications
    'stored_messages',

    # integration for abridge; django-abridge
    'abridge',

    # Api helpers
    #'corsheaders',  # not required yet

    # db migrations
    'south',
    # jenkins
    'django_jenkins',
)

INSTALLED_APPS = DJANGO_APPS + PROJECT_APPS + HELPER_APPS

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # 'corsheaders.middleware.CorsMiddleware',  # not required yet
    'toolkit.apps.me.middleware.EnsureUserHasPasswordMiddleware',
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

# for notifications as well as standard messages
#
# NOTE! this is an antiparttern DO NOT follow the stored_messages docs
# our usecase is to show normal django messages as per normal
# but specifically manually store the inbox messages thus we dont set the
# django.MESSAGE_STORAGE but rather leave it to the django default
# we manually need to mark them as read in this case
#
#MESSAGE_STORAGE = 'stored_messages.storage.PersistentStorage'

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
LOGOUT_URL = '/end/'

AUTHENTICATION_BACKENDS = (
    'toolkit.auth_backends.EmailBackend',
    'django.contrib.auth.backends.ModelBackend',
    'toolkit.auth_backends.SecretKeyBackend',
    'toolkit.apps.review.auth_backends.ReviewDocumentBackend',  # allow users to log in via review urls
)

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
TEMPLATED_EMAIL_BACKEND = 'templated_email.backends.vanilla_django'

AWS_STORAGE_BUCKET_NAME = AWS_FILESTORE_BUCKET = 'dev-toolkit-lawpal-com'

AWS_ACCESS_KEY_ID = AWS_UPLOAD_CLIENT_KEY = 'AKIAIRFGFTRB4LRLWC3A'
AWS_SECRET_ACCESS_KEY = AWS_UPLOAD_CLIENT_SECRET_KEY = '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'
AWS_QUERYSTRING_AUTH = False # to stop 304 not happening and boto appending our info to the querystring
AWS_PRELOAD_METADATA = True
# see http://developer.yahoo.com/performance/rules.html#expires
AWS_HEADERS = {
    'Cache-Control': 'max-age=300',
    'x-amz-acl': 'public-read',
}

CELERY_ACCEPT_CONTENT = ['json', 'pickle', ]

FILEPICKER_API_KEY = 'A4Ly2eCpkR72XZVBKwJ06z'

HELLOSIGN_AUTHENTICATION = ("founders@lawpal.com", "test2007")
HELLOSIGN_API_KEY = '0ea9011ce33b5de3b58af3b3f6d449f8f3f72e2ac06c14c6319439af39fe32f6'
HELLOSIGN_CLIENT_ID = '9bc892af173754698e3fa30dedee3826'
HELLOSIGN_CLIENT_SECRET = '8d770244b9971abfe789f5224552239d'

CORS_ORIGIN_WHITELIST = (
    'localhost:9000'
)

REST_FRAMEWORK = {
    # Use hyperlinked styles by default.
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.JSONPRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ),
    'DEFAULT_MODEL_SERIALIZER_CLASS': (
        'rest_framework.serializers.HyperlinkedModelSerializer',
    ),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        #'rest_framework.authentication.TokenAuthentication',
        #'rest_framework_jwt.authentication.JSONWebTokenAuthentication',
        #'rest_framework.authentication.BasicAuthentication', # Here Temporarily for dev
        'rest_framework.authentication.SessionAuthentication',
    ),
    'DEFAULT_FILTER_BACKENDS': (
        'rest_framework.filters.SearchFilter',
    ),
    # Use Django's standard `django.contrib.auth` permissions,
    # or allow read-only access for unauthenticated users.
    'DEFAULT_PERMISSION_CLASSES': [
        #'rest_framework.permissions.AllowAny',  # only use this in dev
        'toolkit.apps.api.permissions.ApiObjectPermission',
    ],
    'PAGINATE_BY': 10,
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

SPLUNKSTORM_ENDPOINT = 'tcp.pjg2-3xz4.data.splunkstorm.com'
SPLUNKSTORM_PORT = 20824

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
        'medium': {
            'format': '%(levelname)s %(asctime)s %(module)s %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'handlers': {
        'null': {
            'level': 'DEBUG',
            'class': 'django.utils.log.NullHandler',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'medium'
        },
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
            'formatter': 'medium'
        },
        'logfile': {
            'class': 'logging.handlers.WatchedFileHandler',
            'filename': '/tmp/toolkit-{env}.log'.format(env='dev')
        },
        'splunkstorm':{
            'level': 'INFO',
            'class': 'toolkit.loggers.SplunkStormLogger',
            'formatter': 'verbose'
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'propagate': True,
            'level': 'INFO',
        },
        'django.request': {
            'handlers': ['mail_admins', 'console', 'logfile'],
            'level': 'ERROR',
            'propagate': False,
        },
        'django.request': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        }
    }
}

USPS_USERID = '756LAWPA4755'
USPS_PASSWORD = '345LV41YU671'

BLEACH_ALLOWED_ATTRIBUTES = {'blockquote': ['style',], 'div': ['style',], 'span': ['style',]}
BLEACH_ALLOWED_STYLES = ['border', 'font-style', 'font-weight', 'margin', 'padding', 'text-align', 'text-decoration']
BLEACH_ALLOWED_TAGS = ['blockquote', 'br', 'div', 'li', 'ol', 'span', 'ul']
BLEACH_STRIP_COMMENTS = True
BLEACH_STRIP_TAGS = True


INTERCOM_APP_ID = 'wkxzfou'
INTERCOM_APP_SECRET = 'MZCesCDxkDrYdfX8HocAB2F6V5aZzCm-DuF7lyR5'

#
# ACTIVITY STREAM
#
ACTSTREAM_SETTINGS = {
    'MODELS': ('auth.User', 'workspace.Workspace', 'item.Item', 'attachment.Revision'),
    'MANAGER': 'toolkit.core.managers.ToolkitActionManager',
    'FETCH_RELATIONS': True,
    'USE_PREFETCH': True,
    'USE_JSONFIELD': True,
    'USE_FOLLOWING': False,  # VERY importand; will break our system if this changes to True
}

#
# Any change to the LAWPAL_ACTIVITY elements below needs to affect the
# test_notices.py 
#
LAWPAL_ACTIVITY = {
    "abridge": {
        "whitelist": [
                      # 'item-reopened', 'item-closed',
                      # 'item-commented', 'item-comment-created', 'item-comment-deleted',
                      # 'item-invited-reviewer',
                      # 'item-provide-a-document',
                      # 'revision-created', 'revision-comment-created', 'item-added-revision-comment', 
                      # 'revision-added-revision-comment',
                      # 'workspace-added-participant', 'workspace-removed-participant'

                      # activate nearly everything for testing;
                      'item-reopened', 'item-closed',
                      'item-commented', 'item-comment-created', 'item-comment-deleted',
                      'item-invited-reviewer',
                      'item-provide-a-document',
                      'item-invited-signer',
                      'item-completed-review',
                      'item-completed-all-reviews',

                      'revision-created', 'revision-comment-created', 'item-added-revision-comment',
                      'revision-added-revision-comment',
                      'revision-added-review-session-comment',

                      'workspace-deleted',
                      'workspace-added-participant', 'workspace-removed-participant',
                      'workspace-stopped-participating',
                      ]
    },
    "notifications": {
        "whitelist": [
                      'item-reopened', 'item-closed',
                      'item-commented', 'item-comment-created', 'item-comment-deleted',
                      'item-invited-reviewer',
                      'item-provide-a-document',
                      'item-invited-signer',
                      'item-completed-review',
                      'item-completed-all-reviews',

                      'revision-created', 'revision-comment-created', 'item-added-revision-comment', 
                      'revision-added-revision-comment',
                      'revision-added-review-session-comment',

                      'workspace-deleted',
                      'workspace-added-participant', 'workspace-removed-participant',
                      'workspace-stopped-participating',
                      ]
    },
    "activity": {
        "whitelist": ['item-created', 'item-edited', 'item-commented', 'item-changed-the-status', 'item-renamed',
                      'item-provide-a-document', 'item-invited-reviewer', 'item-canceled-their-request-for-a-document',
                      'item-closed', 'item-reopened', 'item-added-revision-comment', 'item-deleted-revision-comment',
                      'item-completed-review', 'item-viewed-revision',
                      'item-completed-all-reviews',
                      'item-invited-signer',
                      'itemrequestrevisionview-provide-a-document',

                      'revision-created', 'revision-deleted',
                      'revision-added-review-session-comment',
                      'revision-added-revision-comment',

                      'workspace-created', 'workspace-deleted',
                      'workspace-added-participant', 'workspace-removed-participant', 
                      'workspace-stopped-participating',
                      ]
    },
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
