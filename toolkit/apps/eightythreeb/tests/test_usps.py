# -*- coding: utf-8 -*-
from django.core import mail
from django.test import TestCase

import datetime
import httpretty

from model_mommy import mommy
from usps.api import USPS_CONNECTION
from usps.api.tracking import TrackConfirmWithFields
from toolkit.apps.matter.services.matter_permission import MightyMatterUserPermissionService
from toolkit.casper.prettify import httprettify_methods, mock_http_requests  # must import directly
from toolkit.apps.workspace.services import USPSTrackingService, USPSResponse

from .data import EIGHTYTHREEB_DATA
from .usps_trackfield_response import TRACK_UNDELIVERED_RESPONSE_XML_BODY

from toolkit.core.mixins.query import IsDeletedQuerySet

from toolkit.apps.workspace.models import Tool, ROLES
from toolkit.apps.eightythreeb.models import EightyThreeB
from toolkit.apps.eightythreeb.management.commands.eightythreeb_usps_track_response import Command as USPSEightyThreeBTracking

TRACKING_CODE_USS39 = 'EJ958083578US'
TRACKING_CODE_USS128 = '70132630000013657033'
TRACKING_CODE = TRACKING_CODE_USS128


class BaseUSPSTrackingCode(TestCase):
    """
    Setup the base data case for USPS test
    """
    fixtures = ['sites', 'tools']

    def setUp(self):
        super(BaseUSPSTrackingCode, self).setUp()

        self.subject = USPSEightyThreeBTracking()

        self.user = mommy.make('auth.User', first_name='Customër', last_name='Tëst', email='test+customer@lawpal.com')
        self.lawyer = mommy.make('auth.User', first_name='Lawyër', last_name='Tëst', email='test+lawyer@lawpal.com')
        lawyer_profile = self.lawyer.profile
        lawyer_profile.data['user_class'] = 'lawyer'
        lawyer_profile.save(update_fields=['data'])

        self.workspace = mommy.make('workspace.Workspace', name='Lawpal (test)', lawyer=self.lawyer)
        self.workspace.tools.add(Tool.objects.get(slug='83b-election-letters'))

        MightyMatterUserPermissionService(matter=self.workspace,
                                          role=ROLES.customer,
                                          user=self.user,
                                          changing_user=self.lawyer).process()
        MightyMatterUserPermissionService(matter=self.workspace,
                                          role=ROLES.lawyer,
                                          user=self.lawyer,
                                          changing_user=self.lawyer).process()

        self.eightythreeb = mommy.make('eightythreeb.EightyThreeB',
                                       slug='e0c545082d1241849be039e338e47a0f',
                                       workspace=self.workspace,
                                       user=self.user,
                                       data=EIGHTYTHREEB_DATA,
                                       filing_date=datetime.date.today() + datetime.timedelta(days=30),
                                       transfer_date=datetime.date.today(),
                                       status=EightyThreeB.STATUS.irs_recieved)


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
        self.assertEqual(type(self.subject.eightythreeb_list), IsDeletedQuerySet)
        self.assertEqual(len(self.subject.eightythreeb_list), 1)
        self.assertTrue(self.eightythreeb in self.subject.eightythreeb_list)

    @mock_http_requests
    def test_result_is_recorded(self):
        self.subject.handle()  # execute the command
        self.eightythreeb = self.eightythreeb._meta.model.objects.get(pk=self.eightythreeb.pk)  # reload the model

        self.assertEqual(self.eightythreeb.status, EightyThreeB.STATUS.complete)

        self.assertTrue('usps' in self.eightythreeb.data)
        self.assertTrue('usps_log' in self.eightythreeb.data)

        self.assertEqual(1, len(self.eightythreeb.data['usps_log']))
        self.assertEqual(3, len(self.eightythreeb.usps_waypoints))

        #
        # index 0 is manually inserted; as the crap design os usps api does not make the latest item list
        # in the waypoints
        #
        self.assertEqual(len(self.eightythreeb.usps_waypoints), 3)

        self.assertEqual(type(self.eightythreeb.usps_waypoints[0]), dict)
        self.assertEqual(self.eightythreeb.usps_waypoints[0]['Event'], u'DELIVERED')
        self.assertEqual(self.eightythreeb.usps_waypoints[0]['EventCity'], u'NEWTON')
        self.assertEqual(self.eightythreeb.usps_waypoints[0]['EventDate'], u'May 21, 2001')
        self.assertEqual(self.eightythreeb.usps_waypoints[0]['EventTime'], u'12:12 pm')

        self.assertEqual(type(self.eightythreeb.usps_waypoints[1]), dict)
        self.assertEqual(self.eightythreeb.usps_waypoints[1]['Event'], u'ENROUTE')
        self.assertEqual(self.eightythreeb.usps_waypoints[1]['EventCity'], u'DES MOINES')
        self.assertEqual(self.eightythreeb.usps_waypoints[1]['EventDate'], u'March 28, 2001')
        self.assertEqual(self.eightythreeb.usps_waypoints[1]['EventTime'], u'9:24 pm')

        self.assertEqual(type(self.eightythreeb.usps_waypoints[2]), dict)
        self.assertEqual(self.eightythreeb.usps_waypoints[2]['Event'], u'ACCEPTANCE')
        self.assertEqual(self.eightythreeb.usps_waypoints[2]['EventCity'], u'BLAINE')
        self.assertEqual(self.eightythreeb.usps_waypoints[2]['EventDate'], u'March 27, 2001')
        self.assertEqual(self.eightythreeb.usps_waypoints[2]['EventTime'], u'10:00 pm')

        #
        # Test the email is sent
        #
        outbox = mail.outbox

        self.assertEqual(len(outbox), 1)
        email = outbox[0]

        self.assertEqual(email.subject, '83(b) Filing Completed for %s' % self.user.get_full_name())

        self.assertEqual(len(email.to), 1)
        self.assertEqual(email.to, ['test+customer@lawpal.com'])
        self.assertEqual(email.from_email, 'Lawyër Tëst (via LawPal) support@lawpal.com')
        self.assertEqual(email.extra_headers, {'Reply-To': self.lawyer.email})


class USPSUndeliveredTrackingCodeCliCommandTest(BaseUSPSTrackingCode):
    @httpretty.activate
    def test_undelivered(self):
        httpretty.register_uri(httpretty.POST, "http://production.shippingapis.com/ShippingAPI.dll",
                               body=TRACK_UNDELIVERED_RESPONSE_XML_BODY,
                               status=200)

        self.subject.handle()  # execute the command
        self.eightythreeb = self.eightythreeb._meta.model.objects.get(pk=self.eightythreeb.pk)  # reload the model

        # ensure that the status has not been updated
        self.assertEqual(self.eightythreeb.status, EightyThreeB.STATUS.irs_recieved)

        self.assertTrue('usps' in self.eightythreeb.data)
        self.assertTrue('usps_log' in self.eightythreeb.data)

        self.assertEqual(1, len(self.eightythreeb.data['usps_log']))
        self.assertEqual(2, len(self.eightythreeb.usps_waypoints))

        self.assertEqual(len(self.eightythreeb.usps_waypoints), 2)

        self.assertEqual(type(self.eightythreeb.usps_waypoints[0]), dict)
        self.assertEqual(self.eightythreeb.usps_waypoints[0]['Event'], u'ENROUTE')
        self.assertEqual(self.eightythreeb.usps_waypoints[0]['EventCity'], u'DES MOINES')
        self.assertEqual(self.eightythreeb.usps_waypoints[0]['EventDate'], u'March 28, 2001')
        self.assertEqual(self.eightythreeb.usps_waypoints[0]['EventTime'], u'9:24 pm')

        self.assertEqual(type(self.eightythreeb.usps_waypoints[1]), dict)
        self.assertEqual(self.eightythreeb.usps_waypoints[1]['Event'], u'ACCEPTANCE')
        self.assertEqual(self.eightythreeb.usps_waypoints[1]['EventCity'], u'BLAINE')
        self.assertEqual(self.eightythreeb.usps_waypoints[1]['EventDate'], u'March 27, 2001')
        self.assertEqual(self.eightythreeb.usps_waypoints[1]['EventTime'], u'10:00 pm')

        #
        # Test the email is sent
        #
        outbox = mail.outbox

        self.assertEqual(len(outbox), 0)


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
        self.assertEqual(type(self.response.is_delivered), bool)
        self.assertEqual(type(self.response.description()), str)
        self.assertEqual(type(self.response.waypoints), list)

    def test_usps_response_summary(self):
        self.assertEqual(self.response.summary, {'EventTime': '12:12 pm', 'AuthorizedAgent': None, 'FirmName': None, 'EventCountry': None, 'EventZIPCode': '50208', 'Event': 'DELIVERED', 'EventCity': 'NEWTON', 'EventState': 'IA', 'EventDate': 'May 21, 2001', 'Name': None})

    def test_usps_response_identity(self):
        self.assertEqual(self.response.identity, '12:12 pm-May 21, 2001-50208')

    def test_usps_response_status(self):
        self.assertEqual(self.response.status, 'DELIVERED')

    def test_usps_response_is_delivered(self):
        self.assertEqual(self.response.is_delivered, True)

    def test_usps_response_description(self):
        self.assertEqual(self.response.description(), 'Current package status : DELIVERED in NEWTON IA 50208, USA. Last Updated :  May 21, 2001:12:12 pm')

    def test_usps_response_waypoints(self):
        self.assertEqual(self.response.waypoints, [{'EventTime': '12:12 pm',
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

class USPSUndeliveredTrackingCodeResponseTest(BaseUSPSTrackingCode):
    """
    Test the expected USPS XML response, which is undelivered
    """
    @httpretty.activate
    def setUp(self):
        httpretty.register_uri(httpretty.POST, "http://production.shippingapis.com/ShippingAPI.dll",
                               body=TRACK_UNDELIVERED_RESPONSE_XML_BODY,
                               status=200)

        super(USPSUndeliveredTrackingCodeResponseTest, self).setUp()
        self.subject = USPSTrackingService()
        self.response = self.subject.track(tracking_code=TRACKING_CODE)

    def test_usps_response_identity(self):
        self.assertEqual(self.response.identity, '9:24 pm-March 28, 2001-50395')

    def test_usps_response_status(self):
        self.assertEqual(self.response.status, 'ENROUTE')

    def test_usps_response_is_delivered(self):
        self.assertEqual(self.response.is_delivered, False)
