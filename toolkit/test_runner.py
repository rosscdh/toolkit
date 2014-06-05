# -*- coding: utf-8 -*-
from django.conf import settings
from django.core.management import call_command
from django.test.simple import DjangoTestSuiteRunner

from rainbowrunners.djrunner import NyanCatDiscoverRunner

import os
import shutil

# PROD_SETTINGS_SRC = os.path.join(settings.SITE_ROOT, 'conf', 'production.local_settings.py')
# PROD_SETTINGS_DEST = os.path.join(settings.SITE_ROOT, 'toolkit', 'production_settings.py')

# assert PROD_SETTINGS_SRC, 'Must have a conf/production.local_settings.py defined'


class AppTestRunner(NyanCatDiscoverRunner, DjangoTestSuiteRunner):
    def build_suite(self, test_labels, *args, **kwargs):
        # not args passed in
        if not test_labels:
            test_labels = []
            # Remove path info and use only the app "label"
            for app in settings.PROJECT_APPS:
                app_name = app.split('.')[-1]
                test_labels.append(app_name)
            test_labels = tuple(test_labels)

        return super(AppTestRunner, self).build_suite(test_labels, *args, **kwargs)

    # def setup_test_environment(self, **kwargs):
    #     # call_command('collectstatic', interactive=False)  # collect static so our casper tests break less

    #     # copy the conf/production.local_settings.py to toolkit/production_settings.py
    #     # so that we can test the various production settings *in mattters for eg
    #     shutil.copyfile(PROD_SETTINGS_SRC, PROD_SETTINGS_DEST)

    #     assert os.path.isfile(PROD_SETTINGS_DEST), 'Could not copy the conf/production.local_settings.py file'

    #     super(AppTestRunner, self).setup_test_environment(**kwargs)

    # def teardown_test_environment(self, **kwargs):
    #     #shutil.rmtree(settings.STATIC_ROOT)  # delete the static folder

    #     # Remove the prod settings which are only present so we can test them
    #     if os.path.exists(PROD_SETTINGS_DEST):
    #         os.remove(PROD_SETTINGS_DEST)

    #     super(AppTestRunner, self).teardown_test_environment(**kwargs)