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

def WORKSPACES(request):
    return {
        'WORKSPACES': Workspace.objects.filter(participants__in=[request.user]) if request.user.is_authenticated() is True else []
    }
