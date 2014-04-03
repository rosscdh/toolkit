# -*- coding: utf-8 -*-
from toolkit.celery import app

from .services import PusherPublisherService


@app.task
def youve_got_notifications(user_username, event, *args, **kwargs):
    pusher = PusherPublisherService(channel=user_username,
                                    event=event)
    pusher.process(**kwargs)