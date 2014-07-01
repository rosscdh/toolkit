# -*- coding: utf-8 -*-
from django import template
from django.contrib.auth.models import User

register = template.Library()


@register.inclusion_tag('partials/avatar.html', takes_context=False)
def avatar(user):
    if isinstance(user, User):
        user.initials = user.get_initials
        user.name = user.get_full_name

    elif isinstance(user, dict):
        user.initials = getattr(user, 'initials', None)
        user.name = getattr(user, 'name', None)

    return {
        'user': user,
    }
