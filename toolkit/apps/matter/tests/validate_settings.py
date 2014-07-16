# -*- coding: utf-8 -*-
import unittest

from django.conf import settings
# temporarily copied here in the toolkit.test_runner.setup_test_environment and teardown_test_environment
# will be deleted after tests run
#from toolkit import production_settings

import os


class MatterProductionSettingsTest(unittest.TestCase):
    """
    Ensure that the production settings are correct and setup so that in
    production; we hook up to the dist version of the angular app and not the
    dev. So we use the minified files and compiled production version of the app
    production {{ STATIC_URL }}ng/* is the path that should be used
    in production the STATICFILES_DIRS need to point at gui/dist so that all the files are copied into 
    our django static
    """
    expected_static_namespace = 'ng'
    expected_prod_relative_absolute_path = os.path.join(settings.SITE_ROOT, 'gui', 'dist')
    expected_dev_relative_absolute_path = os.path.join(settings.SITE_ROOT, 'gui')

    # def test_production_static_path(self):
    #     self.assertEqual(production_settings.STATICFILES_DIRS, ((self.expected_static_namespace, self.expected_prod_relative_absolute_path),))

    def test_dev_static_path(self):
        #
        # Ensure that you have 
        # DEBUG = True and 
        # TEST_PREPROD = False
        #
        self.assertEqual(settings.STATICFILES_DIRS, ((self.expected_static_namespace, self.expected_prod_relative_absolute_path),))