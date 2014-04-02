# -*- coding: utf-8 -*-
from collections import OrderedDict

from toolkit.core.attachment.models import Revision


class RevisionLabelMixin(object):
    """
    Mixin to allow changing the status names of revisions (and getting them)
    """
    @property
    def status_labels(self):
        """
        Get the set of status labels
        """
        choices = self.data.get('status_labels', {})

        if choices == {}:
            defaults = Revision.REVISION_STATUS.get_choices_dict()
            for k, v in defaults.items():
                choices[k] = {'is_active': True, 'label': v}
        # import pdb;pdb.set_trace()
        return choices

    @status_labels.setter
    def status_labels(self, value):
        if type(value) != dict:
            raise Exception('status labels must be of type dict')

        choices = OrderedDict()
        for k in sorted(value.keys()):
            choices[k] = value[k]

        self.data['status_labels'] = choices
