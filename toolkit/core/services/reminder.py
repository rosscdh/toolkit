# -*- coding: utf-8 -*-
from django.conf import settings
from django.utils import timezone
from toolkit.core.item.models import Item
from toolkit.core.services.lawpal_abridge import LawPalAbridgeService

import logging
import datetime
logger = logging.getLogger('django.request')


class BaseReminderService(object):
    """
    Service to collect items whose users need to be reminded because of upcoming due date
    """

    def __init__(self, reminding_limit=settings.REMIND_DUE_DATE_LIMIT):
        self.reminding_limit = reminding_limit
        self.abridge_services = {}

    def collect_object_list(self):
        raise NotImplemented('You msut override this method to return the object that are of interest to you')

    def get_abridge_service(self, user):
        ## TODO: check if dictionary can grow big enough for all user-pks
        try:
            abridge_service = self.abridge_services.get(user.pk)
            if abridge_service is None:
                abridge_service = LawPalAbridgeService(user=user,
                                                       ABRIDGE_ENABLED=getattr(settings, 'ABRIDGE_ENABLED', False))
                self.abridge_services[user.pk] = abridge_service

        except MemoryError:
            self.abridge_services = {}
            logger.critical('Reminder Service: dictionary grew to large. resetting and going on for now, but this should be changed.')
            return self.get_abridge_service(user)

        except Exception as e:
            # AbridgeService is not running.
            logger.critical('Abridge Service Error: %s' % e)

        return abridge_service

    def send_message_to_abridge(self, user, item):
        message_data = {
            'item': item
        }
        message = LawPalAbridgeService.render_reminder_template(**message_data)
        abridge_service = self.get_abridge_service(user)
        if not abridge_service:
            logger.critical('Could not instantiate Abridge Service')
        else:
            abridge_service.create_event(content_group='Important', content=message)

    def process(self):
        raise NotImplemented('You msut override this method to process the objects')


class ReminderService(BaseReminderService):
    def collect_object_list(self):
        today_date = timezone.now()
        timedelta = datetime.timedelta(days=settings.REMIND_DUE_DATE_LIMIT)
        minus_timedelta = datetime.timedelta(days=-settings.REMIND_DUE_DATE_LIMIT)

        from_date = today_date + minus_timedelta
        to_date = today_date + timedelta

        logger.info('TaskReminders for from: %s to: %s' % (from_date, to_date))

        return Item.objects.filter(
            is_complete=False,
            date_due__gte=from_date,
            date_due__lte=to_date)

    def process(self):
        for item in self.collect_object_list().iterator():
            for participant in item.matter.participants.all():
                msg = 'Sending reminder to %s for matter item: %s:%s' % (participant, item.matter, item)
                print(msg)
                logger.info(msg)
                self.send_message_to_abridge(participant, item)