# -*- coding: utf-8 -*-
from dateutil.parser import parse as dateutil_parse


class MatterExportMixin(object):
    """
    Mixin that provides Matter export info
    """
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
            data['last_exported'] = dateutil_parse(data['last_exported'])

        if type(data.get('last_export_requested')) in [str, unicode]:
            data['last_export_requested'] = dateutil_parse(data['last_export_requested'])

        if type(data.get('download_valid_until')) in [str, unicode]:
            data['download_valid_until'] = dateutil_parse(data['download_valid_until'])

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