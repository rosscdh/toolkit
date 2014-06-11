# -*- coding: UTF-8 -*-
from django.test import TestCase
from django.utils import timezone
from django.contrib.humanize.templatetags.humanize import date, naturaltime

from model_mommy import mommy
from toolkit import settings

from toolkit.casper.workflow_case import BaseScenarios

from ...services.reminder import ReminderService
from toolkit.core.services.lawpal_abridge import LawPalAbridgeService

import datetime


class ReminderServiceTest(BaseScenarios, TestCase):
    def setUp(self):
        super(ReminderServiceTest, self).setUp()
        self.basic_workspace()

    def test_reminder_positive(self):
        # create item in reminding period
        item = mommy.make('item.Item',
                          matter=self.matter,
                          date_due=timezone.now() + datetime.timedelta(days=settings.REMIND_DUE_DATE_LIMIT - 1))

        reminder_service = ReminderService()
        items_to_remind = reminder_service.collect_items()

        self.assertItemsEqual(items_to_remind, [item])

    def test_reminder_negative(self):
        # create item out of reminding period
        mommy.make('item.Item',
                          matter=self.matter,
                          date_due=timezone.now() + datetime.timedelta(days=settings.REMIND_DUE_DATE_LIMIT + 1))

        reminder_service = ReminderService()
        items_to_remind = reminder_service.collect_items()

        self.assertItemsEqual(items_to_remind, [])

    def test_reminder_template(self):
        # create item
        date_due = datetime.datetime.today() + datetime.timedelta(days=1)

        item = mommy.make('item.Item',
                          name='Test Item #1',
                          matter=self.matter,
                          date_due=date_due)

        message_data = {
            'item': item
        }
        message = LawPalAbridgeService.render_reminder_template(**message_data)

        self.assertEqual(message,
                         u'<p>Action required</p>\n<p style="color: red">Test Item #1 has not been closed, and its due date is approaching: %s (%s)</p>' % (date_due.strftime('%Y-%m-%d'), naturaltime(date_due)))