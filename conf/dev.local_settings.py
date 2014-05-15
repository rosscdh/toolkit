# -*- coding: utf-8 -*-
LOCAL_SETTINGS = True
from settings import *

SITE_ID = 1

PROJECT_ENVIRONMENT = 'dev'

DEBUG = True
TEST_PREPROD = False  # set to true and DEBUG = False in order to test angular app

if TEST_PREPROD is True:
    STATICFILES_DIRS = (
        # These are the production files
        # not that static is in gui/dist/static *not to be confused with the django {{ STATIC_URL }}ng/ which will now point correctly
        ("ng", os.path.join(SITE_ROOT, 'gui', 'dist')),
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

AUTHY_API_KEY = 'e19afad3c1c207a03ef6a1dcb2adb0c3'

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
ENABLE_CELERY_TASKS = True
