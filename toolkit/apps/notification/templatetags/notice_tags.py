# -*- coding: utf-8 -*-
from django import template
import re
from toolkit.apps.review.models import ReviewDocument
from toolkit.core.item.models import Item

prog = re.compile('/([a-z\d]*)$', flags=re.IGNORECASE)
from toolkit.core.attachment.models import Revision

register = template.Library()

import logging
logger = logging.getLogger('django.request')


@register.inclusion_tag('notification/partials/default.html', takes_context=False)
def render_notice(notice, request=None):
    message = notice.message.data

    actor = message.get('actor')
    action_object = message.get('action_object')
    target = message.get('target')
    client = target.get('client')

    action_object_url = ""

    if action_object:

        # if action_object contains an item, it MUST be a revision. -> build revision link of the following format:
        # /matters/lawpal-corporate-setup/#/checklist/41b53cd527224809a5fd5e325c7511f1/:user_crocodoc_deatil_view_url
        item_link = action_object.get('item')  # perhaps use this link instead of get_absolute_link() ?
        if item_link and request:  # without a user I cannot create a user_review_url

            # perhaps we should add the serialized item to the messages json-data?
            item_slug = re.search(prog, item_link).group(1)

            # revision = Revision.objects.get(slug=action_object['slug'], item__slug=item_slug)
            # review_document = ReviewDocument.objects.get(document=revision, reviewer__in=[request.user.pk, ])

            item = Item.objects.get(slug=item_slug)
            review_document_link = item.get_user_review_url(user=request.user, version_slug=action_object['slug'])

            action_object_url = "%s:%s" % (item.get_absolute_url(), review_document_link)
        else:
            action_object_url = action_object.get('url') if action_object else None

    if message is not None:
        return {
            'pk': notice.pk,
            'actor_name': actor.get('name') if actor else None,
            'actor_initials': actor.get('initials') if actor else None,
            'message': notice.message,
            'action_object_url': action_object_url,
            'action_object_name': action_object.get('name') if action_object else None,
            'date': notice.message.date,
            'base_url': target.get('base_url') if target else None,
            'target_name': target.get('name') if target else None,
            'client_name': client.get('name') if client else None,
        }
