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
    actor = kwargs.pop('actor', False)
    verb = kwargs.get('verb', False)
    action_object = kwargs.get('action_object', False)
    target = kwargs.get('target', False)

    # kwargs will be reused and "old" signal is not needed any more
    del kwargs['signal']

    if actor and verb and action_object and target:

        # do stuff depending on given information, including updating kwargs if needed

        # send to django-activity-stream
        action.send(actor, **kwargs)