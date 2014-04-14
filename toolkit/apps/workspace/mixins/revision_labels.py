# -*- coding: utf-8 -*-
from toolkit.utils import _class_importer
from collections import OrderedDict


class RevisionLabelMixin(object):
    """
    Mixin to allow changing the status names of revisions (and getting them)
    """
    _revision_class = 'toolkit.core.attachment.models.Revision'

    @property
    def status_labels(self):
        if type(self.__class__._revision_class) in [str, unicode]:
            self.__class__._revision_class = _class_importer(self.__class__._revision_class)

        return self.data.get('status_labels', self.__class__._revision_class.REVISION_STATUS.get_choices_dict())

    @status_labels.setter
    def status_labels(self, value):
        if type(value) != dict:
            raise Exception('status labels must be of type dict')

        choices = OrderedDict()
        for k in sorted(value.keys()):
            choices[k] = value[k]

        self.data['status_labels'] = choices

    @property
    def default_status_index(self):
        default_index = 0
        #
        # Get the actual default index; in case the user deletes all indexes
        # except index 3 then 3 should be the default
        #
        for index, value in self.status_labels.iteritems():
            if value not in [None, '']:
                default_index = index
                break

        return default_index

    @property
    def default_status(self):
        return self.status_labels[self.default_status_index]
