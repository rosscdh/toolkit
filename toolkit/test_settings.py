# -*- coding: utf-8 -*-
LOCAL_SETTINGS = True

from settings import *

import hashlib
import random
import logging

logging.disable(logging.CRITICAL)

DEBUG = False # msut be set to false to emulate production
TEST_PREPROD = True  # so we can access local static assets

# Custom test runner for this project
TEST_RUNNER = 'toolkit.test_runner.AppTestRunner'

PROJECT_ENVIRONMENT = 'test'

ATOMIC_REQUESTS = True

INSTALLED_APPS = INSTALLED_APPS + (
    'casper',
    'colortools',
    # Lawpal modules
    #'toolkit.core.tests',
    'hello_sign.tests',
    'dj_crocodoc.tests',
)

SOUTH_TESTS_MIGRATE = False
SKIP_SOUTH_TESTS = True

PASSWORD_HASHERS = (
    'django.contrib.auth.hashers.MD5PasswordHasher',
)

#DEFAULT_FILE_STORAGE = 'inmemorystorage.InMemoryStorage'  # cant because of s3 tests

EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'

AWS_STORAGE_BUCKET_NAME = AWS_FILESTORE_BUCKET = 'dev-toolkit-lawpal-com'

STATICFILES_STORAGE = 'pipeline.storage.PipelineStorage'

HELLOSIGN_CLIENT_ID = '9bc892af173754698e3fa30dedee3826'
HELLOSIGN_CLIENT_SECRET = '8d770244b9971abfe789f5224552239d'

#
# Abridge Integration
#

ABRIDGE_ENABLED = False  # Disabled in testing


#
# Abridge Integration
#

ABRIDGE_ENABLED = False

ABRIDGE_PROJECT = 'lawpal-digest'

ABRIDGE_API_URL = 'http://abridge.local.dev/'
ABRIDGE_ACCESS_KEY_ID = 'empty'
ABRIDGE_SECRET_ACCESS_KEY = 'still_empty'
ABRIDGE_USERNAME = 'blah'
ABRIDGE_PASSWORD = 'blah'

#
# set the mixpanel token to None so that we dont send events in testing
#
MIXPANEL_SETTINGS = {
    'token': None,
}

# activate everything to make sure all events are really called
LAWPAL_ACTIVITY['activity']['whitelist'] = [
    'item-created', 'item-edited', 'item-commented', 'item-changed-the-status', 'item-renamed',
    'item-provide-a-document', 'item-invited-reviewer', 'item-canceled-their-request-for-a-document',
    'item-closed', 'item-reopened', 'item-added-revision-comment', 'item-deleted-revision-comment',
    'item-viewed-revision',
    'revision-created', 'revision-deleted',
    'item-invited-signer',
    'item-completed-all-reviews',
    'itemrequestrevisionview-provide-a-document',
    'workspace-created', 'workspace-added-participant', 'workspace-removed-participant']

# def AutoSlugFieldGenerator():
#     hash_val = '{r}'.format(r=random.random())
#     h = hashlib.sha1(hash_val)
#     return h.hexdigest()


# def FPFileFieldGenerator():
#     return '/tmp/test-file.pdf'

# MOMMY_CUSTOM_FIELDS_GEN = {
#     'autoslug.fields.AutoSlugField': AutoSlugFieldGenerator,
#     'django_filepicker.models.FPFileField': FPFileFieldGenerator,
# }


CELERY_DEFAULT_QUEUE = 'lawpal-test'
ENABLE_CELERY_TASKS = False
