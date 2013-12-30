# -*- coding: utf-8 -*-
from django.core import mail
from django.test import TestCase
from django.db.models.query import QuerySet

import datetime
import httpretty

from model_mommy import mommy
from usps.api import USPS_CONNECTION
from usps.api.tracking import TrackConfirmWithFields
from toolkit.casper import httprettify_methods, mock_http_requests
from toolkit.apps.workspace.services import USPSTrackingService, USPSResponse

from .data import EIGHTYTHREEB_TRACKINGCODE_DATA
from .usps_trackfield_response import TRACK_UNDELIVERED_RESPONSE_XML_BODY

from toolkit.apps.workspace.models import Tool
from toolkit.apps.eightythreeb.models import EightyThreeB
from toolkit.apps.eightythreeb.management.commands.eightythreeb_usps_track_response import Command as USPSEightyThreeBTracking

TRACKING_CODE = 'EJ958083578US'


class BaseUSPSTrackingCode(TestCase):
    """
    Setup the base data case for USPS test
    """
    fixtures = ['sites', 'tools']

    def setUp(self):
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

        email = mail.outbox[0]
        self.assertEqual(email.subject, u'83b Tracking Code entered for Customer Test')
        self.assertEqual(len(email.to), 1)
        self.assertEqual(email.to, ['test+customer@lawpal.com'])
        self.assertEqual(email.from_email, 'tech@lawpal.com')

        email = mail.outbox[1]
        self.assertEqual(email.subject, u'83b Tracking Code entered for Customer Test')
        self.assertEqual(len(email.to), 1)
        self.assertEqual(email.to, ['test+lawyer@lawpal.com'])
        self.assertEqual(email.from_email, 'tech@lawpal.com')

        #mail_to_irs_tracking_code