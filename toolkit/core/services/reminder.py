# -*- coding: utf-8 -*-
import datetime
import logging
from django.conf import settings
from django.utils import timezone
from toolkit.core.item.models import Item
from toolkit.core.services.lawpal_abridge import LawPalAbridgeService


logger = logging.getLogger('django.request')


class ReminderService(object):
    """
    Service to collect items whose users need to be reminded because of upcoming due date
    """

    def __init__(self, reminding_limit=settings.REMIND_DUE_DATE_LIMIT):
        self.reminding_limit = reminding_limit

        self.abridge_services = {}

    def collect_items(self):
        return Item.objects.filter(
            is_complete=False,
            date_due__gt=timezone.now()-datetime.timedelta(days=settings.REMIND_DUE_DATE_LIMIT))

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
            abridge_service = self.get_abridge_service(user)
        except Exception as e:
            # AbridgeService is not running.
            logger.critical('Abridge Service is not running because: %s' % e)
        return abridge_service

    def send_message_to_abridge(self, user, item):
        message_data = {
            'item': item
        }
        message = LawPalAbridgeService.render_reminder_template(**message_data)
        abridge_service = self.get_abridge_service(user)
        abridge_service.create_event(content_group='Important', content=message)

    def process(self):
        items_to_remind = self.collect_items()

        for item in items_to_remind:
            # item.participants() seems to be ALWAYS empty. is there a possibility to set it (yet)?
            for participant in item.matter.participants.all():
                self.send_message_to_abridge(participant, item)