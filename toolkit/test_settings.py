# -*- coding: utf-8 -*-
LOCAL_SETTINGS = True

from settings import *

import hashlib
import random
import logging

logging.disable(logging.CRITICAL)

# Custom test runner for this project
TEST_RUNNER = 'toolkit.test_runner.AppTestRunner'

PROJECT_ENVIRONMENT = 'test'

INSTALLED_APPS = INSTALLED_APPS + (
    'casper',
    'colortools',
)

SOUTH_TESTS_MIGRATE = False
SKIP_SOUTH_TESTS = True

PASSWORD_HASHERS = (
    'django.contrib.auth.hashers.MD5PasswordHasher',
)


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
