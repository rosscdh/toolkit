# -*- coding: utf-8 -*-
__author__ = 'Marius Burfey <marius.burfey@ambient-innovation.com> 07.03.14'

from actstream import action
from django.dispatch import receiver
from django.dispatch.dispatcher import Signal


# first four args as in django-activity-stream, plus custom stuff
send_activity_log = Signal(providing_args=['actor', 'verb', 'action_object', 'target', 'ip'])


@receiver(send_activity_log, dispatch_uid="WkkDwb4BVw")
def on_activity_received(sender, **kwargs):
    actor = kwargs.pop('actor', False)
    verb = kwargs.pop('verb', False)
    action_object = kwargs.pop('action_object', False)
    target = kwargs.pop('target', False)

    if actor and verb and action_object and target:

        # do stuff depending on given information

        # add relevant information to kwargs for django-activity-stream and send
        kwargs.update({
            'actor': actor,
            'verb': verb,
            'action_object': action_object,
            'target': target
        })

        action.send(actor, verb=verb, action_object=action_object)
        # action.send(sender, **kwargs)