# -*- coding: utf-8 -*-

class RequestDocumentUploadMixin(object):
    """
    Mixin to allow Item to act in requesting an upload from a user
    """
    @property
    def note(self):
        return self.data.get('request_document', {}).get('note', None)

    @note.setter
    def note(self, value):
        request_document = self.data.get('request_document', {})
        request_document.update({'note': value})

        self.data['request_document'] = request_document

    @property
    def requested_by(self):
        return self.data.get('request_document', {}).get('requested_by', None)

    @requested_by.setter
    def requested_by(self, value):
        request_document = self.data.get('request_document', {})
        request_document.update({'requested_by': value})

        self.data['request_document'] = request_document