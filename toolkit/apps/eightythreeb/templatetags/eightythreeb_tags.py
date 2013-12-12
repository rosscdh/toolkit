# -*- coding: utf-8 -*-
from django import template

from dateutil import parser

register = template.Library()


@register.filter(name='to_date')
def to_date(value):
    if type(value) in [str, unicode]:
        return parser.parse(value)
    return value