# -*- coding: utf-8 -*-
from django import template
import re
from toolkit.apps.review.models import ReviewDocument

from toolkit.core.item.models import Item  # circular

prog = re.compile('/([a-z\d]*)$', flags=re.IGNORECASE)
register = template.Library()

import logging
logger = logging.getLogger('django.request')


NOTIFICATION_TEMPLATES = {
    'default': template.loader.get_template('notification/partials/default.html'),
    'item-commented': template.loader.get_template('notification/partials/item_comment.html'),
    'revision-added-review-session-comment': template.loader.get_template('notification/partials/review_session_comment.html'),
    'revision-added-revision-comment': template.loader.get_template('notification/partials/revision_comment.html'),
}


def get_notification_template(verb_slug):
    return NOTIFICATION_TEMPLATES.get(verb_slug, NOTIFICATION_TEMPLATES.get('default'))


def get_notification_context(message_data, user):
    actor = message_data.get('actor')

    action_object = message_data.get('action_object')
    target = message_data.get('target')
    client = target.get('client') if target is not None else None

    comment = message_data.get('comment', None)
    item = message_data.get('item', None)
    reviewdocument = message_data.get('reviewdocument', None)

    action_object_url = ""
    reviewer_object = None

    if action_object:

        # it's a default object.
        action_object_url = action_object.get('regular_url', None)  # never use action_object.get('url', None) as we never want the serializer (api) url which is the api link to be used here

        item_queryset = Item.objects.select_related('matter')

        if comment:
            # it's a comment either on item or revision
            if item:
                try:
                    reviewdocument_object = ReviewDocument.objects.get(slug=reviewdocument.get('slug')) if reviewdocument else None
                except ReviewDocument.DoesNotExist:
                    # should not happen in production, only in dev if first crocodoc-signal didn't reach the server
                    # (for example because of missing ngrok)
                    logger.error(u"ReviewDocument did not exist: %s" % reviewdocument.get('slug'))
                    reviewdocument_object = None

                # getting the reviewer_object is ONLY possible if we have a review_copy. otherwise the reviewers are empty
                reviewer_object = reviewdocument_object.reviewers.first() if reviewdocument_object else None

                action_object_url = reviewdocument_object.get_regular_url() if reviewdocument_object else None
            else:
                # it's a link on an item -> show item-link
                target_object = item_queryset.get(slug=action_object.get('slug'))
                action_object_url = target_object.get_regular_url()

    #
    # UGLY HACK
    #
    if action_object_url is None or 'None' in action_object_url:
        action_object_url = None

    if message_data is not None:
        ctx = {
            'actor_name': actor.get('name') if actor else None,
            'actor_initials': actor.get('initials') if actor else None,
            'comment': comment,
            'item_name': item.get('name') if item else None,
            'reviewer_name': reviewer_object.get_full_name() if reviewer_object else None,
            'revision_slug': action_object.get('slug') if action_object else None,
            'action_object_url': action_object_url,
            'action_object_name': action_object.get('name') if action_object else None,
            'base_url': target.get('base_url') if target else None,
            'target_name': target.get('name') if target else None,
            'client_name': client.get('name') if client else None,
        }

    return ctx


@register.simple_tag
def render_notice(notice, request=None):
    """
    Is used on notifications-page and works similar to ActivitySerializer:
    - load verb_slug and decide on this (-> NOTIFICATION_TEMPLATES) which template is used
    - fill ctx with needed data
    """
    message_data = notice.message.data

    verb_slug = message_data.get('verb_slug')

    t = get_notification_template(verb_slug)
    ctx = get_notification_context(message_data, request.user)
    ctx.update({
        'notice_pk': notice.pk,
        'date': notice.message.date,
        'message': notice.message.message,
    })
    context = template.loader.Context(ctx)

    # render the template with passed in context
    return t.render(context)