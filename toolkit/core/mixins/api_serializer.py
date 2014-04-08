# -*- coding: utf-8 -*-
from toolkit.utils import _class_importer


class ApiSerializerMixin(object):
    """
    Mixin to provide access to model serializer
    """
    _serializer = None

    def api_serializer(self, instance, context={'request': None}):
        if type(self.__class__._serializer) in [str, unicode]:
            # not imported yet
            self.__class__._serializer = _class_importer(self.__class__._serializer)

        return self.__class__._serializer(instance, context=context)