# -*- coding: utf-8 -*-
from django.conf import settings
from django.core.management import call_command
from django.test.simple import DjangoTestSuiteRunner
from rainbowrunners.djrunner import NyanCatDiscoverRunner
import shutil


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
    #     call_command('collectstatic', interactive=False)  # collect static so our casper tests break less
    #     super(AppTestRunner, self).setup_test_environment(**kwargs)

    # def teardown_test_environment(self, **kwargs):
    #     shutil.rmtree(settings.STATIC_ROOT)  # delete the static folder
    #     super(AppTestRunner, self).teardown_test_environment(**kwargs)