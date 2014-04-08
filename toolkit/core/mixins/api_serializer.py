# -*- coding: utf-8 -*-
from toolkit.utils import _class_importer


class ApiSerializerMixin(object):
    """
    Mixin to provide access to model serializer
    """
    _serializer = None

    def api_serializer(self, instance, context={'request': None}):
        if type(self._serializer) in [str, unicode]:
            # not imported yet
            self._serializer = _class_importer(self._serializer)
        return self._serializer(instance, context=context)