# -*- coding: utf-8 -*-
from django.core import mail
from django.test import TestCase
from django.core.files import File
from django.core.files.storage import FileSystemStorage
from django.core.urlresolvers import reverse
from django.utils import simplejson as json

import os
import mock
import datetime
import httpretty

from model_mommy import mommy

from toolkit.apps.workspace.models import Tool, MatterUser
from toolkit.apps.eightythreeb.models import EightyThreeB
from toolkit.apps.eightythreeb.management.commands.eightythreeb_usps_track_response import Command as USPSEightyThreeBTracking

from toolkit.casper.prettify import httprettify_methods, mock_http_requests

from .data import EIGHTYTHREEB_TRACKINGCODE_DATA

from .usps_trackfield_response import TRACK_UNDELIVERED_RESPONSE_XML_BODY
from .test_usps import TRACKING_CODE

FILE_BASE_PATH = os.path.dirname(__file__)


class BaseUSPSTrackingCode(TestCase):
    """
    Setup the base data case for USPS test
    """
    fixtures = ['sites', 'tools']

    def setUp(self):
        super(BaseUSPSTrackingCode, self).setUp()

        self.subject = USPSEightyThreeBTracking()

        self.password = 'password'

        self.user = mommy.make('auth.User', first_name='Customër', last_name='Tëst', email='test+customer@lawpal.com')
        self.user.set_password(self.password)
        self.user.save()

        self.lawyer = mommy.make('auth.User', first_name='Lawyer', last_name='Test', email='test+lawyer@lawpal.com')
        self.lawyer.set_password(self.password)
        self.lawyer.save()

        self.workspace = mommy.make('workspace.Workspace', name='Lawpal (test)', lawyer=self.lawyer)
        self.workspace.tools.add(Tool.objects.get(slug='83b-election-letters'))
        MatterUser.objects.create(matter=self.workspace, user=self.user)
        MatterUser.objects.create(matter=self.workspace, user=self.lawyer)

        self.eightythreeb = mommy.make('eightythreeb.EightyThreeB',
                                       slug='e0c545082d1241849be039e338e47a0f',
                                       workspace=self.workspace,
                                       user=self.user,
                                       data=EIGHTYTHREEB_TRACKINGCODE_DATA,
                                       filing_date=datetime.date.today() + datetime.timedelta(days=30),
                                       transfer_date=datetime.date.today(),
                                       status=EightyThreeB.STATUS.mail_to_irs_tracking_code)

        self.eightythreeb.attachment_set.create(attachment=File(open('%s/attachment-1.gif' % FILE_BASE_PATH, 'r')))
        self.eightythreeb.attachment_set.create(attachment=File(open('%s/attachment-2.jpg' % FILE_BASE_PATH, 'r')))
        self.eightythreeb.attachment_set.create(attachment=File(open('%s/attachment-3.pdf' % FILE_BASE_PATH, 'r')))


class TestTrackingCodeModal(BaseUSPSTrackingCode):

    @httpretty.activate
    def test_form_validates_and_redirects(self):
        httpretty.register_uri(httpretty.POST, "http://production.shippingapis.com/ShippingAPI.dll",
                               body=TRACK_UNDELIVERED_RESPONSE_XML_BODY,
                               status=200)

        url = reverse('eightythreeb:tracking_code', kwargs={'slug': self.eightythreeb.slug})

        # User not logged in
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp['Location'], 'http://testserver/start/?next=/83b/%s/tracking_code/' % self.eightythreeb.slug)

        self.client.login(username=self.user.username, password=self.password)

        # Valid user
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)

        # Valid submission
        resp = self.client.post(url, {
            'tracking_code': TRACKING_CODE,
            'user': self.user
        }, follow=True)

        redirect = reverse('workspace:tool_object_overview', kwargs={
            'workspace': self.eightythreeb.workspace.slug,
            'tool': self.eightythreeb.tool_slug,
            'slug': self.eightythreeb.slug
        })

        actual_response = {
            'redirect': True,
            'url': redirect
        }

        self.assertEqual(resp.content, json.dumps(actual_response))

        # was it saved?
        self.assertEqual(self.eightythreeb.tracking_code, TRACKING_CODE)


class TestTrackingCodeEmail(BaseUSPSTrackingCode):

    def setUp(self):
        super(TestTrackingCodeEmail, self).setUp()
        self.eightythreeb.tracking_code = TRACKING_CODE
        self.eightythreeb.save(update_fields=['data'])

    def test_signal_sends_email(self):
        # ensure its not already present
        self.assertTrue('mail_to_irs_tracking_code' not in self.eightythreeb.data['markers'])
        self.assertEqual(len(mail.outbox), 0)

        # issue the signal
        self.eightythreeb.base_signal.send(sender=self, instance=self.eightythreeb, actor=self.eightythreeb.user, name='mail_to_irs_tracking_code')
        # reload the model data
        self.eightythreeb = self.eightythreeb._meta.model.objects.get(pk=self.eightythreeb.pk)

        # tests
        self.assertTrue('mail_to_irs_tracking_code' in self.eightythreeb.data['markers'])

        self.assertEqual(len(mail.outbox), 2)  # to customer AND lawyer @TODO and accountant too???

        num_attachments = self.eightythreeb.attachment_set.all().count()

        email = mail.outbox[0]

        self.assertEqual(email.subject, u'83b Tracking Code entered for Customër Tëst')
        self.assertEqual(len(email.attachments), num_attachments)  # test we have the attachments
        self.assertEqual(len(email.to), 1)
        self.assertEqual(email.to, ['test+customer@lawpal.com'])
        self.assertEqual(email.from_email, 'support@lawpal.com')
        self.assertEqual(email.extra_headers, {'Reply-To': 'support@lawpal.com'})

        email = mail.outbox[1]
        self.assertEqual(email.subject, u'83b Tracking Code entered for Customër Tëst')
        self.assertEqual(len(email.attachments), num_attachments)  # test we have the attachments
        self.assertEqual(len(email.to), 1)
        self.assertEqual(email.to, ['test+lawyer@lawpal.com'])
        self.assertEqual(email.from_email, 'support@lawpal.com')
        self.assertEqual(email.extra_headers, {'Reply-To': 'support@lawpal.com'})
