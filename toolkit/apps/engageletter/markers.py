# -*- coding: utf-8 -*-
from django.core.urlresolvers import reverse_lazy

from toolkit.apps.workspace.markers import BaseSignalMarkers, Marker
from toolkit.apps.workspace.markers.lawyers import LawyerSetupTemplateMarker


class LawyerCreateLetterMarker(Marker):
    name = 'lawyer_complete_form'
    description = 'Attorney: Create Engagement Letter'
    signals = ['toolkit.apps.engageletter.signals.lawyer_complete_form']

    action_name = 'Create Engagement Letter'
    action_type = Marker.ACTION_TYPE.redirect
    action_user_class = ['lawyer']

    def get_action_url(self):
        # we dont have access to the workspace or tool from here
        return None  # must return None here to ensure the default create tool is called

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
