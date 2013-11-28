# -*- coding: utf-8 -*-
from django.conf import settings

from toolkit.apps.workspace.models import Workspace


def EXPOSED_SETTINGS(request):
    return {
        'SHORT_DATE_FORMAT': settings.SHORT_DATE_FORMAT.lower()
    }

def WORKSPACES(request):
    return {
        'WORKSPACES': Workspace.objects.filter(participants__in=[request.user]) if request.user.is_authenticated() is True else []
    }