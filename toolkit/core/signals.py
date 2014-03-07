# -*- coding: utf-8 -*-
__author__ = 'Marius Burfey <marius.burfey@ambient-innovation.com> 07.03.14'

from actstream import action
from django.dispatch import receiver
from django.dispatch.dispatcher import Signal


# first four args as in django-activity-stream, plus custom stuff
send_activity_log = Signal(providing_args=['actor', 'verb', 'action_object', 'target', 'ip', 'whatever'])


@receiver(send_activity_log, dispatch_uid="check_if_i_must_be_dynamic")
def on_activity_recieved(sender, **kwargs):
    actor = kwargs.pop('actor', False)
    verb = kwargs.pop('verb', False)
    action_object = kwargs.pop('action_object', False)
    target = kwargs.pop('target', False)

    if actor and verb and action_object and target:

        # do stuff depending on given information

        # add relevant information to kwargs for django-activity-stream and send
        kwargs['actor'] = actor
        kwargs['verb'] = verb
        kwargs['action_object'] = action_object
        kwargs['target'] = target

        print kwargs

        action.send(actor, verb=verb, action_object=action_object)
        # action.send(sender, **kwargs)