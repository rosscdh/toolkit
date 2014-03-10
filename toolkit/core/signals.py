# -*- coding: utf-8 -*-
__author__ = 'Marius Burfey <marius.burfey@ambient-innovation.com> 07.03.14'

from actstream import action
from django.dispatch import receiver
from django.dispatch.dispatcher import Signal


# first four args as in django-activity-stream, plus custom stuff
send_activity_log = Signal(providing_args=['actor', 'verb', 'action_object', 'target', 'ip'])


@receiver(send_activity_log, dispatch_uid="core.on_activity_received")
def on_activity_received(sender, **kwargs):
    # actor has to be popped, the rest has to remain in kwargs
    # Pops
    actor = kwargs.pop('actor', False)
    signal = kwargs.pop('signal', None)
    # Gets
    verb = kwargs.get('verb', False)
    action_object = kwargs.get('action_object', False)
    target = kwargs.get('target', False)

    #
    # Test that we have the required arguments to send the action signal
    #
    if actor and verb and action_object and target:
        # send to django-activity-stream
        action.send(actor, **kwargs)