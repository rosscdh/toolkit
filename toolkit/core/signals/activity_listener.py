# -*- coding: utf-8 -*-
"""
Signals that listen for changes to the core models and then record them as
activity_stream objects
@TODO turn the signal handlers into its own module
"""
from django.dispatch import receiver
from django.dispatch.dispatcher import Signal

from toolkit.tasks import run_task
from toolkit.core.tasks import (_activity_send,
                                _activity_delete,
                                _abridge_send,
                                _notifications_send,
                                _mentions_send,)
import logging
logger = logging.getLogger('django.request')


"""
Base Signal and listener used to funnel events
"""


# first four args as in django-activity-stream, plus custom stuff
send_activity_log = Signal(providing_args=['actor', 'verb', 'action_object', 'target', 'message', 'user', 'item',
                                           'comment', 'previous_name', 'current_status', 'previous_status', 'filename',
                                           'date_created', 'version'])
delete_activity_log = Signal(providing_args=['actor', 'uuid', 'action_object', 'item'])


@receiver(send_activity_log, dispatch_uid="core.on_activity_received")
def on_activity_received(sender, **kwargs):
    # actor has to be popped, the rest has to remain in kwargs and is not used here, except message to use in abridge
    actor = kwargs.pop('actor', False)
    kwargs.pop('signal', None)
    # Gets
    verb = kwargs.get('verb', False)
    action_object = kwargs.get('action_object', False)
    target = kwargs.get('target', False)
    reviewdocument = kwargs.get('reviewdocument', False)

    send_to_all = kwargs.get('send_to_all', False)

    message = kwargs.get('message', False)
    #
    # allow us to override the generic message passed in
    #
    if kwargs.get('override_message') not in [None, '']:
        #
        # @BUSINESSRULE must override the "message" key here
        # but preserve original_message
        #
        kwargs['original_message'] = kwargs['message']  # preserve

        message = kwargs.get('override_message')
        # override the message
        kwargs['message'] = message

    verb_slug = kwargs.get('verb_slug', False)

    #
    # Ugly default message
    #
    if not message:
        message = u'%s %s %s' % (actor, verb, action_object)

    #
    # Test that we have the required arguments to send the action signal
    #
    if actor and action_object and target and verb_slug:
        # send to django-activity-stream
        # note the kwarg.pop so that they dont get sent in as kwargs
        # skip_async = True means the activity will be added synchronously
        run_task(_activity_send, actor=actor, target=kwargs.pop('target', None),
                 action_object=kwargs.pop('action_object', None), message=kwargs.pop('message', None),
                 **kwargs)

        # send the notifications to the participants
        run_task(_notifications_send, verb_slug=verb_slug, actor=actor, target=target, action_object=action_object,
                 message=message, comment=kwargs.get('comment', None), item=kwargs.get('item', None),
                 reviewdocument=reviewdocument, send_to_all=send_to_all)

        # send to abridge service
        run_task(_abridge_send, verb_slug=verb_slug, actor=actor, target=target, action_object=action_object,
                 message=message, comment=kwargs.get('comment', None), item=kwargs.get('item', None),
                 reviewdocument=reviewdocument, send_to_all=send_to_all)

        # send the @username mentions
        run_task(_mentions_send, actor=actor, action_object=action_object, text=kwargs.get('comment', message))

    else:
        logger.error('One or more or actor: {actor} action_object: {action_object} target: {target} verb_slug: {verb_slug} where not provided'.format(actor=actor, action_object=action_object, target=target, verb_slug=verb_slug))


@receiver(delete_activity_log, dispatch_uid="core.delete_activity_log")
def on_delete_activity_log(sender, uuid, item, action_object, **kwargs):
    """
    Delete Activity based on passed in crocodoc uuid
    """
    _activity_delete(uuid=uuid, target=item, action_object=action_object, **kwargs)

