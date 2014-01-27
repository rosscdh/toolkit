# -*- coding: utf-8 -*-
from django.core.urlresolvers import reverse

from . import Marker, Prerequisite


class LawyerSetupTemplateMarker(Prerequisite):
    """
    @SHARED marker for lawyers to enter their header, logo, footer info
    """
    name = 'lawyer_setup_template'
    description = 'Attorney: Setup Letter Template'
    signals = ['toolkit.apps.engageletter.signals.lawyer_setup_template']

    action_name = 'Edit Engagement Letter Template'
    action_type = Marker.ACTION_TYPE.redirect
    action_user_class = ['lawyer']

    # specific to this marker only
    required_data_markers = ['firm_address', 'firm_logo']

    @property
    def is_complete(self):
        """
        is complete is evaluated against the LAWYER profile.data value and
        not the normal test against the tool.data
        self.workspace is ALWAYS present with prerequisistes
        """
        data = self.workspace.lawyer.profile.data
        return all([True if key in data and data[key] not in ['', None] else False for key in self.required_data_markers])

    def get_action_url(self):
        url = reverse('me:letterhead')

        if self.is_complete is True:
            return None
        else:
            return url 