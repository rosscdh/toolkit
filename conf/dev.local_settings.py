# -*- coding: utf-8 -*-
LOCAL_SETTINGS = True
from settings import *

SITE_ID = 1

TEST_PREPROD = False  # set to true and DEBUG = False in order to test angular app
PROJECT_ENVIRONMENT = 'dev'

DEBUG = True
COMPRESSION_ENABLED = False


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

CROCDOC_API_KEY = 'pRzHhZS4jaGes193db28cwyu'

AUTHY_API_KEY = 'e19afad3c1c207a03ef6a1dcb2adb0c3'


#
# Abridge Integration
#

ABRIDGE_ENABLED = True  # disabled by default

ABRIDGE_PROJECT = 'lawpal-digest'

ABRIDGE_API_URL = 'http://localhost:8001/'
ABRIDGE_ACCESS_KEY_ID = ''
ABRIDGE_SECRET_ACCESS_KEY = ''
ABRIDGE_USERNAME = ''
ABRIDGE_PASSWORD = ''