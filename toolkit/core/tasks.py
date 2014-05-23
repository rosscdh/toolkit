# -*- coding: utf-8 -*-
from django.conf import settings

from toolkit.celery import app
from toolkit.tasks import run_task
from toolkit.core.services.lawpal_abridge import LawPalAbridgeService
from toolkit.apps.default.templatetags.toolkit_tags import ABSOLUTE_BASE_URL
from toolkit.apps.notification.tasks import youve_got_notifications

import logging
logger = logging.getLogger('django.request')

ACTIVITY_WHITELIST = settings.LAWPAL_ACTIVITY.get('activity', {}).get('whitelist', [])
ABRIDGE_WHITELIST = settings.LAWPAL_ACTIVITY.get('abridge', {}).get('whitelist', [])
NOTIFICATIONS_WHITELIST = settings.LAWPAL_ACTIVITY.get('notifications', {}).get('whitelist', [])

try:
    from actstream import action
except ImportError:
    logger.critical('django-activity-stream is not installed')
    raise Exception('django-activity-stream is not installed')

try:
    import stored_messages
except ImportError:
    logger.critical('django-stored-messages is not installed')
    raise Exception('django-stored-messages is not installed')


def _serialize_kwargs(kwargs):
    for key, item in kwargs.iteritems():
        if hasattr(item, 'api_serializer') is True:
            kwargs[key] = item.api_serializer(item, context={'request': None}).data
    return kwargs


@app.task
def _activity_send(actor, target, action_object, message, **kwargs):
    """
    Send activity to django-activity-stream
    """
    verb_slug = kwargs.get('verb_slug', False)

    if verb_slug in ACTIVITY_WHITELIST:
        kwargs = _serialize_kwargs(kwargs)
        action.send(actor, target=target, action_object=action_object, message=message, **kwargs)


@app.task
def _abridge_send(verb_slug, actor, target, action_object, message=None, comment=None, item=None,
                  reviewdocument=None, send_to_all=False):
    """
    Send activity data to abridge
    """
    if verb_slug in ABRIDGE_WHITELIST:
        abridge_service = False  # assume false

        query_set = target.participants
        #
        # If we are not sending this message to all participants then exclude the originator
        #
        if send_to_all is False:
            query_set = query_set.exclude(id=actor.pk)

        for user in query_set.all():
            #
            # Categorically turn it off by default
            #
            try:
                abridge_service = LawPalAbridgeService(user=user,
                                                       ABRIDGE_ENABLED=getattr(settings, 'ABRIDGE_ENABLED', False))  
                                                       # initialize and pass in the user
            except Exception as e:
                # AbridgeService is not running.
                logger.critical('Abridge Service is not running because: %s' % e)

            if abridge_service:
                from toolkit.api.serializers.user import LiteUserSerializer
                message_data = _serialize_kwargs({'actor': actor,
                                                  'action_object': action_object,
                                                  'target': target,
                                                  'comment': comment,
                                                  'message': message,
                                                  'item': item,
                                                  'reviewdocument': reviewdocument,
                                                  'verb_slug': verb_slug})
                # Because we cant mixn the ApiMixin class ot the django User Object
                message_data['actor'] = LiteUserSerializer(actor, context={'request': None}).data

                message_for_abridge = LawPalAbridgeService.render_message_template(user, **message_data)

                abridge_service.create_event(content_group=target.name,
                                             content=message_for_abridge)


@app.task
def _notifications_send(verb_slug, actor, target, action_object, message, comment, item, reviewdocument,
                        send_to_all=False):
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

            query_set = target.participants.select_related('profile')
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
            if hasattr(reviewdocument, 'api_serializer') is True:
                reviewdocument = reviewdocument.api_serializer(item, context={'request': None}).data

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
                                            item=item,
                                            reviewdocument=reviewdocument)

            #
            # @TODO move into manager?
            #
            for u in query_set.exclude(profile__has_notifications=True):
                profile = u.profile
                profile.has_notifications = True
                profile.save(update_fields=['has_notifications'])
            #
            # Send pusher notification
            #
            for u in query_set.values('username'):
                run_task(youve_got_notifications, 
                    username=u.get('username'),
                    event='notifications.new')
