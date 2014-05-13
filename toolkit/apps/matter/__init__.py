# -*- coding: UTF-8 -*-
from django.conf import settings


MATTER_EXPORT_DAYS_VALID = getattr(settings, 'MATTER_EXPORT_DAYS_VALID', 3)