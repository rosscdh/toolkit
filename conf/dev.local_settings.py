# -*- coding: utf-8 -*-
LOCAL_SETTINGS = True
from settings import *

SITE_ID = 1

PROJECT_ENVIRONMENT = 'dev'

DEBUG = True
TEST_PREPROD = False  # set to true and DEBUG = False in order to test angular app

if TEST_PREPROD is True:
    #
    # If in prod mode load from the gui/dist path (ie only the selected components)
    # this implies that we need to manually specify the selected components in GruntFile
    #
    STATICFILES_DIRS = (
        # These are the production files
        # not that static is in gui/dist/static *not to be confused with the django {{ STATIC_URL }}ng/ which will now point correctly
        ("ng", os.path.join(SITE_ROOT, 'gui', 'dist')),
    )
    #
    # NB! note the .min use here for react
    #
    PIPELINE_JS = {
        'reactjs': {
            'source_filenames': (
                'js/react-0.10.0.min.js',
                'js/matter_list.jsx',
            ),
            'output_filename': 'js/jsx-all-compiled.js',
        }
    }

else:
    #
    # If in debug mode load from the gui path (ie all of the components)
    #
    STATICFILES_DIRS = (
        # These are the dev files
        ("ng", os.path.join(SITE_ROOT, 'gui')),
    )

INSTALLED_APPS = INSTALLED_APPS + (
    'debug_toolbar',
    # User switcher
    'debug_toolbar_user_panel',
    # Debug toolbar panels
    'template_timings_panel',
)

INTERNAL_IPS = ('127.0.0.1',)

DEBUG_TOOLBAR_PANELS = (
    'debug_toolbar.panels.version.VersionDebugPanel',
    'debug_toolbar.panels.timer.TimerDebugPanel',
    'debug_toolbar.panels.settings_vars.SettingsVarsDebugPanel',
    'debug_toolbar.panels.headers.HeaderDebugPanel',
    'debug_toolbar.panels.request_vars.RequestVarsDebugPanel',
    'debug_toolbar.panels.template.TemplateDebugPanel',
    'debug_toolbar.panels.sql.SQLDebugPanel',
    'debug_toolbar.panels.signals.SignalDebugPanel',
    'debug_toolbar.panels.logger.LoggingPanel',
    'debug_toolbar_user_panel.panels.UserPanel',
    'template_timings_panel.panels.TemplateTimings.TemplateTimings',
)
MIDDLEWARE_CLASSES += (
    'debug_toolbar.middleware.DebugToolbarMiddleware',
)
DEBUG_TOOLBAR_CONFIG = {
    'INTERCEPT_REDIRECTS': False
}

CROCDOC_API_KEY = '27FXmeRJ3StkMZGxi46UTwWH'

#
# Authy
#
AUTHY_KEY = 'bcdfb7ce5e6854dcfe65ce5dd0d568c7'
AUTHY_IS_SANDBOXED = True

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

# how long are users allowed to edit/delete their comments (in minutes)
DELETE_COMMENTS_DURATION = 60
EDIT_COMMENTS_DURATION = DELETE_COMMENTS_DURATION

#
# Abridge Integration
#

ABRIDGE_ENABLED = False if sys.argv[1] in ['syncdb', 'migrate', 'test', 'loaddata'] else True  # disable when we are syncing or migrating or loadingdata

ABRIDGE_PROJECT = 'lawpal-digest'

ABRIDGE_API_URL = 'http://localhost:8001/'
ABRIDGE_ACCESS_KEY_ID = ''
ABRIDGE_SECRET_ACCESS_KEY = ''
ABRIDGE_USERNAME = ''
ABRIDGE_PASSWORD = ''

INTERCOM_APP_ID = 'wkxzfou'
INTERCOM_APP_SECRET = 'MZCesCDxkDrYdfX8HocAB2F6V5aZzCm-DuF7lyR5'

#
# Mixpanel Analytics
#
MIXPANEL_SETTINGS = {
    'token': '92deaf40d5aa77e00bf8f764002950ab',
}

#
# Payments
#
STRIPE_PUBLIC_KEY = 'sk_test_8Po9Bh0rj12nISHPFsOQz46Q'
STRIPE_SECRET_KEY = 'pk_test_pVBXSHiazhp3b0EyGHQa8Dx2'

#
# Celery SQS Tasks
#
CELERY_DEFAULT_QUEUE = 'lawpal-local'
ENABLE_CELERY_TASKS = False

#
# Authy
#
AUTHY_KEY = 'bcdfb7ce5e6854dcfe65ce5dd0d568c7'
AUTHY_IS_SANDBOXED = True

#
# Pusher
#
PUSHER_APP_ID = 44301
PUSHER_KEY = '514360ee427ceb00cd8d'
PUSHER_SECRET = '8fa687dde7e745e8f9d7'


#
# HelloSign
#
HELLOSIGN_AUTHENTICATION = ("ross@lawpal.com", "test2007")
HELLOSIGN_API_KEY = '75dd93222c11eb4483a98ddc7898022bb86d4b9e6d11113b2b9214b90daa3160'
HELLOSIGN_CLIENT_ID = '11603fe6a0664760ac06d67789ce982c'
HELLOSIGN_CLIENT_SECRET = '47c36768e08d72b1084979b1f8edc133'
