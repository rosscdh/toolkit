# -*- coding: utf-8 -*-
from django.test import TestCase
from django.core.urlresolvers import reverse

import mock

from toolkit.casper.workflow_case import BaseScenarios
from toolkit.apps.workspace.markers import Marker

from ..markers import EightyThreeBSignalMarkers
from ..markers import (LawyerCompleteFormMarker,
                       LawyerInviteUserMarker,
                       CustomerCompleteFormMarker,
                       CustomerDownloadDocMarker,
                       CustomerPrintAndSignMarker,
                       CustomerUploadScanMarker,
                       CustomerTrackingNumberMarker,
                       USPSDeliveryStatusMarker,
                       ProcessCompleteMarker)


class EightyThreeBSignalMarkersTest(TestCase):
    """
    Test the base 83(b) signal markers handler
    """
    def setUp(self):
        super(EightyThreeBSignalMarkersTest, self).setUp()
        self.subject = EightyThreeBSignalMarkers

    def test_correct_init(self):
        subject = self.subject()
        self.assertEqual(len(subject.signal_map), 9)

    def test_signal_map_name_vals(self):
        subject = self.subject()
        name_vals = [(m.name, m.val) for m in subject.signal_map]

        self.assertEqual(len(name_vals), 9)

        self.assertEqual(name_vals, [('lawyer_complete_form', 0),
                                     ('lawyer_invite_customer', 1),
                                     ('customer_complete_form', 2),
                                     ('customer_download_pdf', 3),
                                     ('customer_print_and_sign', 4),
                                     ('copy_uploaded', 5),
                                     ('mail_to_irs_tracking_code', 6),
                                     ('irs_recieved', 7),
                                     ('complete', 8)])


class BaseTestMarker(BaseScenarios, TestCase):
    val = None
    clazz = LawyerInviteUserMarker

    def setUp(self):
        super(BaseTestMarker, self).setUp()
        self.basic_workspace()

        self.subject = self.clazz(self.val)
        self.subject.tool = self.eightythreeb

    def test_has_properties(self):
        self.assertTrue(hasattr(self.subject, 'tool'))
        self.assertTrue(hasattr(self.subject, 'name'))
        self.assertTrue(hasattr(self.subject, 'description'))
        self.assertTrue(hasattr(self.subject, 'signals'))
        self.assertTrue(hasattr(self.subject, 'action_name'))
        self.assertTrue(hasattr(self.subject, 'action_type'))
        self.assertTrue(hasattr(self.subject, 'action_user_class'))

    def test_action_attribs(self):
        self.assertEqual(self.subject.action_attribs, {})

    def test_get_action_url(self):
        url = reverse('workspace:tool_object_invite', kwargs={'workspace': self.subject.tool.workspace.slug, 'tool': self.subject.tool.tool_slug, 'slug': self.subject.tool.slug})
        self.assertEqual(self.subject.get_action_url(), url)


class LawyerCompleteFormMarkerTest(BaseTestMarker):
    val = 0
    clazz = LawyerCompleteFormMarker

    def test_properties(self):
        self.assertTrue(type(self.subject), self.clazz)
        self.assertEqual(self.subject.name, 'lawyer_complete_form')
        self.assertEqual(self.subject.description, 'Attorney: Setup 83(b) Election Letter')
        self.assertEqual(self.subject.signals, ['toolkit.apps.eightythreeb.signals.lawyer_complete_form'])
        self.assertEqual(self.subject.action_name, 'Setup 83(b)')
        self.assertEqual(self.subject.action_type, Marker.ACTION_TYPE.modal)
        self.assertEqual(self.subject.action_user_class, ['lawyer'])

    def test_action_attribs(self):
        self.assertEqual(self.subject.action_attribs, {'target': '#modal-lawyer_complete_form'})

    def test_get_action_url(self):
        self.assertEqual(self.subject.get_action_url(), self.subject.tool.get_edit_url())

    def test_action(self):
        self.assertEqual(self.subject.action, self.subject.tool.get_edit_url())

        # set as complete then the action should return None
        self.subject.tool.status = self.subject.tool.STATUS_83b.complete
        self.assertEqual(self.subject.action, None)

        # set as greater than the LawyerCompleteFormMarker.val then the action should also return None
        self.subject.tool.status = self.subject.tool.STATUS_83b.customer_download_pdf
        self.assertEqual(self.subject.action, None)


class LawyerInviteUserMarkerTest(BaseTestMarker):
    val = 1
    clazz = LawyerInviteUserMarker

    def test_properties(self):
        self.assertTrue(type(self.subject), self.clazz)
        self.assertEqual(self.subject.name, 'lawyer_invite_customer')
        self.assertEqual(self.subject.description, 'Attorney: Invite client to complete the 83(b) Election Letter')
        self.assertEqual(self.subject.signals, ['toolkit.apps.eightythreeb.signals.lawyer_invite_customer'])
        self.assertEqual(self.subject.action_name, 'Invite Client')
        self.assertEqual(self.subject.action_type, Marker.ACTION_TYPE.redirect)
        self.assertEqual(self.subject.action_user_class, ['lawyer'])

    def test_action_name(self):
        self.assertEqual(self.subject.action_name, 'Invite Client')

    def test_iscomplete_action_name(self):
        prop_mock = mock.PropertyMock()
        # mock out the is_complete property so we can test its post complete action name
        with mock.patch.object(self.clazz, 'is_complete', prop_mock):
            self.subject = self.clazz(self.val)
            prop_mock.return_value = True

            self.assertEqual(self.subject.action_name, 'Reinvite Client')

    def test_get_action_url(self):
        url = reverse('workspace:tool_object_invite', kwargs={'workspace': self.subject.tool.workspace.slug, 'tool': self.subject.tool.tool_slug, 'slug': self.subject.tool.slug})
        self.assertEqual(self.subject.get_action_url(), url)

    def test_action(self):
        prop_mock = mock.PropertyMock()

        # mock the subjects status so that its greater than the current markers val
        self.subject.tool.status = self.subject.tool.STATUS_83b.irs_recieved
        # on complete we dont have an action
        self.assertEqual(self.subject.action, None)

        # mock out the is_complete property so we can test its post complete action name
        with mock.patch.object(self.clazz, 'is_complete', prop_mock):
            self.subject = self.clazz(self.val)
            prop_mock.return_value = True
            self.subject.tool = self.eightythreeb
            # test we have this when is_complete = True
            self.assertEqual(self.subject.action, None)


class CustomerCompleteFormMarkerTest(BaseTestMarker):
    val = 2
    clazz = CustomerCompleteFormMarker

    def test_properties(self):
        self.assertTrue(type(self.subject), self.clazz)
        self.assertEqual(self.subject.name, 'customer_complete_form')
        self.assertEqual(self.subject.description, 'Client: Complete 83(b) Election Letter')
        self.assertEqual(self.subject.signals, ['toolkit.apps.eightythreeb.signals.customer_complete_form'])
        self.assertEqual(self.subject.action_name, 'Complete 83(b)')
        self.assertEqual(self.subject.action_type, Marker.ACTION_TYPE.redirect)
        self.assertEqual(self.subject.action_user_class, ['customer'])

    def test_get_action_url(self):
        self.assertEqual(self.subject.get_action_url(), self.subject.tool.get_edit_url())

    def test_action(self):
        prop_mock = mock.PropertyMock()

        # mock the subjects status so that its greater than the current markers val
        self.subject.tool.status = self.subject.tool.STATUS_83b.irs_recieved
        # on complete we dont have an action
        self.assertEqual(self.subject.action, None)

        # mock out the is_complete property so we can test its post complete action name
        with mock.patch.object(self.clazz, 'is_complete', prop_mock):
            self.subject = self.clazz(self.val)
            prop_mock.return_value = True
            self.subject.tool = self.eightythreeb
            # test we have this when is_complete = True
            self.assertEqual(self.subject.action, None)


class CustomerDownloadDocMarkerTest(BaseTestMarker):
    val = 3
    clazz = CustomerDownloadDocMarker

    def test_properties(self):
        self.assertTrue(type(self.subject), self.clazz)
        self.assertEqual(self.subject.name, 'customer_download_pdf')
        self.assertEqual(self.subject.description, 'Client: Download 83(b) Election Letter and Instructions')
        self.assertEqual(self.subject.long_description, '')
        self.assertEqual(self.subject.signals, ['toolkit.apps.eightythreeb.signals.customer_download_pdf'])
        self.assertEqual(self.subject.action_name, 'Download 83(b)')
        self.assertEqual(self.subject.action_type, Marker.ACTION_TYPE.redirect)
        self.assertEqual(self.subject.action_user_class, ['customer'])

    def test_get_action_url(self):
        url = reverse('workspace:tool_object_download', kwargs={'workspace': self.subject.tool.workspace.slug, 'tool': self.subject.tool.tool_slug, 'slug': self.subject.tool.slug})
        self.assertEqual(self.subject.get_action_url(), url)

    def test_action(self):
        prop_mock = mock.PropertyMock()
        action_url = url = reverse('workspace:tool_object_download', kwargs={'workspace': self.subject.tool.workspace.slug, 'tool': self.subject.tool.tool_slug, 'slug': self.subject.tool.slug})

        # the download button will NOT show when the status < the download value
        self.subject.tool.status = self.subject.tool.STATUS_83b.lawyer_invite_customer
        self.assertEqual(self.subject.action, None)

        # the download button will show when the status > the download value
        self.subject.tool.status = self.subject.tool.STATUS_83b.irs_recieved
        # on complete we do have an action
        self.assertEqual(self.subject.action, action_url)


class CustomerPrintAndSignMarkerTest(BaseTestMarker):
    val = 4
    clazz = CustomerPrintAndSignMarker

    def test_properties(self):
        self.assertTrue(type(self.subject), self.clazz)
        self.assertEqual(self.subject.name, 'customer_print_and_sign')
        self.assertEqual(self.subject.description, 'Client: Print, check and sign 83(b) Election Letter')
        self.assertEqual(self.subject.long_description, 'Print and sign the 83(b) Election where indicated.')
        self.assertEqual(self.subject.signals, ['toolkit.apps.eightythreeb.signals.customer_print_and_sign'])
        self.assertEqual(self.subject.action_name, 'I have printed and signed the Election')
        self.assertEqual(self.subject.action_type, Marker.ACTION_TYPE.remote)
        self.assertEqual(self.subject.action_user_class, ['customer'])

    def test_action_attribs(self):
        self.assertEqual(self.subject.action_attribs, {'method': 'PATCH',
                                                       'status': 4,
                                                       'tool': '83b-election-letters',
                                                       'tool_object_id': 1})

    def test_get_action_url(self):
        url = reverse('api:eightythreeb-detail', kwargs={'pk': self.subject.tool.pk})
        self.assertEqual(self.subject.get_action_url(), url)

    def test_action(self):
        prop_mock = mock.PropertyMock()

        # mock the subjects status so that its greater than the current markers val
        self.subject.tool.status = self.subject.tool.STATUS_83b.irs_recieved
        # on complete we dont have an action
        self.assertEqual(self.subject.action, None)

        # mock out the is_complete property so we can test its post complete action name
        with mock.patch.object(self.clazz, 'is_complete', prop_mock):
            self.subject = self.clazz(self.val)
            prop_mock.return_value = True
            self.subject.tool = self.eightythreeb
            # test we have this when is_complete = True
            self.assertEqual(self.subject.action, None)


class CustomerUploadScanMarkerTest(BaseTestMarker):
    val = 5
    clazz = CustomerUploadScanMarker

    def test_properties(self):
        self.assertTrue(type(self.subject), self.clazz)
        self.assertEqual(self.subject.name, 'copy_uploaded')
        self.assertEqual(self.subject.description, 'Client: Scan and upload signed copy')
        self.assertEqual(self.subject.long_description, None)
        self.assertEqual(self.subject.signals, ['toolkit.apps.eightythreeb.signals.copy_uploaded'])
        self.assertEqual(self.subject.action_name, 'Upload Attachment')
        self.assertEqual(self.subject.action_type, Marker.ACTION_TYPE.modal)
        self.assertEqual(self.subject.action_user_class, ['customer'])

    def test_action_attribs(self):
        self.assertEqual(self.subject.action_attribs, {'target': '#modal-copy_uploaded'})

    def test_get_action_url(self):
        url = reverse('eightythreeb:attachment', kwargs={'slug': self.subject.tool.slug})
        self.assertEqual(self.subject.get_action_url(), url)


class CustomerTrackingNumberMarkerTest(BaseTestMarker):
    val = 6
    clazz = CustomerTrackingNumberMarker

    def test_properties(self):
        self.assertTrue(type(self.subject), self.clazz)
        self.assertEqual(self.subject.name, 'mail_to_irs_tracking_code')
        self.assertEqual(self.subject.description, 'Client: Mail to IRS & register Tracking Code')
        self.assertEqual(self.subject.long_description, 'Mail 83(b) form using USPS Registered Post *ONLY* and enter the Tracking Number here')
        self.assertEqual(self.subject.signals, ['toolkit.apps.eightythreeb.signals.mail_to_irs_tracking_code'])
        self.assertEqual(self.subject.action_name, 'Enter Tracking Number')
        self.assertEqual(self.subject.action_type, Marker.ACTION_TYPE.modal)
        self.assertEqual(self.subject.action_user_class, ['customer', 'lawyer'])

    def test_action_attribs(self):
        self.assertEqual(self.subject.action_attribs, {'target': '#modal-mail_to_irs_tracking_code'})

    def test_get_action_url(self):
        url = reverse('eightythreeb:tracking_code', kwargs={'slug': self.subject.tool.slug})
        self.assertEqual(self.subject.get_action_url(), url)

    def test_action(self):
        prop_mock = mock.PropertyMock()
        action_url = reverse('eightythreeb:tracking_code', kwargs={'slug': self.subject.tool.slug})

        # This marker shows only when it is the active value or the next "irs_recieved"
        self.subject.tool.status = self.subject.tool.STATUS_83b.mail_to_irs_tracking_code
        self.assertEqual(self.subject.action, action_url)
        # mock the subjects status so that its greater than the current markers val
        self.subject.tool.status = self.subject.tool.STATUS_83b.irs_recieved
        # on complete we dont have an action
        self.assertEqual(self.subject.action, action_url)

        # is NOT visible when any other marker is the status
        self.subject.tool.status = self.subject.tool.STATUS_83b.customer_print_and_sign
        self.assertEqual(self.subject.action, None)
        self.subject.tool.status = self.subject.tool.STATUS_83b.customer_complete_form
        self.assertEqual(self.subject.action, None)


class USPSDeliveryStatusMarkerTest(BaseTestMarker):
    val = 7
    clazz = USPSDeliveryStatusMarker

    def test_properties(self):
        self.assertTrue(type(self.subject), self.clazz)
        self.assertEqual(self.subject.name, 'irs_recieved')
        self.assertEqual(self.subject.description, 'Waiting for reciept of 83(b) by IRS (via USPS) for EJ958083578US')
        self.assertEqual(self.subject.long_description, 'Waiting for USPS response')
        self.assertEqual(self.subject.signals, ['toolkit.apps.eightythreeb.signals.irs_recieved'])
        self.assertEqual(self.subject.action_name, None)
        self.assertEqual(self.subject.action_type, None)
        self.assertEqual(self.subject.action_user_class, [])

    def test_get_action_url(self):
        with self.assertRaises(NotImplementedError) as context:
            self.subject.get_action_url()

    def test_action(self):
        with self.assertRaises(NotImplementedError) as context:
            self.subject.action


class ProcessCompleteMarkerTest(BaseTestMarker):
    val = 8
    clazz = ProcessCompleteMarker

    def test_properties(self):
        self.assertTrue(type(self.subject), self.clazz)
        self.assertEqual(self.subject.name, 'complete')
        self.assertEqual(self.subject.description, 'Process Complete')
        self.assertEqual(self.subject.long_description, None)
        self.assertEqual(self.subject.signals, ['toolkit.apps.eightythreeb.signals.complete'])
        self.assertEqual(self.subject.action_name, None)
        self.assertEqual(self.subject.action_type, None)
        self.assertEqual(self.subject.action_user_class, [])

    def test_get_action_url(self):
        with self.assertRaises(NotImplementedError) as context:
            self.subject.get_action_url()

    def test_action(self):
        with self.assertRaises(NotImplementedError) as context:
            self.subject.action
