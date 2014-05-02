# -*- coding: utf-8 -*-
from django.conf import settings
from casper.tests import CasperTestCase

import sys
import os.path

PROJECT_NAME = settings.ROOT_URLCONF.split('.')[0]


class BaseCasperJs(CasperTestCase):
    """
    Base Class with helper methods to load casper tests
    """
    @property
    def test_path(self):
        return os.path.dirname(sys.modules[self.__module__].__file__)

    def load_casper_file(self, js_file, **kwargs):
        casper_test_folder_path = kwargs.get('casper_test_folder', 'casper-tests')

        test_path = getattr(self, 'test_path', os.path.dirname(__file__))

        test_path = os.path.join(test_path, 
                                 casper_test_folder_path,
                                 js_file
                                )
        kwargs.update({
            'timeout': 30000,
            'casper_helper_js_path': kwargs.get('casper_helper_js_path', os.path.join(settings.SITE_ROOT, '{project}/casper/jslib/djangocasper.js'.format(project=PROJECT_NAME))),
            'STATIC_PATH': kwargs.get('STATIC_PATH', os.path.join(settings.SITE_ROOT, '{project}/apps/default/static/'.format(project=PROJECT_NAME))),
        })

        return self.casper(test_path, **kwargs)