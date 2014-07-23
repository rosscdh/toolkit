# -*- coding: utf-8 -*-
from django.conf import settings
from django.utils import timezone

from toolkit.apps.task.models import Task

from toolkit.core.services.lawpal_abridge import LawPalAbridgeService

from .reminder import BaseReminderService

import logging
import datetime
logger = logging.getLogger('django.request')


class TaskReminderService(BaseReminderService):
    """
    Service to collect tasks whose users need to be reminded because of upcoming due date
    """
    def collect_object_list(self):
        today_date = timezone.now()
        timedelta = datetime.timedelta(days=settings.REMIND_DUE_DATE_LIMIT)
        minus_timedelta = datetime.timedelta(days=-settings.REMIND_DUE_DATE_LIMIT)

        from_date = today_date + minus_timedelta
        to_date = today_date + timedelta

        logger.info('TaskReminders for from: %s to: %s' % (from_date, to_date))

        return Task.objects.filter(
            is_complete=False,
            date_due__gte=from_date,
            date_due__lte=to_date)

    def process(self):
        for task in self.collect_object_list().iterator():
            # Customised send email here
            task.send_reminder(from_user=task.created_by)

            for participant in task.assigned_to.all():
                item = task.item
                matter = item.matter
                msg = 'Sending reminder to %s for matter: %s item: %s task: %s' % (participant, matter, item, task)
                print msg
                logger.info(msg)
                self.send_message_to_abridge(participant, task)
