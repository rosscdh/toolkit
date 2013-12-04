# -*- coding: utf-8 -*-
from django.db import models

from . import EIGHTYTHREEB_STATUS


class StatusMixin(object):
    @staticmethod
    def choices():
        return EIGHTYTHREEB_STATUS.get_all()

    @property
    def current_status(self):
        return self.STATUS_83b.get_desc_by_value(self.status)

    def current_markers(self):
        return self.data.get('markers')

    def next_status_step(self):
        return None

    def prev_status_step(self):
        return None
