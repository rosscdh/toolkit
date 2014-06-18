# -*- coding: UTF-8 -*-
from django.conf import settings

import pusher
import json

import logging
logger = logging.getLogger('django.request')

PUSHER_APP_ID = getattr(settings, 'PUSHER_APP_ID', None)
PUSHER_KEY = getattr(settings, 'PUSHER_KEY', None)
PUSHER_SECRET = getattr(settings, 'PUSHER_SECRET', None)

if PUSHER_APP_ID is None:
    raise Exception("You must specify a PUSHER_APP_ID in your local_settings.py")
if PUSHER_KEY is None:
    raise Exception("You must specify a PUSHER_KEY in your local_settings.py")
if PUSHER_SECRET is None:
    raise Exception("You must specify a PUSHER_SECRET in your local_settings.py")


class PusherPublisherService(object):
    """ Service to push data out to channels on pusher.com
    so the js lib can pick them up """
    channels = None
    event = None
    data = {}

    def __init__(self, channel, event, **kwargs):
        # is we pass in a tuple or list (iterable)
        # otherwise make it a list
        self.channels =  channel if hasattr(channel, '__iter__') else [channel]
        self.event = event

        # append our core data
        self.data.update(kwargs)

        logger.debug('Initialized PusherPublisherService with {data}'.format(data=json.dumps(self.data)))

        if not settings.IS_TESTING:
            self.pusher = pusher.Pusher(app_id=PUSHER_APP_ID, key=PUSHER_KEY, secret=PUSHER_SECRET)

    def process(self, **kwargs):
        if not settings.IS_TESTING:

            if 'event' not in kwargs:
                kwargs.update({'event': self.event})

            self.data.update(kwargs)

            for channel in self.channels:
                logger.debug('Sending pusher event on #{channel}'.format(channel=channel))

                self.data.update({
                    'channel': channel,
                })

                self.pusher[channel].trigger(self.event, self.data)


class RealTimeMatterEvent(object):
    """
    When an item is updated (via api) we issue an event to pusher

    ```
    {"event": "update|create|delete", "model": "matter|item|revision", "id": ":slug|:uuid|:uuid", "from_id": ":username"}

    NB id from_id is null then it should update for all
    ```
    """
    service = PusherPublisherService
    event_names = ('create', 'update', 'delete',)

    def __init__(self, matter):
        self.channel = matter.slug

    def process(self, event, obj, ident, from_ident=None, **kwargs):
        assert event in self.event_names, 'event must be in %s' % self.event_names

        model = obj.__class__.__name__.lower()

        kwargs.update({
            'is_global': False
        })

        # if we have no from_ident it means its a global level event like all user signed
        if from_ident is None:
            kwargs.update({
                'is_global': True
            })

        service = self.service(channel=self.channel,
                               event=event,
                               model=model,
                               id=str(ident),
                               from_id=from_ident,
                               **kwargs)
        service.process()
