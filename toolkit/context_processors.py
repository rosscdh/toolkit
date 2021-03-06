# -*- coding: utf-8 -*-
from django.conf import settings

from toolkit.apps.workspace.models import Workspace


def EXPOSED_GLOBALS(request):
    return {
        'DEBUG': settings.DEBUG,
        'PROJECT_ENVIRONMENT': settings.PROJECT_ENVIRONMENT,

        # @TODO remove this GLOBALS as its totally not necessary as a context processor
        # context processors ARE template globals by definition
        'GLOBALS': {
            'DATE_FORMAT': settings.DATE_FORMAT,
            'JS_DATE_FORMAT': settings.JS_DATE_FORMAT,

            'SHORT_DATE_FORMAT': settings.SHORT_DATE_FORMAT,
            'JS_SHORT_DATE_FORMAT': settings.JS_SHORT_DATE_FORMAT,

            'FILEPICKER_API_KEY': settings.FILEPICKER_API_KEY,
            'HELLOSIGN_CLIENT_ID': settings.HELLOSIGN_CLIENT_ID,
            'INTERCOM_APP_ID': settings.INTERCOM_APP_ID,
            'MIXPANEL_API_TOKEN': settings.MIXPANEL_SETTINGS['token'],
            'STRIPE_PUBLIC_KEY': settings.STRIPE_PUBLIC_KEY
        }
    }

def FIRSTSEEN(request):
    return {
        'firstseen': request.GET.get('firstseen', '0') == '1'
    }


def LAYOUT(request):
    user = getattr(request, 'user', None)
    profile = getattr(user, 'profile', None)

    return {
        'LAYOUT': u'%s.html' % profile.user_class if profile else 'base.html'
    }


def REQUESTS_COUNT(request):
    count = 0
    if request.user.is_authenticated():
       count = request.user.profile.open_requests if request.user.is_authenticated else 0

    return {
        'REQUESTS_COUNT': count,
    }


def WORKSPACES(request):
    return {
        'WORKSPACES': Workspace.objects.mine(request.user)
    }
