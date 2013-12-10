# -*- coding: utf-8 -*-


class StatusMixin(object):
    @property
    def current_status(self):
        return self.STATUS_83b.get_desc_by_value(self.status)

    def current_markers(self):
        return self.data.get('markers')

    def next_status_step(self):
        return None

    def prev_status_step(self):
        return None
