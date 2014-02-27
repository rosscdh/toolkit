# -*- coding: utf-8 -*-
from django.test import TestCase

from model_mommy import mommy

from toolkit.casper.workflow_case import BaseScenarios
from toolkit.apps.eightythreeb.models import EightyThreeB

from ..markers.lawyers import LawyerSetupTemplateMarker

REQUIRED_MARKERS = ['firm_address', 'firm_logo']


class LawyerSetupTemplateMarker_IsCompleteTest(BaseScenarios, TestCase):
    """
    The LawyerSetupTemplateMarker should be is_complete if the spcified keys
    have a value that is not None
    """
    def setUp(self):
        super(LawyerSetupTemplateMarker_IsCompleteTest, self).setUp()
        self.basic_workspace()

        data = {}
        for key in LawyerSetupTemplateMarker.required_data_markers:
            data[key] = 'Yes we have a value for %s' % key

        profile = self.lawyer.profile
        profile.data = data
        profile.save(update_fields=['data'])

        self.subject = LawyerSetupTemplateMarker(1, workspace=self.workspace)
        self.subject.tool = self.eightythreeb

    def test_required_data_markers(self):
        self.assertEqual(LawyerSetupTemplateMarker.required_data_markers, REQUIRED_MARKERS)

    def test_is_complete(self):
        self.assertEqual(self.subject.tool.workspace.lawyer.profile.data, {u'firm_address': u'Yes we have a value for firm_address', u'firm_logo': u'Yes we have a value for firm_logo'})
        self.assertTrue(self.subject.is_complete)


class LawyerSetupTemplateMarker_IsNotCompleteTest(BaseScenarios, TestCase):
    """
    The LawyerSetupTemplateMarker should NOT be is_complete if the spcified keys
    are not present or have an invalid value
    """
    def setUp(self):
        super(LawyerSetupTemplateMarker_IsNotCompleteTest, self).setUp()
        self.basic_workspace()

        data = {}
        invalid = [None, '']
        for i, key in enumerate(LawyerSetupTemplateMarker.required_data_markers):
            val = invalid[1] if i%2 else invalid[0]  # set teh value to an invalid value from the list
            data[key] = val

        profile = self.lawyer.profile
        profile.data = data
        profile.save(update_fields=['data'])

        self.subject = LawyerSetupTemplateMarker(1, workspace=self.workspace)
        self.subject.tool = self.eightythreeb

    def test_is_complete_is_false(self):
        """
        should not be complete if we have invalid values in the key
        """
        self.assertEqual(self.subject.tool.workspace.lawyer.profile.data, {u'firm_address': None, u'firm_logo': u''})
        self.assertFalse(self.subject.is_complete)

    def test_is_complete_is_false_if_no_keys(self):
        """
        should not be complete if we have invalid values in the key
        """
        profile = self.lawyer.profile
        profile.data = {}
        profile.save(update_fields=['data'])

        self.assertEqual(self.subject.tool.workspace.lawyer.profile.data, {})
        self.assertFalse(self.subject.is_complete)
