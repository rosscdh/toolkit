# -*- coding: utf-8 -*-
from django import template

register = template.Library()


@register.inclusion_tag('matter/partials/user_intro.html', takes_context=True)
def user_intro(context):
    return context