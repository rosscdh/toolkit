# -*- coding: utf-8 -*-
"""
Signals that listen for changes to the core models and then record them as
activity_stream objects
@TODO turn the signal handlers into its own module
"""
from actstream import action
from django.dispatch import receiver
from django.dispatch.dispatcher import Signal
from abridge.services import AbridgeService  # import the server


"""
Base Signal and listener used to funnel events
"""


# first four args as in django-activity-stream, plus custom stuff
send_activity_log = Signal(providing_args=['actor', 'verb', 'action_object', 'target', 'message', 'user', 'item'])


@receiver(send_activity_log, dispatch_uid="core.on_activity_received")
def on_activity_received(sender, **kwargs):
    # actor has to be popped, the rest has to remain in kwargs and is not used here, except message to use in abridge

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
            s = AbridgeService(user=user)  # initialize and pass in the user
            if not message:
                message = '%s %s %s' % (actor, verb, action_object)
            s.create_event(content_group=target.name,
                           content='<div style="font-size:3.3em;">%s</div>' % message)

"""
Listen for events from various models
"""
# signal handlers for post_save:

def on_workspace_post_save(sender, instance, created, **kwargs):
    """
        The owning lawyer is the only one who can create, modify or delete the workspace, so this is possible.
    """
    if created:
        from toolkit.core.services import MatterActivityEventService
        MatterActivityEventService(instance).created_matter(lawyer=instance.lawyer)


def on_item_post_save(sender, instance, created, **kwargs):
    """
        At this moment only the layer can edit items. So this is possible.
    """
    if created:
        from toolkit.core.services import MatterActivityEventService
        MatterActivityEventService(instance.matter).created_item(user=instance.matter.lawyer, item=instance)


# def on_revision_post_save(sender, instance, created, **kwargs):
#     if created:
#         activity_service = MatterActivityEventService(instance.item.matter)
#         activity_service.created_revision(user=instance.uploaded_by, revision=instance)
