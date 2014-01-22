# -*- coding: utf-8 -*-
from django import template

register = template.Library()

import logging
logger = logging.getLogger('django.request')


@register.inclusion_tag('engageletter/partials/lawyer_header.html', takes_context=False)
def lawyer_header(lawyer):
    return {
    }


@register.inclusion_tag('engageletter/partials/lawyer_footer.html', takes_context=False)
def lawyer_footer(lawyer):
    return {
    }