# -*- coding: utf-8 -*-
from collections import OrderedDict

from toolkit.apps.workspace.mixins.categories import InvalidCategoryValue
from toolkit.core.attachment.models import Revision


class RevisionLabelMixin(object):
    """
    Mixin to allow changing the status names of revisions (and getting them)
    """
    @property
    def status_labels(self):
        """
        Get the set of closing groups
        """
        result = self.data.get('status_labels', False)

        if result in (False, {}):
            return Revision.REVISION_STATUS.get_choices_dict()
        return result

    @status_labels.setter
    def status_labels(self, value):
        """
        Set the status names as a dict
        """
        if type(value) != dict:
            raise InvalidCategoryValue

        choices = OrderedDict()
        for k in sorted(value.keys()):
            choices[str(k)] = value[k]

        self.data['status_labels'] = choices