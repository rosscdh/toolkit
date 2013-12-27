# -*- coding: utf-8 -*-
from django.test import TestCase
from django.db.models.query import QuerySet

import datetime

from model_mommy import mommy
from usps.api import USPS_CONNECTION
from usps.api.tracking import TrackConfirmWithFields
from toolkit.casper import httprettify_methods, mock_http_requests
from toolkit.apps.workspace.services import USPSTrackingService, USPSResponse


from .data import EIGHTYTHREEB_DATA

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
                            data=EIGHTYTHREEB_DATA,
                            filing_date=datetime.date.today() + datetime.timedelta(days=30),
                            transfer_date=datetime.date.today(),
                            status=EightyThreeB.STATUS_83b.irs_recieved)


class USPSTrackingCodeCliCommandTest(BaseUSPSTrackingCode):
    """
    test our response to the USPS tracking code XML process
    83b_usps_track_response.py cli command
    """
    def test_instance_tracking_code(self):
        self.assertEqual(self.eightythreeb.tracking_code, TRACKING_CODE)

    def test_usps_service_type(self):
        self.assertEqual(type(self.subject.service), USPSTrackingService)

    def test_usps_83b_list_contains_correct_items(self):
        """
        Test the subject contains the correct items in its action list
        """
        self.assertEqual(type(self.subject.eightythreeb_list), QuerySet)
        self.assertEqual(len(self.subject.eightythreeb_list), 1)
        self.assertTrue(self.eightythreeb in self.subject.eightythreeb_list)

    @mock_http_requests
    def test_result_is_recorded(self):
        self.subject.handle()  # execute the command
        self.eightythreeb = self.eightythreeb._meta.model.objects.get(pk=self.eightythreeb.pk)  # reload the model

        self.assertTrue('usps' in self.eightythreeb.data)
        self.assertTrue('usps_log' in self.eightythreeb.data)

        self.assertEqual(1, len(self.eightythreeb.data['usps_log']))
        self.assertEqual(3, len(self.eightythreeb.usps_waypoints))

        #
        # index 0 is manually inserted; as the crap design os usps api does not make the latest item list
        # in the waypoints
        #
        self.assertEqual(type(self.eightythreeb.usps_waypoints[0]), dict)
        self.assertEqual(self.eightythreeb.usps_waypoints[0]['EventCity'], u'NEWTON')
        self.assertEqual(self.eightythreeb.usps_waypoints[0]['EventDate'], u'May 21, 2001')
        self.assertEqual(self.eightythreeb.usps_waypoints[0]['EventTime'], u'12:12 pm')

        self.assertEqual(type(self.eightythreeb.usps_waypoints[1]), dict)
        self.assertEqual(self.eightythreeb.usps_waypoints[1]['EventCity'], u'DES MOINES')
        self.assertEqual(self.eightythreeb.usps_waypoints[1]['EventDate'], u'March 28, 2001')
        self.assertEqual(self.eightythreeb.usps_waypoints[1]['EventTime'], u'9:24 pm')

        self.assertEqual(type(self.eightythreeb.usps_waypoints[2]), dict)
        self.assertEqual(self.eightythreeb.usps_waypoints[2]['EventCity'], u'BLAINE')
        self.assertEqual(self.eightythreeb.usps_waypoints[2]['EventDate'], u'March 27, 2001')
        self.assertEqual(self.eightythreeb.usps_waypoints[2]['EventTime'], u'10:00 pm')


@httprettify_methods()
class USPSTrackingCodeResponseTest(BaseUSPSTrackingCode):
    """
    Test the expected USPS XML response
    """
    def setUp(self):
        super(USPSTrackingCodeResponseTest, self).setUp()
        self.subject = USPSTrackingService()
        self.response = self.subject.track(tracking_code=TRACKING_CODE)

    def test_we_have_correct_service_as_subject(self):
        self.assertEqual(type(self.subject), USPSTrackingService)

    def test_service_properties(self):
        """
        Ensure properties are set
        """
        self.assertTrue(hasattr(self.subject, 'USERID'))
        self.assertTrue(hasattr(self.subject, 'PASSWORD'))
        self.assertTrue(self.subject.USERID not in [None, ''])
        self.assertTrue(self.subject.PASSWORD not in [None, ''])

        self.assertTrue(hasattr(self.subject, 'USPS_CONNECTION'))
        self.assertEqual(self.subject.USPS_CONNECTION, USPS_CONNECTION)  # is a live connection

    def test_service_uses_correct_usps_xml_class(self):
        """
        Ensure were using the USPS TrackFields service
        """
        self.assertEqual(type(self.subject.service), TrackConfirmWithFields)

    def test_track_usps_response(self):
        self.assertEqual(type(self.response), USPSResponse)

    def test_usps_response_properties(self):
        self.assertEqual(type(self.response.as_json), str)
        self.assertEqual(type(self.response.summary), dict)
        self.assertEqual(type(self.response.status), str)
        self.assertEqual(type(self.response.description), str)
        self.assertEqual(type(self.response.waypoints), list)

    def test_usps_response_summary(self):
        self.assertEqual(self.response.summary, {'EventTime': '12:12 pm', 'AuthorizedAgent': None, 'FirmName': None, 'EventCountry': None, 'EventZIPCode': '50208', 'Event': 'DELIVERED', 'EventCity': 'NEWTON', 'EventState': 'IA', 'EventDate': 'May 21, 2001', 'Name': None})

    def test_usps_response_status(self):
        self.assertEqual(self.response.status, 'DELIVERED')

    def test_usps_response_description(self):
        self.assertEqual(self.response.description, 'The package is currently DELIVERED in NEWTON IA 50208, USA. The event took place on May 21, 2001:12:12 pm')

    def test_usps_response_waypoints(self):
        self.assertEqual(self.response.waypoints, [ {'EventTime': '12:12 pm',
                                                     'AuthorizedAgent': None,
                                                     'FirmName': None,
                                                     'EventCountry': None,
                                                     'EventZIPCode': '50208',
                                                     'Event': 'DELIVERED',
                                                     'EventCity': 'NEWTON',
                                                     'EventState': 'IA',
                                                     'EventDate': 'May 21, 2001',
                                                     'Name': None},
                                                    {'AuthorizedAgent': None,
                                                      'Event': 'ENROUTE',
                                                      'EventCity': 'DES MOINES',
                                                      'EventCountry': None,
                                                      'EventDate': 'March 28, 2001',
                                                      'EventState': 'IA',
                                                      'EventTime': '9:24 pm',
                                                      'EventZIPCode': '50395',
                                                      'FirmName': None,
                                                      'Name': None},
                                                    {'AuthorizedAgent': None,
                                                      'Event': 'ACCEPTANCE',
                                                      'EventCity': 'BLAINE',
                                                      'EventCountry': None,
                                                      'EventDate': 'March 27, 2001',
                                                      'EventState': 'WA',
                                                      'EventTime': '10:00 pm',
                                                      'EventZIPCode': '98231',
                                                      'FirmName': None,
                                                      'Name': None}])
