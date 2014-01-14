# -*- coding: utf-8 -*-
from django.core import mail
from django.test import TestCase
from django.core.management import call_command

from toolkit.casper.workflow_case import BaseProjectCaseMixin
from toolkit.apps.eightythreeb.models import EightyThreeB
from toolkit.apps.eightythreeb.management.commands.eightythreeb_reminder import Command as EightyThreeBReminderCommand


class BaseCustomer(BaseProjectCaseMixin):
    def setUp(self):
        super(BaseCustomer, self).setUp()
        self.basic_workspace()


class EightyThreeBReminderEmailTest(BaseCustomer):
    """
    As a customer
    I want to recive and email every day to remind me to complete the 83(b) process
    Except for when the 83(b) is complete or pending delivery
    """
    INVALID_REMINDER_EMAIL_STATUS = EightyThreeB.INCOMPLETE_EXCLUDED_STATUS

    def test_valid_83b_email(self):
        VALID_STATUS_LIST = [(val, name, desc) for val, name, desc in EightyThreeB.STATUS_83b.get_all() if val not in self.INVALID_REMINDER_EMAIL_STATUS]

        for valid_status, name, desc in VALID_STATUS_LIST:
            self.eightythreeb.status = valid_status
            self.eightythreeb.save(update_fields=['status'])

            command = EightyThreeBReminderCommand()
            self.assertEqual(len(command.eightythreeb_list), 1)

            # call it conventionally
            call_command('eightythreeb_reminder')
            self.assertEqual(len(mail.outbox), 1)
            email = mail.outbox[0]

            self.assertEqual(email.subject, 'ACTION REQUIRED : 83(b) Filing Reminder Update')
            self.assertEqual(email.extra_headers, {'Reply-To': self.lawyer.email})
            mail.outbox.pop()  # remove the current one to allow for further tests

    def test_invalid_83b_email(self):
        """
        83bs in the excluded status should not get emails
        """
        INVALID_STATUS_LIST = [(val, name, desc) for val, name, desc in EightyThreeB.STATUS_83b.get_all() if val in self.INVALID_REMINDER_EMAIL_STATUS]

        for valid_status, name, desc in INVALID_STATUS_LIST:
            self.eightythreeb.status = valid_status
            self.eightythreeb.save(update_fields=['status'])

            command = EightyThreeBReminderCommand()
            self.assertEqual(len(command.eightythreeb_list), 0)

            # call it conventionally
            call_command('eightythreeb_reminder')
            self.assertEqual(len(mail.outbox), 0)