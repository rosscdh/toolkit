# -*- coding: utf-8 -*-
from django.conf import settings

from toolkit.apps.workspace.models import Workspace
from toolkit.core.item.models import Item


def EXPOSED_GLOBALS(request):
    return {
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
            'PUSHER_KEY': settings.PUSHER_KEY,
        }
    }


def LAYOUT(request):
    user = getattr(request, 'user', None)
    profile = getattr(user, 'profile', None)

    return {
        'LAYOUT': u'%s.html' % profile.user_class if profile else 'base.html'
    }


def WORKSPACES(request):
    return {
        'WORKSPACES': Workspace.objects.mine(request.user)
    }
