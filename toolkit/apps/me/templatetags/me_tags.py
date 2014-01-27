# -*- coding: utf-8 -*-
from django import template

register = template.Library()

import logging
logger = logging.getLogger('django.request')


@register.inclusion_tag('lawyer/letterhead/lawyer_header.html', takes_context=False)
def lawyer_header(lawyer):
    return {
        'lawyer': lawyer,
        'profile': lawyer.profile,
        'firm_logo': lawyer.profile.firm_logo,
        'firm_address': lawyer.profile.data.get('firm_address'),
    }


@register.inclusion_tag('lawyer/letterhead/lawyer_footer.html', takes_context=False)
def lawyer_footer(lawyer):
    return {
        'lawyer': lawyer,
        'profile': lawyer.profile,
        'firm_logo': lawyer.profile.firm_logo,
        'firm_address': lawyer.profile.data.get('firm_address'),
    }