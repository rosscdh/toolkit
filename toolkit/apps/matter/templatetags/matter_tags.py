# -*- coding: utf-8 -*-
from django import template
from django.conf import settings

register = template.Library()

SHOW_USER_INTRO = getattr(settings, 'DEMO_MATTER_SHOW_USER_INTRO', False)


@register.inclusion_tag('matter/partials/user_intro.html', takes_context=True)
def user_intro(context):
    if SHOW_USER_INTRO is False:
        context.update({
            'firstseen': False
        })
    return context