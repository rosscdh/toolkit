# -*- coding: utf-8 -*-
"""
Signals that listen for changes to the core models and then record them as
activity_stream objects
@TODO turn the signal handlers into its own module
"""
from django import template
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

from toolkit.apps.notification.templatetags.notice_tags import get_notification_template, get_notification_context

#from toolkit.apps.notification.tasks import youve_got_notifications

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


def _serialize_kwargs(kwargs):
    for key, item in kwargs.iteritems():
        if hasattr(item, 'api_serializer') is True:
            kwargs[key] = item.api_serializer(item, context={'request': None}).data
    return kwargs


def _activity_send(actor, target, action_object, message, **kwargs):
    """
    Send activity to django-activity-stream
    """
    verb_slug = kwargs.get('verb_slug', False)

    if verb_slug in ACTIVITY_WHITELIST:
        kwargs = _serialize_kwargs(kwargs)
        action.send(actor, target=target, action_object=action_object, message=message, **kwargs)


def _abridge_send(verb_slug, actor, target, action_object, message=None, comment=None, item=None):
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
            except Exception as e:
                # AbridgeService is not running.
                logger.critical('Abridge Service is not running because: %s' % e)
                s = False

            if s:
                if message:
                    #
                    # @MARIUS I think that this would best be done as a @staticmethod
                    # as part of the LawPalAbridgeService that way its reuseable
                    # and sole responsiblity? thoughts? rc
                    #
                    message_data = _serialize_kwargs({'actor': actor,
                                                      'action_object': action_object,
                                                      'target': target,
                                                      'comment': comment,
                                                      'item': item})
                    t = get_notification_template(verb_slug)
                    ctx = get_notification_context(message_data, user)
                    ctx.update({
                        # 'notice_pk': notice.pk,
                        # 'date': notice.message.date,
                        'message': message,
                    })

                    context = template.loader.Context(ctx)

                    # render the template with passed in context
                    message_for_abridge = t.render(context)

                    s.create_event(content_group=target.name,
                                   content=message_for_abridge)


def _notifications_send(verb_slug, actor, target, action_object, message, comment, item, send_to_all=False):
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

    if verb_slug in NOTIFICATIONS_WHITELIST:

        # catch when we have no stored message
        if stored_messages is None:
            logger.critical('django-stored-messages is not installed')
            return None

        if message:

            from toolkit.api.serializers.user import LiteUserSerializer
            # from toolkit.api.serializers.matter import LiteMatterSerializer

            query_set = target.participants
            #
            # If we are not sending this message to all participants then exclude the originator
            #
            if send_to_all is False:
                query_set = query_set.exclude(id=actor.pk)

            # Because we cant mixn the ApiMixin class ot the django User Object
            actor = LiteUserSerializer(actor, context={'request': None}).data

            if hasattr(action_object, 'api_serializer') is True:
                action_object = action_object.api_serializer(action_object, context={'request': None}).data
            if hasattr(item, 'api_serializer') is True:
                item = item.api_serializer(item, context={'request': None}).data

            target_class_name = target.__class__.__name__

            if target_class_name == 'Workspace':
                target = target.api_serializer(target, context={'request': None}).data

            else:
                raise Exception('Unknown target_class_name: %s' % target_class_name)

            stored_messages.add_message_for(users=query_set.all(),
                                            level=stored_messages.STORED_INFO,
                                            message=message,
                                            extra_tags='',
                                            fail_silently=False,
                                            verb_slug=verb_slug,
                                            actor=actor,
                                            action_object=action_object,
                                            target=target,
                                            comment=comment,
                                            item=item)

            #
            # @TODO move into manager?
            #
            for u in query_set.select_related('profile').exclude(profile__has_notifications=True):
                profile = u.profile
                profile.has_notifications = True
                profile.save(update_fields=['has_notifications'])


@receiver(send_activity_log, dispatch_uid="core.on_activity_received")
def on_activity_received(sender, **kwargs):
    # actor has to be popped, the rest has to remain in kwargs and is not used here, except message to use in abridge
    actor = kwargs.pop('actor', False)
    kwargs.pop('signal', None)
    # Gets
    verb = kwargs.get('verb', False)
    action_object = kwargs.get('action_object', False)
    target = kwargs.get('target', False)

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

    if not message:
        message = u'%s %s %s' % (actor, verb, action_object)

    #
    # Test that we have the required arguments to send the action signal
    #
    if actor and action_object and target and verb_slug:
        # send to django-activity-stream
        # note the kwarg.pop so that they dont get sent in as kwargs
        _activity_send(actor=actor, target=kwargs.pop('target', None), action_object=kwargs.pop('action_object', None),
                       message=kwargs.pop('message', None), **kwargs)

        # send the notifications to the participants
        _notifications_send(verb_slug=verb_slug, actor=actor, target=target, action_object=action_object,
                            message=message, comment=kwargs.get('comment', None),
                            item=kwargs.get('item', None), send_to_all=send_to_all)
        # send to abridge service
        _abridge_send(verb_slug=verb_slug, actor=actor, target=target, action_object=action_object, message=message,
                      comment=kwargs.get('comment', None), item=kwargs.get('item', None))
