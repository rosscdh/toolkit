# -*- coding: utf-8 -*-
"""
Signals that listen for changes to the core models and then record them as
activity_stream objects
@TODO turn the signal handlers into its own module
"""
from actstream import action
from django.dispatch import receiver
from django.dispatch.dispatcher import Signal


"""
Base Signal and listener used to funnel events
"""


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

"""
Listen for events from various models
"""
# signal handlers for post_save:

def on_workspace_post_save(sender, instance, created, **kwargs):
    """
        The owning lawyer is the only one who can create, modify or delete the workspace, so this is possible.
    """
    if created:
        send_activity_log.send(sender, **{
            actor=instance.lawyer,
            verb=u'created',
            action_object=instance,
            target=instance
        })


def on_item_post_save(sender, instance, created, **kwargs):
    """
        At this moment only the layer can edit items. So this is possible.
    """
    if created:
        send_activity_log.send(sender, **{
            actor=instance.matter.lawyer,
            verb=u'created',
            action_object=instance,
            target=instance.matter
        })


def on_revision_post_save(sender, instance, created, **kwargs):
    if created:
        send_activity_log.send(sender, **{
            actor=instance.uploaded_by,
            verb=u'created',
            action_object=instance,
            target=instance.item.matter
        })