# -*- coding: utf-8 -*-
from django import template
from django.template.defaultfilters import floatformat
from django.utils.safestring import mark_safe

register = template.Library()

import logging
logger = logging.getLogger('django.request')


@register.filter
def quick_status(engageletter):
    if engageletter.is_complete:
        return mark_safe('<span class="label label-success">COMPLETE</span>')

    else:
        return mark_safe('<span class="label label-success">%s%%</span>' % floatformat(engageletter.markers.percent_complete, '0'))


@register.filter
def status_row_class(engageletter):
    if engageletter.is_complete:
        return 'success'
