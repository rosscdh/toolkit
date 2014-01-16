# -*- coding: utf-8 -*-
from django.core.urlresolvers import reverse

from toolkit.apps.workspace.markers import BaseSignalMarkers, Marker
from toolkit.apps.workspace.markers.lawyers import LawyerSetupTemplateMarker


class LawyerCreateLetterMarker(Marker):
    name = 'lawyer_complete_form'
    description = 'Attorney: Create Engagement Letter'
    signals = ['toolkit.apps.engageletter.signals.lawyer_complete_form']

    action_type = Marker.ACTION_TYPE.redirect
    action_user_class = ['lawyer']

    @property
    def action_name(self):
        return 'Edit Engagement Letter' if self.is_complete is True else 'Create Engagement Letter'

    def get_action_url(self):
        if self.tool is not None:
            return reverse('workspace:tool_object_edit', kwargs={'workspace': self.tool.workspace.slug, 'tool': self.tool.tool_slug, 'slug': self.tool.slug})
        return None

    @property
    def action(self):
        if self.tool and (self.tool.is_complete is True or self.tool.status >= self.tool.STATUS.customer_complete_form):
            return None
        else:
            return self.get_action_url()


class LawyerInviteUserMarker(Marker):
    name = 'lawyer_invite_customer'
    description = 'Attorney: Invite client to complete & sign the Engagement Letter'
    signals = ['toolkit.apps.engageletter.signals.lawyer_invite_customer']

    action_name = 'Invite Client to Complete & Sign'
    action_type = Marker.ACTION_TYPE.redirect
    action_user_class = ['lawyer']


class CustomerCompleteLetterFormMarker(Marker):
    name = 'customer_complete_form'
    description = 'Client: Complete Engagement Letter'
    signals = ['toolkit.apps.engageletter.signals.customer_complete_form']

    action_name = 'Complete Engagement Letter'
    action_type = Marker.ACTION_TYPE.redirect
    action_user_class = ['customer']


class CustomerSignAndSendMarker(Marker):
    name = 'customer_sign_and_send'
    description = 'Client: Sign & Send the Engagement Letter'
    signals = ['toolkit.apps.engageletter.signals.customer_sign_and_send']

    action_name = 'Complete Engagement Letter'
    action_type = Marker.ACTION_TYPE.redirect
    action_user_class = ['customer']


class ProcessCompleteMarker(Marker):
    name = 'complete'
    description = 'Process Complete'
    signals = ['toolkit.apps.engageletter.signals.complete']


class EngagementLetterMarkers(BaseSignalMarkers):
    signal_map = [
        LawyerCreateLetterMarker(0),
        LawyerSetupTemplateMarker(1),
        LawyerInviteUserMarker(2),
        CustomerCompleteLetterFormMarker(3),
        CustomerSignAndSendMarker(4),
        ProcessCompleteMarker(5)
    ]
