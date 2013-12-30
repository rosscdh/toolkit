# -*- coding: utf-8 -*-
from django.core import mail
from django.test import TestCase
from django.core.files import File
from django.core.files.storage import FileSystemStorage

import os
import mock
import datetime

from model_mommy import mommy

from toolkit.apps.workspace.models import Tool
from toolkit.apps.eightythreeb.models import EightyThreeB
from toolkit.apps.eightythreeb.management.commands.eightythreeb_usps_track_response import Command as USPSEightyThreeBTracking

from .data import EIGHTYTHREEB_TRACKINGCODE_DATA

FILE_BASE_PATH = os.path.dirname(__file__)

from .test_usps import TRACKING_CODE


class BaseUSPSTrackingCode(TestCase):
    """
    Setup the base data case for USPS test
    """
    fixtures = ['sites', 'tools']

    @mock.patch('storages.backends.s3boto.S3BotoStorage', FileSystemStorage)
    def setUp(self):
        super(BaseUSPSTrackingCode, self).setUp()

        self.subject = USPSEightyThreeBTracking()

        self.user = mommy.make('auth.User', first_name='Customer', last_name='Test', email='test+customer@lawpal.com')
        self.lawyer = mommy.make('auth.User', first_name='Lawyer', last_name='Test', email='test+lawyer@lawpal.com')

        self.workspace = mommy.make('workspace.Workspace', name='Lawpal (test)')
        self.workspace.tools.add(Tool.objects.get(slug='83b-election-letters'))
        self.workspace.participants.add(self.user)
        self.workspace.participants.add(self.lawyer)

        self.eightythreeb = mommy.make('eightythreeb.EightyThreeB',
                                       slug='e0c545082d1241849be039e338e47a0f',
                                       workspace=self.workspace,
                                       user=self.user,
                                       data=EIGHTYTHREEB_TRACKINGCODE_DATA,
                                       filing_date=datetime.date.today() + datetime.timedelta(days=30),
                                       transfer_date=datetime.date.today(),
                                       status=EightyThreeB.STATUS_83b.mail_to_irs_tracking_code)

        self.eightythreeb.attachment_set.create(attachment=File(open('%s/attachment-1.gif' % FILE_BASE_PATH, 'r')))
        self.eightythreeb.attachment_set.create(attachment=File(open('%s/attachment-2.jpg' % FILE_BASE_PATH, 'r')))
        self.eightythreeb.attachment_set.create(attachment=File(open('%s/attachment-3.pdf' % FILE_BASE_PATH, 'r')))


class TestTrackingCodeEntered(BaseUSPSTrackingCode):

    def setUp(self):
        super(TestTrackingCodeEntered, self).setUp()
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

        self.assertEqual(email.subject, u'83b Tracking Code entered for Customer Test')
        self.assertEqual(len(email.attachments), num_attachments)  # test we have the attachments
        self.assertEqual(len(email.to), 1)
        self.assertEqual(email.to, ['test+customer@lawpal.com'])
        self.assertEqual(email.from_email, 'tech@lawpal.com')

        email = mail.outbox[1]
        self.assertEqual(email.subject, u'83b Tracking Code entered for Customer Test')
        self.assertEqual(len(email.attachments), num_attachments)  # test we have the attachments
        self.assertEqual(len(email.to), 1)
        self.assertEqual(email.to, ['test+lawyer@lawpal.com'])
        self.assertEqual(email.from_email, 'tech@lawpal.com')
