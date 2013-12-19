# -*- coding: utf-8 -*-
from django.conf import settings

from toolkit.apps.workspace.models import Workspace


def EXPOSED_GLOBALS(request):
    return {
        'GLOBALS': {
            'DATE_FORMAT': settings.DATE_FORMAT,
            'JS_DATE_FORMAT': settings.JS_DATE_FORMAT,

            'SHORT_DATE_FORMAT': settings.SHORT_DATE_FORMAT,
            'JS_SHORT_DATE_FORMAT': settings.JS_SHORT_DATE_FORMAT,
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
