# -*- coding: utf-8 -*-
from toolkit.celery import app

from .services import PusherPublisherService


@app.task
def youve_got_notifications(username, event, *args, **kwargs):
    pusher = PusherPublisherService(channel=username,
                                    event=event)
    pusher.process(**kwargs)