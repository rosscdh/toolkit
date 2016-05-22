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
    ("Ross Crawford-dHeureuse", 'sendrossemail@gmail.com'),
)

MANAGERS = ADMINS# + (
    #("Alex Halliday", 'alex@lawpal.com'),
#)

DEFAULT_FROM = (
 ("LawPal Support", 'sendrossemail@gmail.com'),
)

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'lgi%*e=%s@y3-jos^uydhc5gz80m9ts&9io5xh6myf+$fuy7+n'

URL_ENCODE_SECRET_KEY = 'k5aa6b5x6qo#9p+lx^k^_zp^ay30ksokl7z%xup4*y3=f4rdgk'

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
    ("ng", os.path.join(SITE_ROOT, 'gui', 'dist')),
)

STATICFILES_STORAGE = 'pipeline.storage.PipelineCachedStorage'
#STATICFILES_STORAGE = 'pipeline.storage.PipelineStorage'

MEDIA_ROOT = os.path.join(SITE_ROOT, 'media')
MEDIA_URL = '/m/'

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'pipeline.finders.FileSystemFinder',
    'pipeline.finders.AppDirectoriesFinder',
    'pipeline.finders.PipelineFinder',
    #'pipeline.finders.CachedFileFinder',  # Causes issue with .less files https://github.com/cyberdelia/django-pipeline/issues/293
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
    'toolkit.apps.task',
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
    'dj_authy',
    'dj_box',
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

    # django-permission
    'permission',

    # getsentry.com
    #'raven.contrib.django.raven_compat',
    'rollbar',

    # Payments
    'payments',

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

    # threadedcomments app needs to be above the django.contrib.comments app
    'threadedcomments',
    'django.contrib.comments',
    'toolkit.apps.discussion',  # NB needs to be in the defined order here AFTER actstream

    'jsonify',

    # social-auth
    'social.apps.django_app.sa_default',

    # integration for abridge; django-abridge
    'abridge',

    # Api helpers
    #'corsheaders',  # not required yet

    # Asset pipeline
    'pipeline',

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
    'dj_authy.middleware.AuthyAuthenticationRequiredMiddleware',
    'toolkit.apps.me.middleware.EnsureUserHasPasswordMiddleware',
    'social.apps.django_app.middleware.SocialAuthExceptionMiddleware',
    'django.middleware.gzip.GZipMiddleware',
    'pipeline.middleware.MinifyHTMLMiddleware',
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
    'social.apps.django_app.context_processors.backends',
    'social.apps.django_app.context_processors.login_redirect',
    'toolkit.context_processors.EXPOSED_GLOBALS',
    'toolkit.context_processors.FIRSTSEEN',
    'toolkit.context_processors.LAYOUT',
    'toolkit.context_processors.REQUESTS_COUNT',
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
LOGIN_REDIRECT_URL = '/'
LOGIN_ERROR_URL    = '/login-error/'
LOGOUT_URL = '/end/'

AUTHENTICATION_BACKENDS = (
    'toolkit.auth_backends.EmailBackend',
    #'social.backends.goclio.GoClioOAuth2',
    'social.backends.box.BoxOAuth2',
    'social.backends.dropbox.DropboxOAuth2',
    'django.contrib.auth.backends.ModelBackend',
    'toolkit.auth_backends.SecretKeyBackend',
    'toolkit.apps.review.auth_backends.ReviewDocumentBackend',  # allow users to log in via review urls
    'permission.backends.PermissionBackend',  # use django-permission
)

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
TEMPLATED_EMAIL_BACKEND = 'templated_email.backends.vanilla_django'

COMMENTS_APP = 'toolkit.apps.discussion'

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
#CELERY_ACKS_LATE = True  # as we want to to be acknowledged after its completed; http://celery.readthedocs.org/en/latest/configuration.html#celery-acks-late

FILEPICKER_API_KEY = 'A4Ly2eCpkR72XZVBKwJ06z'

CORS_ORIGIN_WHITELIST = (
    'localhost:9000'
)

REST_FRAMEWORK = {
    # Use hyperlinked styles by default.
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.JSONPRenderer',
        #'rest_framework.renderers.UnicodeJSONRenderer',
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


PIPELINE_CSS = {
  'core': {
        'source_filenames': (
            'bootstrap/css/bootstrap.css',
            'css/flat-ui.css',
            'fonts/pe-icon-7-stroke/css/pe-icon-7-stroke.css',
            'css/application.css',
            'css/animate.css',
            'less/introjs-custom.less'
            'css/font-awesome.min.css'
        ),
        'output_filename': 'css/core.css',
        'extra_context': {
            'media': 'screen,projection',
        },
  }
}
PIPELINE_JS = {
    'core': {
        'source_filenames': (
            'js/jquery.ui.touch-punch.min.js',
            'js/jquery.tagsinput.js',
            'js/jquery.placeholder.js',

            'js/bootstrap-select.js',
            'js/bootstrap-switch.js',
            'js/bootstrap-typeahead.js',

            'js/flatui-checkbox.js',
            'js/flatui-radio.js',

            'js/parsley-1.2.4.min.js',
            'js/parsley-form.js',

            'js/application.js',
        ),
        'output_filename': 'js/core.js',
    },

    'matter_list': {
        'source_filenames': (
            'js/react-0.11.1.js',
            'js/matter_list.jsx',
        ),
        'output_filename': 'js/jsx-matter_list-compiled.js',
    },
    'request_list': {
        'source_filenames': (
            'js/react-0.11.1.js',
            'js/request_list.jsx',
        ),
        'output_filename': 'js/jsx-request_list-compiled.js',
    }
}
PIPELINE_COMPILERS = [
    'pipeline.compilers.less.LessCompiler',
    'react.utils.pipeline.JSXCompiler',
]

CRISPY_TEMPLATE_PACK = 'bootstrap3'


#
# Social Auth
#
REDIRECT_IS_HTTPS = False
SOCIAL_AUTH_LOGIN_URL = LOGIN_URL
SOCIAL_AUTH_LOGIN_ERROR_URL = LOGIN_ERROR_URL


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

# how long are users allowed to edit/delete their comments (in minutes)
DELETE_COMMENTS_DURATION = 60
EDIT_COMMENTS_DURATION = DELETE_COMMENTS_DURATION

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
# BILLING_MATTER_LIMIT
#

BILLING_MATTER_LIMIT = {
    'ENABLED': False,
    'MAX_FREE_MATTERS': 3,
    'EXCLUDE_EMAILS': ('yael@lawpal.com', 'csandersreach@chicagobar.org',),
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

                      # Signing
                      'item-sent-for-signing', 'item-completed-signing-setup',
                      #'item-viewed-signature-request', # removed due to it being overkill
                      'item-signed',

                      # activate nearly everything for testing;
                      'item-reopened', 'item-closed',
                      'item-commented', 'item-comment-created', 'item-comment-deleted',
                      'item-invited-reviewer',
                      'item-provide-a-document',
                      'item-added-signer',
                      'item-completed-review',
                      'item-completed-all-reviews',
                      # Tasks
                      'item-task-added', 'item-task-deleted',
                      'item-task-completed','item-task-reopened',

                      'revision-created', 'revision-comment-created', 'item-added-revision-comment',
                      'revision-added-revision-comment',
                      'revision-added-review-session-comment',
                      'revision-changed-the-status',

                      'workspace-deleted',
                      'workspace-added-participant', 'workspace-removed-participant',
                      'workspace-stopped-participating',
                      'workspace-export-started',
                      'workspace-export-finished',
                      'workspace-export-downloaded',
                      ]
    },
    "notifications": {
        "whitelist": [
                      # Signing
                      'item-sent-for-signing', 'item-completed-signing-setup',
                      #'item-viewed-signature-request', # removed due to it being overkill
                      'item-signed',

                      'item-reopened', 'item-closed',
                      'item-commented', 'item-comment-created', 'item-comment-deleted',
                      'item-invited-reviewer',
                      'item-provide-a-document',
                      'item-added-signer',
                      'item-completed-review',
                      'item-completed-all-reviews',
                      # Tasks
                      'item-task-added', 'item-task-deleted',
                      'item-task-completed','item-task-reopened',

                      'revision-created', 'revision-comment-created', 'item-added-revision-comment',
                      'revision-added-revision-comment',
                      'revision-added-review-session-comment',
                      'revision-changed-the-status',

                      'workspace-deleted',
                      'workspace-added-participant', 'workspace-removed-participant',
                      'workspace-stopped-participating',
                      'workspace-export-started',
                      'workspace-export-finished',
                      'workspace-export-downloaded',
                      ]
    },
    "activity": {
        "whitelist": [
                      # Signing
                      'item-sent-for-signing', 'item-completed-signing-setup',
                      'item-viewed-signature-request',  # kept for record reasons
                      'item-signed',

                      'item-created', 'item-edited', 'item-commented', 'item-changed-the-status', 'item-renamed',
                      'item-provide-a-document', 'item-invited-reviewer', 'item-canceled-their-request-for-a-document',
                      'item-closed', 'item-reopened', 'item-added-revision-comment', 'item-deleted-revision-comment',
                      'item-completed-review', 'item-viewed-revision',
                      'item-completed-all-reviews',
                      'item-added-signer',
                      'itemrequestrevisionview-provide-a-document',
                      # Tasks
                      'item-task-added', 'item-task-deleted',
                      'item-task-completed','item-task-reopened',

                      'revision-created', 'revision-deleted',
                      'revision-added-review-session-comment',
                      'revision-added-revision-comment', 'revision-deleted-revision-comment',
                      'revision-changed-the-status',

                      'workspace-created', 'workspace-deleted',
                      'workspace-added-participant', 'workspace-removed-participant',
                      'workspace-stopped-participating',
                      'workspace-export-started',
                      'workspace-export-finished',
                      'workspace-export-downloaded',
                      ]
    },
}


#
# Payments
#
PAYMENTS_PLANS = {
    "early-bird-monthly": {
        "stripe_plan_id": "early-bird-monthly",
        "name": "Early Bird",
        "description": "Signup for LawPal's Early Bird plan and save! <br />Create unlimited projects with unlimited collaborators.<br /> Available for a limited time only.",
        "features": "Unlimited Projects<br/> Unlimited Collaborators<br/> E-Signing<br/> Priority Support<br/> No long-term commitment",
        "price": 25,
        "currency": "usd",
        "interval": "month"
    }
}

MATTER_EXPORT_DAYS_VALID = 3

REMIND_DUE_DATE_LIMIT = 7

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
