# -*- coding: utf-8 -*-
from django import template

register = template.Library()

import logging
logger = logging.getLogger('django.request')


@register.inclusion_tag('notification/partials/notice.html', takes_context=False)
def render_notice(notice):
    message = notice.message.data

    actor = message.get('actor')
    action_object = message.get('action_object')
    target = message.get('target')
    client = target.get('client')

    if message is not None:
        return {
            'pk': notice.pk,
            'actor_name': actor.get('name') if actor else None,
            'actor_initials': actor.get('initials') if actor else None,
            'message': notice.message,
            'action_object': action_object,
            'date': notice.message.date,
            'base_url': target.get('base_url') if target else None,
            'target_name': target.get('name') if target else None,
            'client_name': client.get('name') if client else None,
        }
