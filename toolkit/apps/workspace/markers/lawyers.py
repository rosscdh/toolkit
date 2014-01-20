# -*- coding: utf-8 -*-
from django.core.urlresolvers import reverse

from .base import Marker


class LawyerSetupTemplateMarker(Marker):
    """
    @SHARED marker for lawyers to enter their header, logo, footer info
    """
    name = 'lawyer_setup_template'
    description = 'Attorney: Setup Letter Template'
    signals = ['toolkit.apps.engageletter.signals.lawyer_setup_template']

    action_name = 'Setup Letter Template'
    action_type = Marker.ACTION_TYPE.redirect
    action_user_class = ['lawyer']

    # specific to this marker only
    required_markers = ['firm_address', 'firm_logo']

    @property
    def is_complete(self):
        """
        is complete is evaluated against the LAWYER profile.data value and
        not the normal test against the tool.data
        """
        if self.tool is not None:
            
            data = self.tool.workspace.lawyer.profile.data
            return all([True if key in data and data[key] not in ['', None] else False for key in self.required_markers])

        return False

    def get_action_url(self):
        return reverse('me:letterhead')