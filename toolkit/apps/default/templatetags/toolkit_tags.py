# -*- coding: utf-8 -*-
from django import template
from django.conf import settings
from django.core.urlresolvers import reverse
from django.contrib.contenttypes.models import ContentType

from toolkit.utils import CURRENT_SITE

import urlparse

register = template.Library()

import logging
logger = logging.getLogger('django.request')

def _DOMAIN_WITH_END_SLASH():
    _CURRENT_SITE = CURRENT_SITE()
    return _CURRENT_SITE.domain if _CURRENT_SITE.domain[-1] == '/' else '%s/' % _CURRENT_SITE.domain

@register.simple_tag
def admin_url_for(instance):
    content_type = ContentType.objects.get(model=instance._meta.model.__name__.lower())
    return reverse('admin:{app_name}_{model_name}_change'.format(app_name=content_type.app_label, model_name=content_type.model), args=(instance.pk,))


@register.simple_tag
def ABSOLUTE_BASE_URL(path=None):
    """
    Return the full current site domain with optional path appended
    ABSOLUTE_BASE_URL()
        returns: Site.domain http://example.com/

    ABSOLUTE_BASE_URL(path='/my/path/specified.html')
        returns: http://example.com/my/path/specified.html
    """
    return urlparse.urljoin(_DOMAIN_WITH_END_SLASH(), path)
ABSOLUTE_BASE_URL.is_safe = True


@register.simple_tag
def ABSOLUTE_STATIC_URL(path=None):
    """
    Return the full current site domain with {{ STATIC_URL }}
    ABSOLUTE_STATIC_URL()
        returns: http://example.com/static/

    ABSOLUTE_STATIC_URL(path='/my/path/specified.css')
        returns: http://example.com/static/my/path/specified.css
    """
    if path is not None:
        path = path if settings.STATIC_URL in path else '%s%s' % (settings.STATIC_URL, path)
    return urlparse.urljoin(_DOMAIN_WITH_END_SLASH(), path)
ABSOLUTE_STATIC_URL.is_safe = True


@register.simple_tag
def ABSOLUTE_MEDIA_URL(path=None):
    """
    Return the full current site domain with {{ MEDIA_URL }}
    ABSOLUTE_MEDIA_URL()
        returns: http://example.com/media/

    ABSOLUTE_MEDIA_URL(path='/my/path/specified.jpg')
        returns: http://example.com/media/my/path/specified.jpg
    """
    if path is not None:
        path = path if settings.MEDIA_URL in path else '%s%s' % (settings.MEDIA_URL, path)
    return urlparse.urljoin(_DOMAIN_WITH_END_SLASH(), path)
ABSOLUTE_MEDIA_URL.is_safe = True


@register.inclusion_tag('partials/firstseen.html', takes_context=True)
def firstseen(context):
    return {
        'PROJECT_ENVIRONMENT': settings.PROJECT_ENVIRONMENT,
        'show': True if context['request'].GET.get('firstseen', '0') == '1' else False,
    }
