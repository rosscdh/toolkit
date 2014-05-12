# -*- coding: utf-8 -*-
from django.conf import settings
from toolkit.celery import app

from .services import PusherPublisherService


@app.task
def youve_got_notifications(username, event, *args, **kwargs):
    if settings.PROJECT_ENVIRONMENT not in ['test']:
        pusher = PusherPublisherService(channel=username,
                                        event=event)
        pusher.process(**kwargs)