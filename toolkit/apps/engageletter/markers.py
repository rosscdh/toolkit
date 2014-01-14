# -*- coding: utf-8 -*-
from toolkit.apps.workspace.markers import BaseSignalMarkers, Marker


class LawyerSetupTemplateMarker(Marker):
    name = 'lawyer_setup_template'
    description = 'Attorney: Setup Engagement Letter Template'
    signals = ['toolkit.apps.engageletter.signals.lawyer_setup_template']

    action_name = 'Setup Engagement Letter Template'
    action_type = Marker.ACTION_TYPE.redirect
    action_user_class = ['lawyer']


class LawyerCreateLetterMarker(Marker):
    name = 'lawyer_complete_form'
    description = 'Attorney: Create Engagement Letter'
    signals = ['toolkit.apps.engageletter.signals.lawyer_complete_form']

    action_name = 'Create Engagement Letter'
    action_type = Marker.ACTION_TYPE.redirect
    action_user_class = ['lawyer']


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


class CustomerDownloadMarker(Marker):
    name = 'customer_download_letter'
    description = 'Client: Download Signed Engagement Letter'
    signals = ['toolkit.apps.engageletter.signals.customer_download_letter']

    action_name = 'Download Engagement Letter'
    action_type = Marker.ACTION_TYPE.redirect
    action_user_class = ['customer']


class LawyerDownloadMarker(Marker):
    name = 'lawyer_download_letter'
    description = 'Attorney: Download Signed Engagement Letter'
    signals = ['toolkit.apps.engageletter.signals.lawyer_download_letter']

    action_name = 'Download Engagement Letter'
    action_type = Marker.ACTION_TYPE.redirect
    action_user_class = ['lawyer']


class ProcessCompleteMarker(Marker):
    name = 'complete'
    description = 'Process Complete'
    signals = ['toolkit.apps.engageletter.signals.complete']


class EngagementLetterSignalMarkers(BaseSignalMarkers):
    signal_map = [
        LawyerSetupTemplateMarker(0),
        LawyerCreateLetterMarker(1),
        LawyerInviteUserMarker(2),
        CustomerCompleteLetterFormMarker(3),
        CustomerSignAndSendMarker(4),
        CustomerDownloadMarker(5),
        LawyerDownloadMarker(6),
        ProcessCompleteMarker(7)
    ]
