# -*- coding: utf-8 -*-
from django.conf import settings


def EXPOSED_SETTINGS(request):
    return {
        'SHORT_DATE_FORMAT': settings.SHORT_DATE_FORMAT.lower()
    }