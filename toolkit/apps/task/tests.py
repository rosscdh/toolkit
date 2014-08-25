# -*- coding: UTF-8 -*-
from django.core import mail
from django.test import TestCase
from django.utils import timezone
from django.contrib.humanize.templatetags.humanize import date, naturaltime

from toolkit import settings
from toolkit.casper.workflow_case import BaseScenarios

from model_mommy import mommy

import datetime


class TaskReminderServiceTest(BaseScenarios, TestCase):
    def setUp(self):
        super(TaskReminderServiceTest, self).setUp()
        self.basic_workspace()
        item = mommy.make('item.Item',
                          matter=self.matter,
                          date_due=timezone.now() + datetime.timedelta(days=settings.REMIND_DUE_DATE_LIMIT - 1))
        self.task = mommy.make('task.Task',
                                item=item,
                                is_complete=False,
                                created_by=self.lawyer,
                                assigned_to=[self.user],
                                date_due=timezone.now() + datetime.timedelta(days=settings.REMIND_DUE_DATE_LIMIT + 1))

    def test_reminder_positive(self):
        # create item in reminding period

        self.task.send_reminder(from_user=self.lawyer)
        outbox = mail.outbox
        self.assertEqual(len(outbox), 1)
        email = outbox[0]
        self.assertEqual(email.subject, u'[ACTION REQUIRED] Please complete the task')
        self.assertTrue('<h3>Warning, Task Overdue</h3>' not in email.body)

    def test_reminder_overdue(self):
        self.task.date_due = timezone.now() + datetime.timedelta(days=-5)
        self.task.save(update_fields=['date_due'])

        self.task.send_reminder(from_user=self.lawyer)
        outbox = mail.outbox
        self.assertEqual(len(outbox), 1)
        email = outbox[0]
        self.assertEqual(email.subject, u'[ACTION REQUIRED] (Expired) Please complete the task')
        self.assertTrue('<h3>Warning, Task Overdue</h3>' in email.body)