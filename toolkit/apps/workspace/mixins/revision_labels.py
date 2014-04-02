# -*- coding: utf-8 -*-
from collections import OrderedDict
from toolkit.core.attachment.models import Revision


class RevisionLabelMixin(object):
    """
    Mixin to allow changing the status names of revisions (and getting them)
    """
    @property
    def status_labels(self):
        return self.data.get('status_labels', OrderedDict())

    @status_labels.setter
    def status_labels(self, value):
        if type(value) != dict:
            raise Exception('status labels must be of type dict')

        choices = OrderedDict()
        for k in sorted(value.keys()):
            choices[k] = value[k]
        self.data['status_labels'] = choices