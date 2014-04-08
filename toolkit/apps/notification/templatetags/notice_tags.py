# -*- coding: utf-8 -*-
from django import template

register = template.Library()

import logging
logger = logging.getLogger('django.request')


@register.inclusion_tag('notification/partials/notice.html', takes_context=False)
def render_notice(notice):
    message = notice.message.data
    return {
        'pk': notice.pk,
        'actor_name': message.get('actor').get('name'),
        'actor_initials': message.get('actor').get('initials'),
        'message': notice.message,
        'date': notice.message.date,
        'base_url': message.get('target').get('base_url'),
        'target_name': message.get('target').get('name'),
        'client_name': message.get('target').get('client').get('name'),
        'notice_message': notice.message
    }
