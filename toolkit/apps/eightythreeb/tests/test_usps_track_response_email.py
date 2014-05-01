# -*- coding: utf-8 -*-
from django.core import mail
from django.core.management import call_command

import httpretty

from toolkit.apps.eightythreeb.models import EightyThreeB
from toolkit.casper.workflow_case import BaseProjectCaseMixin
from toolkit.apps.eightythreeb.tests.test_usps import TRACKING_CODE
from toolkit.apps.eightythreeb.management.commands.eightythreeb_usps_track_response import Command as EightyThreeBIsCompleteEmailCommand


from toolkit.apps.eightythreeb.tests.usps_trackfield_response import TRACK_RESPONSE_XML_BODY


class BaseCustomer(BaseProjectCaseMixin):
    def setUp(self):
        super(BaseCustomer, self).setUp()
        self.basic_workspace()


class EightyThreeBIsCompleteEmailTest(BaseCustomer):
    """
    As a customer
    I want to recive and email when my 83b is delivered and complete
    """
    def setUp(self):
        super(EightyThreeBIsCompleteEmailTest, self).setUp()

        self.eightythreeb.status = EightyThreeB.STATUS.irs_recieved
        self.eightythreeb.tracking_code = TRACKING_CODE
        self.eightythreeb.save()

    @httpretty.activate
    def test_valid_83b_email(self):
        httpretty.register_uri(httpretty.POST, "http://production.shippingapis.com/ShippingAPI.dll",
                               body=TRACK_RESPONSE_XML_BODY,
                               status=200)

        command = EightyThreeBIsCompleteEmailCommand()
        self.assertEqual(len(command.eightythreeb_list), 1)

        # call it conventionally
        call_command('eightythreeb_usps_track_response')

        # lets inspect the email
        self.assertEqual(len(mail.outbox), 1)
        email = mail.outbox[0]

        self.assertEqual(email.from_email, u'Lawyër Tëst (via LawPal) support@lawpal.com')
        self.assertEqual(email.extra_headers, {'Reply-To': self.lawyer.email})
        self.assertEqual(email.subject, '83(b) Filing Completed for %s' % self.user.get_full_name())
        self.assertEqual(email.recipients(), [self.user.email])
