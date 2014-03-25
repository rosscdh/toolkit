# -*- coding: utf-8 -*-
"""
Signals that listen for changes to the core models and then record them as
activity_stream objects
@TODO turn the signal handlers into its own module
"""
from django.conf import settings
from django.dispatch import receiver
from django.dispatch.dispatcher import Signal

try:
    from actstream import action
except ImportError:
    action = None

try:
    import stored_messages
except ImportError:
    stored_messages = None

from toolkit.core.services.lawpal_abridge import LawPalAbridgeService

import logging
logger = logging.getLogger('django.request')

"""
Base Signal and listener used to funnel events
"""


# first four args as in django-activity-stream, plus custom stuff
send_activity_log = Signal(providing_args=['actor', 'verb', 'action_object', 'target', 'message', 'user', 'item',
                                           'comment', 'previous_name', 'current_status', 'previous_status', 'filename',
                                           'date_created', 'version'])

ACTIVITY_WHITELIST = settings.LAWPAL_ACTIVITY.get('activity', {}).get('whitelist', [])
ABRIDGE_WHITELIST = settings.LAWPAL_ACTIVITY.get('abridge', {}).get('whitelist', [])
NOTIFICATIONS_WHITELIST = settings.LAWPAL_ACTIVITY.get('notifications', {}).get('whitelist', [])


def _activity_send(actor, **kwargs):
    """
    Send activity to django-activity-stream
    """
    verb_slug = kwargs.get('verb_slug', False)
    # import pdb;pdb.set_trace()
    if verb_slug in ACTIVITY_WHITELIST:
        action.send(actor, **kwargs)


def _abridge_send(verb_slug, actor, target, message=None):
    """
    Send activity data to abridge
    """
    if verb_slug in ABRIDGE_WHITELIST:
        for user in target.participants.exclude(id=actor.pk).all():
            #
            # Categorically turn it off by default
            #
            try:
                s = LawPalAbridgeService(user=user,
                                         ABRIDGE_ENABLED=getattr(settings, 'ABRIDGE_ENABLED', False))  # initialize and pass in the user
                if message:
                    s.create_event(content_group=target.name,
                                   content='<div style="font-size:3.3em;">%s</div>' % message)

            except Exception as e:
                # AbridgeService is not running.
                logger.critical('Abridge Service is not running because: %s' % e)


def _notifications_send(verb_slug, actor, target, message):
    """
    Send persistent messages (notifications) for this user
    github notifications style
        stored_messages.STORED_DEBUG,
        stored_messages.STORED_INFO,
        stored_messages.STORED_SUCCESS,
        stored_messages.STORED_WARNING,
        stored_messages.STORED_ERROR
    update the user.profile.has_notifications
    """
    #import pdb;pdb.set_trace()
    if verb_slug in NOTIFICATIONS_WHITELIST:
        # catch when we have no stored message
        if stored_messages is None:
            logger.critical('django-stored-messages is not installed')
            return None

        if message:
            query_set = target.participants.exclude(id=actor.pk)
            stored_messages.add_message_for(users=query_set.all(),
                                            level=stored_messages.STORED_INFO,
                                            message=message,
                                            extra_tags='',
                                            fail_silently=False)
            #
            # @TODO move into manager?
            #
            for u in query_set.all():
                profile = u.profile
                profile.has_notifications = True
                profile.save(update_fields=['has_notifications'])


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
    verb_slug = kwargs.get('verb_slug', False)

    if not message:
        message = '%s %s %s' % (actor, verb, action_object)

    #
    # Test that we have the required arguments to send the action signal
    #
    if actor and verb and action_object and target and verb_slug:
        # catch if we don't have it installed
        if action is None:
            logger.critical('actstream is not installed')
        else:
            # send to django-activity-stream
            _activity_send(actor=actor, **kwargs)

        # send the notifications to the participants
        _notifications_send(verb_slug=verb_slug, actor=actor, target=target, message=message)
        # send to abridge service
        _abridge_send(verb_slug=verb_slug, actor=actor, target=target, message=message)