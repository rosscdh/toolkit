# -*- coding: utf-8 -*-

from . import EIGHTYTHREEB_STATUS


class StatusMixin(object):
    @staticmethod
    def status_choices():
        return EIGHTYTHREEB_STATUS.get_choices()

    @property
    def current_status(self):
        return self.STATUS_83b.get_desc_by_value(self.status)

    def next_status_step(self):
        return None

    def prev_status_step(self):
        return None
