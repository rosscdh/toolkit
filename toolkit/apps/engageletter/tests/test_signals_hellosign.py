# -*- coding: utf-8 -*-
from django.core.cache import cache
from django.test import TestCase, Client
from django.core.urlresolvers import reverse

from model_mommy import mommy

from toolkit.casper.workflow_case import BaseScenarios

from hello_sign.models import HelloSignRequest, HelloSignLog
from hello_sign.views import HelloSignWebhookEventHandler

from .data import ENGAGELETTER_DATA as BASE_ENGAGELETTER_DATA
from ..models import EngagementLetter

from hello_sign.tests.data import HELLOSIGN_200_RESPONSE, HELLOSIGN_WEBHOOK_EVENT_DATA
from hello_sign.tests.models import TestMonkeyModel

import json


class HelloSignWebhookEventsTest(BaseScenarios, TestCase):
    """
    Test the handleing of HelloSign webhook events

    as per: http://www.hellosign.com/api/gettingStarted "Handling callbacks"

    NOTE: Your endpoint will need to return a 200 HTTP code and a response body
    containing the following text: "Hello API Event Received". Otherwise,
    the callback will be considered a failure and will be retried later.
    """
    subject = HelloSignWebhookEventHandler
    client = Client

    def setUp(self):
        super(HelloSignWebhookEventsTest, self).setUp()
        self.basic_workspace()

        self.engageletter = mommy.make('engageletter.EngagementLetter',
                            slug='d1c545082d1241849be039e338e47aa0',
                            workspace=self.workspace,
                            user=self.user,
                            data=BASE_ENGAGELETTER_DATA.copy(),
                            status=EngagementLetter.STATUS.customer_sign_and_send)  # set the status to customer_sign_and_send

        self.engageletter_content_object = self.engageletter.get_content_type_object()

        self.signature_request_id = HELLOSIGN_WEBHOOK_EVENT_DATA['SIGNATURE_REQUEST_SENT']['signature_request'].get('signature_request_id')

        self.request = HelloSignRequest.objects.create(content_object_type=self.engageletter_content_object,
                                                       object_id=self.engageletter.pk,
                                                       signature_request_id=self.signature_request_id,
                                                       data=HELLOSIGN_200_RESPONSE)

    def get_webhook_event_post_data(self, name):
        """
        Return the aspect of the HS Event data Dict by name

        NB: HelloSign wraps the json data in another json object called "json"
        i.e. HelloSign sends a post object with key "json" that is set to an actual
        string of JSON
        """
        return { 'json': json.dumps(HELLOSIGN_WEBHOOK_EVENT_DATA[name]) }

    def get_hellosign_post_response(self, name):
        return self.client.post(reverse('hellosign_webhook_event'), self.get_webhook_event_post_data(name=name))

    def test_webhook_events_are_logged(self):
        """
        This .. is a big.. ugly test. but it works (hahah.. soudns like php)

        0. SIGNATURE_REQUEST_SENT - Sent to the registerd url when the intial request is setup
        1. SIGNATURE_REQUEST_SIGNED_CLIENT - Sent when the client has signed their doc
        2. SIGNATURE_REQUEST_SIGNED_LAWYER - Sent when the lawyer has signed their doc
        3. SIGNATURE_REQUEST_ALL_SIGNED - Sent when all parties have signed
        """
        #
        # hardcode the keys as Dict does not preseve order
        #
        for i, key in enumerate([u'SIGNATURE_REQUEST_SENT', u'SIGNATURE_REQUEST_SIGNED_CLIENT', u'SIGNATURE_REQUEST_SIGNED_LAWYER', u'SIGNATURE_REQUEST_ALL_SIGNED']):

            # post response
            resp = self.get_hellosign_post_response(name=key)

            hs_logs = self.request.hellosignlog_set.all()
            #
            # Test that each log is recorded and present
            #
            self.assertEqual(hs_logs.count(), (i + 1))

            #
            # Most recent event log
            # testing HelloSignLog.Meta: ordering = ['-id'] here
            #
            log = hs_logs[0]

            self.assertEqual(log.event_type, log.data['event'].get('event_type'))
            self.assertEqual(log.data, HELLOSIGN_WEBHOOK_EVENT_DATA[key])

            # update the object
            # must happen in order to get updated status
            self.engageletter = EngagementLetter.objects.get(pk=self.engageletter.pk)

            if log.event_type in ['signature_request_sent']:
                #
                # no events take place in our system here
                # and not signers should have been present
                #
                self.assertEqual(log.signer_status, (None, None))
                # test the status has NOT changed and were still waiting for a sig
                self.assertEqual(self.engageletter.status, EngagementLetter.STATUS.customer_sign_and_send)

            elif log.event_type in ['signature_request_signed']:
                #
                # test that the workspace data is updated
                # and that the status of the object changes
                # and that and emails are set
                #
                user, status = log.signer_status

                if user.profile.user_class == 'customer':
                    self.assertEqual(user, self.user)
                    self.assertEqual(status, 'signed')

                    # test the sigs are updated
                    self.assertEqual(self.engageletter.signatures, log.signatures)
                    self.assertEqual(self.engageletter.signatures[1].get('status_code'), 'signed')
                    self.assertEqual(self.engageletter.signatures[1].get('signed_at'), 1392037300)

                    # test the status has changed
                    self.assertEqual(self.engageletter.status, EngagementLetter.STATUS.lawyer_sign)

                elif user.profile.user_class == 'lawyer':
                    self.assertEqual(user, self.lawyer)
                    self.assertEqual(status, 'signed')

                    # test the sigs are updated
                    self.assertEqual(self.engageletter.signatures, log.signatures)
                    self.assertEqual(self.engageletter.signatures[0].get('status_code'), 'signed')
                    self.assertEqual(self.engageletter.signatures[0].get('signed_at'), 1392037626)

                    # test the status has changed
                    self.assertEqual(self.engageletter.status, EngagementLetter.STATUS.complete)


            elif log.event_type in ['signature_request_all_signed']:
                #
                # no events take place in our system here
                # but log.signer_staus will return the last user that signed
                #
                self.assertEqual(log.signer_status, (self.lawyer, u'signed'))
                # test the status has and the process is now complete
                self.assertEqual(self.engageletter.status, EngagementLetter.STATUS.complete)

        #
        # All expeced events are present and in right order
        #
        recorded_event_types = [l.event_type for l in hs_logs] # this should default to order_by('-id') which is a @BUSINESS_RULE
        self.assertEqual(recorded_event_types, [u'signature_request_all_signed', u'signature_request_signed', u'signature_request_signed', u'signature_request_sent'])
