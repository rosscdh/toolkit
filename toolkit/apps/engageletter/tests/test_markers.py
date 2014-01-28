# -*- coding: utf-8 -*-
from django.test import TestCase
from django.core.urlresolvers import reverse

from model_mommy import mommy
import mock

from toolkit.apps.workspace.markers import Marker
from toolkit.casper.workflow_case import BaseScenarios

from .data import ENGAGELETTER_DATA as BASE_ENGAGELETTER_DATA
from ..models import EngagementLetter
from ..markers import EngagementLetterMarkers
from ..markers import (LawyerSetupTemplatePrerequisite,
                      LawyerCreateLetterMarker,
                      LawyerInviteUserMarker,
                      CustomerCompleteLetterFormMarker,
                      CustomerSignAndSendMarker,
                      ProcessCompleteMarker)


class EngagementLetterMarkersTest(TestCase):
    """
    Test the base engagement letter signal markers handler
    """
    def setUp(self):
        super(EngagementLetterMarkersTest, self).setUp()
        self.subject = EngagementLetterMarkers

    def test_correct_init(self):
        subject = self.subject()
        self.assertEqual(len(subject.signal_map), 6)

    def test_signal_map_name_vals(self):
        subject = self.subject()
        name_vals = [(m.name, m.val) for m in subject.signal_map]

        self.assertEqual(len(name_vals), 6)

        self.assertEqual(name_vals, [('lawyer_complete_form', 1),
                                     ('lawyer_review_letter_text', 2),
                                     ('lawyer_invite_customer', 3),
                                     ('customer_complete_form', 4),
                                     ('customer_sign_and_send', 5),
                                     ('complete', 6)])

    def test_prerequisite_vals(self):
        subject = self.subject()
        name_vals = [(m.name, m.val) for m in subject.prerequisite_signal_map]

        self.assertEqual(len(name_vals), 1)
        self.assertEqual(name_vals, [('lawyer_setup_template', 0)])

    def test_signal_map_items_next_previous_values(self):
        subject = self.subject()
        test = [(m.next_marker, m.previous_marker, m.markers_map) for m in subject.signal_map]



class BaseTestMarker(BaseScenarios, TestCase):
    val = None
    subject = None
    clazz = LawyerSetupTemplatePrerequisite

    def setUp(self):
        super(BaseTestMarker, self).setUp()
        self.basic_workspace()
        if self.val is not None:
            if self.clazz.is_prerequisite is True:
                self.subject = self.clazz(self.val, workspace=self.workspace)
            else:
                self.subject = self.clazz(self.val)

            data = BASE_ENGAGELETTER_DATA.copy()
            if 'lawyer_complete_form' in data['markers']:
                del data['markers']['lawyer_complete_form']

            self.subject.tool = mommy.make('engageletter.EngagementLetter',
                                slug='d1c545082d1241849be039e338e47aa0',
                                workspace=self.workspace,
                                user=self.user,
                                data=data,
                                status=EngagementLetter.STATUS.lawyer_complete_form)

    def test_has_properties(self):
        if self.val is not None:
            self.assertTrue(hasattr(self.subject, 'tool'))
            self.assertTrue(hasattr(self.subject, 'val'))
            self.assertTrue(hasattr(self.subject, 'name'))
            self.assertTrue(hasattr(self.subject, 'description'))
            self.assertTrue(hasattr(self.subject, 'signals'))
            self.assertTrue(hasattr(self.subject, 'action_name'))
            self.assertTrue(hasattr(self.subject, 'action_type'))
            self.assertTrue(hasattr(self.subject, 'action_user_class'))

    def test_action_attribs(self):
        if self.val is not None:
            self.assertEqual(self.subject.action_attribs, {'toggle': 'action'})

    def test_get_action_url(self):
        if self.val is not None:
            with self.assertRaises(NotImplementedError):
                self.subject.get_action_url()

    def test_action(self):
        if self.val is not None:
            with self.assertRaises(NotImplementedError):
                self.subject.action


class LawyerSetupTemplatePrerequisiteTest(BaseTestMarker):
    val = 0
    clazz = LawyerSetupTemplatePrerequisite

    def test_properties(self):
        self.assertTrue(type(self.subject), self.clazz)
        self.assertEqual(self.subject.val, self.val)
        self.assertEqual(self.subject.name, 'lawyer_setup_template')
        self.assertEqual(self.subject.description, 'Attorney: Setup Letterhead Template')
        self.assertEqual(self.subject.signals, ['toolkit.apps.engageletter.signals.lawyer_setup_template'])
        self.assertEqual(self.subject.action_name, 'Edit Letterhead Template')
        self.assertEqual(self.subject.action_type, Marker.ACTION_TYPE.redirect)
        self.assertEqual(self.subject.action_user_class, ['lawyer'])

    def test_get_action_url(self):
        self.assertEqual(self.subject.get_action_url(), '/me/settings/letterhead/?next=/workspace/lawpal-test/tool/engagement-letters/create/')

    def test_action(self):
        self.assertEqual(self.subject.action, '/me/settings/letterhead/?next=/workspace/lawpal-test/tool/engagement-letters/create/')


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

    def test_get_action_url(self):
        url = reverse('workspace:tool_object_edit', kwargs={'workspace': self.subject.tool.workspace.slug, 'tool': self.subject.tool.tool_slug, 'slug': self.subject.tool.slug})
        self.assertEqual(self.subject.get_action_url(), url)

    def test_action(self):
        url = reverse('workspace:tool_object_edit', kwargs={'workspace': self.subject.tool.workspace.slug, 'tool': self.subject.tool.tool_slug, 'slug': self.subject.tool.slug})
        self.assertEqual(self.subject.action, url)


class LawyerInviteUserMarkerTest(BaseTestMarker):
    val = 0
    clazz = LawyerInviteUserMarker

    def test_properties(self):
        self.assertTrue(type(self.subject), self.clazz)
        self.assertEqual(self.subject.val, self.val)
        self.assertEqual(self.subject.name, 'lawyer_invite_customer')
        self.assertEqual(self.subject.description, 'Attorney: Invite client to complete & sign the Engagement Letter')
        self.assertEqual(self.subject.signals, ['toolkit.apps.engageletter.signals.lawyer_invite_customer'])
        self.assertEqual(self.subject.action_name, 'Invite Client')
        self.assertEqual(self.subject.action_type, Marker.ACTION_TYPE.redirect)
        self.assertEqual(self.subject.action_user_class, ['lawyer'])

    def test_get_action_url(self):
        url = reverse('workspace:tool_object_invite', kwargs={'workspace': self.subject.tool.workspace.slug, 'tool': self.subject.tool.tool_slug, 'slug': self.subject.tool.slug})
        self.assertEqual(self.subject.get_action_url(), url)

    def test_action(self):
        url = reverse('workspace:tool_object_invite', kwargs={'workspace': self.subject.tool.workspace.slug, 'tool': self.subject.tool.tool_slug, 'slug': self.subject.tool.slug})
        self.assertEqual(self.subject.action, url)


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

    def test_get_action_url(self):
        url = reverse('workspace:tool_object_edit', kwargs={'workspace': self.subject.tool.workspace.slug, 'tool': self.subject.tool.tool_slug, 'slug': self.subject.tool.slug})
        self.assertEqual(self.subject.get_action_url(), url)

    def test_action(self):
        url = reverse('workspace:tool_object_edit', kwargs={'workspace': self.subject.tool.workspace.slug, 'tool': self.subject.tool.tool_slug, 'slug': self.subject.tool.slug})
        self.assertEqual(self.subject.action, url)


class CustomerSignAndSendMarkerTest(BaseTestMarker):
    val = 0
    clazz = CustomerSignAndSendMarker

    def test_properties(self):
        self.assertTrue(type(self.subject), self.clazz)
        self.assertEqual(self.subject.val, self.val)
        self.assertEqual(self.subject.name, 'customer_sign_and_send')
        self.assertEqual(self.subject.description, 'Client: Sign & Send the Engagement Letter')
        self.assertEqual(self.subject.signals, ['toolkit.apps.engageletter.signals.customer_sign_and_send'])
        self.assertEqual(self.subject.action_name, 'Sign Engagment Letter')
        self.assertEqual(self.subject.action_type, Marker.ACTION_TYPE.redirect)
        self.assertEqual(self.subject.action_user_class, ['customer'])

    def test_get_action_url(self):
        url = reverse('engageletter:sign', kwargs={'slug': self.subject.tool.slug})
        self.assertEqual(self.subject.get_action_url(), url)

    def test_action(self):
        url = reverse('engageletter:sign', kwargs={'slug': self.subject.tool.slug})
        self.assertEqual(self.subject.action, url)


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

    def test_action_attribs(self):
        self.assertEqual(self.subject.action_attribs, {})
