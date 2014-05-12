# -*- coding: utf-8 -*-
from django.conf import settings
from toolkit.celery import app

from .services import PusherPublisherService

import logging
logger = logging.getLogger('django.request')


@app.task
def youve_got_notifications(username, event, *args, **kwargs):
    if settings.PROJECT_ENVIRONMENT not in ['test']:
        logger.info('Sending youve_got_notifications: %s' % username)
        pusher = PusherPublisherService(channel=username,
                                        event=event)
        pusher.process(**kwargs)