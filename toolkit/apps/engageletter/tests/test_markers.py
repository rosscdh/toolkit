# -*- coding: utf-8 -*-
from django.test import TestCase
from django.core.urlresolvers import reverse

import mock

from toolkit.apps.workspace.markers import Marker
from toolkit.casper.workflow_case import BaseScenarios

from ..markers import EngagementLetterSignalMarkers
from ..markers import (LawyerSetupTemplateMarker,
                      LawyerCreateLetterMarker,
                      LawyerInviteUserMarker,
                      CustomerCompleteLetterFormMarker,
                      CustomerSignAndSendMarker,
                      CustomerDownloadMarker,
                      LawyerDownloadMarker,
                      ProcessCompleteMarker)


class EngagementLetterSignalMarkersTest(TestCase):
    """
    Test the base engagement letter signal markers handler
    """
    def setUp(self):
        super(EngagementLetterSignalMarkersTest, self).setUp()
        self.subject = EngagementLetterSignalMarkers

    def test_correct_init(self):
        subject = self.subject()
        self.assertEqual(len(subject.signal_map), 8)

    def test_signal_map_name_vals(self):
        subject = self.subject()
        name_vals = [(m.name, m.val) for m in subject.signal_map]

        self.assertEqual(len(name_vals), 8)

        self.assertEqual(name_vals, [('lawyer_setup_template', 0),
                                     ('lawyer_complete_form', 1),
                                     ('lawyer_invite_customer', 2),
                                     ('customer_complete_form', 3),
                                     ('customer_sign_and_send', 4),
                                     ('customer_download_letter', 5),
                                     ('lawyer_download_letter', 6),
                                     ('complete', 7)])


class BaseTestMarker(BaseScenarios, TestCase):
    val = None
    clazz = LawyerSetupTemplateMarker

    def setUp(self):
        super(BaseTestMarker, self).setUp()
        self.basic_workspace()

        self.subject = self.clazz(self.val)
        self.subject.tool = self.eightythreeb

    def test_has_properties(self):
        self.assertTrue(hasattr(self.subject, 'tool'))
        self.assertTrue(hasattr(self.subject, 'val'))
        self.assertTrue(hasattr(self.subject, 'name'))
        self.assertTrue(hasattr(self.subject, 'description'))
        self.assertTrue(hasattr(self.subject, 'signals'))
        self.assertTrue(hasattr(self.subject, 'action_name'))
        self.assertTrue(hasattr(self.subject, 'action_type'))
        self.assertTrue(hasattr(self.subject, 'action_user_class'))

    def test_action_attribs(self):
        self.assertEqual(self.subject.action_attribs, {})

    def test_get_action_url(self):
        with self.assertRaises(NotImplementedError):
            self.subject.get_action_url()

    def test_action(self):
        with self.assertRaises(NotImplementedError):
            self.subject.action


class LawyerSetupTemplateMarkerTest(BaseTestMarker):
    val = 0
    clazz = LawyerSetupTemplateMarker

    def test_properties(self):
        self.assertTrue(type(self.subject), self.clazz)
        self.assertEqual(self.subject.val, self.val)
        self.assertEqual(self.subject.name, 'lawyer_setup_template')
        self.assertEqual(self.subject.description, 'Attorney: Setup Engagement Letter Template')
        self.assertEqual(self.subject.signals, ['toolkit.apps.engageletter.signals.lawyer_setup_template'])
        self.assertEqual(self.subject.action_name, 'Setup Engagement Letter Template')
        self.assertEqual(self.subject.action_type, Marker.ACTION_TYPE.redirect)
        self.assertEqual(self.subject.action_user_class, ['lawyer'])


class LawyerCreateLetterMarkerTest(BaseTestMarker):
    val = 0
    clazz = LawyerCreateLetterMarker

    def test_properties(self):
        self.assertTrue(type(self.subject), self.clazz)
        self.assertEqual(self.subject.val, self.val)
        self.assertEqual(self.subject.name, 'lawyer_complete_form')
        self.assertEqual(self.subject.description, 'Attorney: Create Engagement Letter')
        self.assertEqual(self.subject.signals, ['toolkit.apps.engageletter.signals.lawyer_complete_form'])
        self.assertEqual(self.subject.action_name, 'Create Engagement Letter')
        self.assertEqual(self.subject.action_type, Marker.ACTION_TYPE.redirect)
        self.assertEqual(self.subject.action_user_class, ['lawyer'])


class LawyerInviteUserMarkerTest(BaseTestMarker):
    val = 0
    clazz = LawyerInviteUserMarker

    def test_properties(self):
        self.assertTrue(type(self.subject), self.clazz)
        self.assertEqual(self.subject.val, self.val)
        self.assertEqual(self.subject.name, 'lawyer_invite_customer')
        self.assertEqual(self.subject.description, 'Attorney: Invite client to complete & sign the Engagement Letter')
        self.assertEqual(self.subject.signals, ['toolkit.apps.engageletter.signals.lawyer_invite_customer'])
        self.assertEqual(self.subject.action_name, 'Invite Client to Complete & Sign')
        self.assertEqual(self.subject.action_type, Marker.ACTION_TYPE.redirect)
        self.assertEqual(self.subject.action_user_class, ['lawyer'])


class CustomerCompleteLetterFormMarkerTest(BaseTestMarker):
    val = 0
    clazz = CustomerCompleteLetterFormMarker

    def test_properties(self):
        self.assertTrue(type(self.subject), self.clazz)
        self.assertEqual(self.subject.val, self.val)
        self.assertEqual(self.subject.name, 'customer_complete_form')
        self.assertEqual(self.subject.description, 'Client: Complete Engagement Letter')
        self.assertEqual(self.subject.signals, ['toolkit.apps.engageletter.signals.customer_complete_form'])
        self.assertEqual(self.subject.action_name, 'Complete Engagement Letter')
        self.assertEqual(self.subject.action_type, Marker.ACTION_TYPE.redirect)
        self.assertEqual(self.subject.action_user_class, ['customer'])


class CustomerSignAndSendMarkerTest(BaseTestMarker):
    val = 0
    clazz = CustomerSignAndSendMarker

    def test_properties(self):
        self.assertTrue(type(self.subject), self.clazz)
        self.assertEqual(self.subject.val, self.val)
        self.assertEqual(self.subject.name, 'customer_sign_and_send')
        self.assertEqual(self.subject.description, 'Client: Sign & Send the Engagement Letter')
        self.assertEqual(self.subject.signals, ['toolkit.apps.engageletter.signals.customer_sign_and_send'])
        self.assertEqual(self.subject.action_name, 'Complete Engagement Letter')
        self.assertEqual(self.subject.action_type, Marker.ACTION_TYPE.redirect)
        self.assertEqual(self.subject.action_user_class, ['customer'])


class CustomerDownloadMarkerTest(BaseTestMarker):
    val = 0
    clazz = CustomerDownloadMarker

    def test_properties(self):
        self.assertTrue(type(self.subject), self.clazz)
        self.assertEqual(self.subject.val, self.val)
        self.assertEqual(self.subject.name, 'customer_download_letter')
        self.assertEqual(self.subject.description, 'Client: Download Signed Engagement Letter')
        self.assertEqual(self.subject.signals, ['toolkit.apps.engageletter.signals.customer_download_letter'])
        self.assertEqual(self.subject.action_name, 'Download Engagement Letter')
        self.assertEqual(self.subject.action_type, Marker.ACTION_TYPE.redirect)
        self.assertEqual(self.subject.action_user_class, ['customer'])


class LawyerDownloadMarkerTest(BaseTestMarker):
    val = 0
    clazz = LawyerDownloadMarker

    def test_properties(self):
        self.assertTrue(type(self.subject), self.clazz)
        self.assertEqual(self.subject.val, self.val)
        self.assertEqual(self.subject.name, 'lawyer_download_letter')
        self.assertEqual(self.subject.description, 'Attorney: Download Signed Engagement Letter')
        self.assertEqual(self.subject.signals, ['toolkit.apps.engageletter.signals.lawyer_download_letter'])
        self.assertEqual(self.subject.action_name, 'Download Engagement Letter')
        self.assertEqual(self.subject.action_type, Marker.ACTION_TYPE.redirect)
        self.assertEqual(self.subject.action_user_class, ['lawyer'])


class ProcessCompleteMarkerTest(BaseTestMarker):
    val = 0
    clazz = ProcessCompleteMarker

    def test_properties(self):
        self.assertTrue(type(self.subject), self.clazz)
        self.assertEqual(self.subject.name, 'complete')
        self.assertEqual(self.subject.val, self.val)
        self.assertEqual(self.subject.description, 'Process Complete')
        self.assertEqual(self.subject.signals, ['toolkit.apps.engageletter.signals.complete'])
        self.assertEqual(self.subject.action_name, None)
        self.assertEqual(self.subject.action_type, None)
        self.assertEqual(self.subject.action_user_class, [])
