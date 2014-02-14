# -*- coding: utf-8 -*-
from django import template
from django.conf import settings
from toolkit.utils import CURRENT_SITE

import urlparse

register = template.Library()

import logging
logger = logging.getLogger('django.request')

_CURRENT_SITE = CURRENT_SITE()
_DOMAIN_WITHOUT_END_SLASH = _CURRENT_SITE.domain[0:-1] if _CURRENT_SITE.domain[-1] == '/' else _CURRENT_SITE.domain


@register.simple_tag
def ABSOLUTE_BASE_URL(path=None):
    return urlparse.urljoin(_CURRENT_SITE, path)
ABSOLUTE_BASE_URL.is_safe = True

@register.simple_tag
def ABSOLUTE_STATIC_URL(path=None):
    if path is not None:
        path = path if settings.STATIC_URL in path else '%s%s' % (settings.STATIC_URL, path)
    url = '{domain}{path}'.format(domain=_DOMAIN_WITHOUT_END_SLASH, path=path)
    return url
ABSOLUTE_STATIC_URL.is_safe = True

@register.simple_tag
def ABSOLUTE_MEDIA_URL(path=None):
    if path is not None:
        path = path if settings.MEDIA_URL in path else '%s%s' % (settings.MEDIA_URL, path)

    return '{domain}{path}'.format(domain=_DOMAIN_WITHOUT_END_SLASH, path=path)
ABSOLUTE_MEDIA_URL.is_safe = True
