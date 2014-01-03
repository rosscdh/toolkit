# -*- coding: utf-8 -*-
from django import template
from django.utils.safestring import SafeText
from dateutil import parser

register = template.Library()

import logging
logger = logging.getLogger('django.request')


@register.filter(name='to_date')
def to_date(value):
    logger.info('to_date: %s %s' % (value, type(value)))
    if type(value) in [SafeText, str, unicode]:
        return parser.parse(value)
    return value