# -*- coding: utf-8 -*-
"""
Signals that listen for changes to the core models and then record them as
activity_stream objects
@TODO turn the signal handlers into its own module
"""
from django.conf import settings
from actstream import action
from django.dispatch import receiver
from django.dispatch.dispatcher import Signal

import logging
import requests

logger = logging.getLogger('django.request')

"""
Base Signal and listener used to funnel events
"""


# first four args as in django-activity-stream, plus custom stuff
send_activity_log = Signal(providing_args=['actor', 'verb', 'action_object', 'target', 'message', 'user', 'item'])


@receiver(send_activity_log, dispatch_uid="core.on_activity_received")
def on_activity_received(sender, **kwargs):
    # actor has to be popped, the rest has to remain in kwargs and is not used here, except message to use in abridge
    from toolkit.core.services.lawpal_abridge import LawPalAbridgeService  # import the server

    # Pops
    actor = kwargs.pop('actor', False)
    kwargs.pop('signal', None)
    # Gets
    verb = kwargs.get('verb', False)
    action_object = kwargs.get('action_object', False)
    target = kwargs.get('target', False)
    message = kwargs.get('message', False)

    #
    # Test that we have the required arguments to send the action signal
    #
    if actor and verb and action_object and target:
        # send to django-activity-stream
        action.send(actor, **kwargs)

        # send data to abridge
        for user in target.participants.all():
            #
            # Categorically turn it off by default
            #
            try:
                #from toolkit.core.services import LawPalAbridgeService
                s = LawPalAbridgeService(user=user,
                                         ABRIDGE_ENABLED=getattr(settings, 'ABRIDGE_ENABLED', False))  # initialize and pass in the user

                if not message:
                    message = '%s %s %s' % (actor, verb, action_object)

                s.create_event(content_group=target.name,
                               content='<div style="font-size:3.3em;">%s</div>' % message)

            except requests.exceptions.ConnectionError, e:
                # AbridgeService is not running.
                logger.critical('Abridge Service is not running because: %s' % e)
