# -*- coding: utf-8 -*-
from django import template
from django.utils.safestring import mark_safe, SafeText

from dateutil import parser

register = template.Library()

import logging
logger = logging.getLogger('django.request')


@register.filter(name='full_address')
def full_address(address):
    """
    Print the address in a human readable format.
    """
    addr = '<strong>%s</strong><br>' % address['address1']

    if address.get('address2', False):
        addr = addr + '%s<br>' % address['address2']

    addr = addr + '%s, %s %s' % (address['city'], address['state'], address['zip'])

    if address.get('country', False):
        addr = addr + '<br>%s' % address['country']

    return mark_safe('<address>%s</address>' % addr)


@register.filter(name='to_date')
def to_date(value):
    logger.info('to_date: %s %s' % (value, type(value)))
    if type(value) in [SafeText, str, unicode]:
        return parser.parse(value)
    return value
