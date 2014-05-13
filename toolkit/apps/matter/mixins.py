# -*- coding: utf-8 -*-
from django.utils.timezone import utc
from dateutil.parser import parse as dateutil_parse

import datetime


def _ensure_utc(date):
    return dateutil_parse(date).replace(tzinfo=utc)  # ensure is utc


class MatterExportMixin(object):
    """
    Mixin that provides Matter export info
    """
    def export_matter(self, requested_by):
        from toolkit.tasks import run_task
        from toolkit.apps.matter.tasks import _export_matter

        #
        # Reset Pending Export
        #
        export_info = self.export_info
        export_info.update({
            'is_pending_export': True,
            'last_export_requested': datetime.datetime.utcnow().isoformat(),
            'last_export_requested_by': requested_by.get_full_name(),
        })
        self.save(update_fields=['data'])

        # start the process
        run_task(_export_matter, matter=self, requested_by=requested_by)
        # record the event
        self.actions.started_matter_export(user=requested_by)

    @property
    def export_info(self):
        data = self.data.get('export', {
            'is_pending_export': False,
            'last_exported': None,
            'last_exported_by': None,
            'last_export_requested': None,
            'last_export_requested_by': None,
            'download_valid_until': None,
            'download_url': None,
        })
        if type(data.get('last_exported')) in [str, unicode]:
            data['last_exported'] = _ensure_utc(data['last_exported'])

        if type(data.get('last_export_requested')) in [str, unicode]:
            data['last_export_requested'] = _ensure_utc(data['last_export_requested'])

        if type(data.get('download_valid_until')) in [str, unicode]:
            data['download_valid_until'] = _ensure_utc(data['download_valid_until'])

        return data

    @export_info.setter
    def export_info(self, value):
        if type(value) not in [dict]:
            raise Exception('export_info must be dict')
        self.data['export'] = value

    @property
    def is_pending_export(self):
        return self.export_info.get('is_pending_export')

    @is_pending_export.setter
    def is_pending_export(self, value):
        if type(value) not in [bool]:
            raise Exception('is_pending_export must be Boolean')
        data = self.export_info
        data.update({'is_pending_export': value})
        self.export_info = data
