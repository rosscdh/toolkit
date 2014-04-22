# -*- coding: utf-8 -*-
from django import template
import re
from toolkit.core.item.models import Item

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


def _get_context(message_data, user):
    actor = message_data.get('actor')
    action_object = message_data.get('action_object')
    target = message_data.get('target')
    client = target.get('client')

    comment = message_data.get('comment', None)
    item = message_data.get('item', None)

    action_object_url = ""

    if action_object:
        if comment:
            # it's a comment either on item or revision
            if item:
                # # if action_object contains an item, it MUST be a revision. -> build revision link of the following format:
                # # /matters/lawpal-corporate-setup/#/checklist/41b53cd527224809a5fd5e325c7511f1/:user_crocodoc_deatil_view_url
                item_object = Item.objects.get(slug=item.get('slug'))
                # item = item.object  # is a dict, not a serializer-object
                # item_s = ItemSerializer(item)
                # item_o = item_s.get_object()
                action_object_url = item_object.get_full_user_review_url(user=user, version_slug=action_object['slug'])
                # review_document_link = item_object.get_user_review_url(user=user, version_slug=action_object['slug'])

                # action_object_url = "%s:%s" % (item_object.get_absolute_url(), review_document_link)
            else:
                # it's a link on an item -> show item-link
                target_object = Item.objects.get(slug=action_object.get('slug'))
                action_object_url = target_object.get_absolute_url() if action_object else None
                # action_object_url = action_object.get('url') if action_object else None
        else:
            # it's a default object.
            # would be great to have a generic way from the serialized object (-> dict) to the object to call
            # get_absolute_url()
            action_object_url = action_object.get('url') if action_object else None

    if message_data is not None:
        ctx = {
            'actor_name': actor.get('name') if actor else None,
            'actor_initials': actor.get('initials') if actor else None,
            'comment': comment,
            'item_name': item.get('name') if item else None,
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
    ctx = _get_context(message_data, request.user)
    ctx.update({
        'notice_pk': notice.pk,
        'date': notice.message.date,
        'message': notice.message.message,
    })
    context = template.loader.Context(ctx)

    # render the template with passed in context
    return t.render(context)