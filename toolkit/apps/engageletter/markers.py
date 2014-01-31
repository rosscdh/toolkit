# -*- coding: utf-8 -*-
from django.core.urlresolvers import reverse

from toolkit.apps.workspace.markers import BaseSignalMarkers, Marker

from toolkit.apps.workspace.markers.lawyers import LawyerSetupTemplateMarker


class LawyerSetupTemplatePrerequisite(LawyerSetupTemplateMarker):
    def get_action_url(self):
        if self.is_complete is True:
            return None

        else:
            url = reverse('me:letterhead')
            tool_slug = self.workspace.tools.filter(slug='engagement-letters').first().slug
            next = reverse('workspace:tool_object_new', kwargs={'workspace': self.workspace.slug, 'tool': tool_slug})
            return '%s?next=%s' % (url, next)


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
        if self.tool:
            if self.tool.is_complete is True or self.tool.status > self.tool.STATUS.customer_complete_form:
                return None
            else:
                return self.get_action_url()
        return None


class LawyerReviewEngagementLetterMarker(Marker):
    name = 'lawyer_review_letter_text'
    description = 'Attorney: Review Engagement Letter Text'
    signals = ['toolkit.apps.engageletter.signals.lawyer_review_letter_text']

    action_name = 'Engagement Letter Text'
    action_type = Marker.ACTION_TYPE.redirect
    action_user_class = ['lawyer']

    def get_action_url(self):
        if self.tool is not None:
            return reverse('engageletter:lawyer_template', kwargs={'slug': self.tool.slug})
        return None


class LawyerInviteUserMarker(Marker):
    name = 'lawyer_invite_customer'
    description = 'Attorney: Invite client to complete & sign the Engagement Letter'
    signals = ['toolkit.apps.engageletter.signals.lawyer_invite_customer']

    action_type = Marker.ACTION_TYPE.redirect
    action_user_class = ['lawyer']

    @property
    def action_name(self):
        return 'Reinvite Client' if self.is_complete is True else 'Invite Client'

    def get_action_url(self):
        return reverse('workspace:tool_object_invite', kwargs={'workspace': self.tool.workspace.slug, 'tool': self.tool.tool_slug, 'slug': self.tool.slug})

    @property
    def action(self):
        if self.tool.is_complete is True or self.tool.status > self.tool.STATUS.customer_complete_form:
            return None
        else:
            return self.get_action_url()


class CustomerCompleteLetterFormMarker(Marker):
    name = 'customer_complete_form'
    description = 'Client: Complete Engagement Letter'
    signals = ['toolkit.apps.engageletter.signals.customer_complete_form']

    action_name = 'Complete Engagement Letter'
    action_type = Marker.ACTION_TYPE.redirect
    action_user_class = ['customer']

    def get_action_url(self):
        if self.tool is not None:
            return reverse('workspace:tool_object_edit', kwargs={'workspace': self.tool.workspace.slug, 'tool': self.tool.tool_slug, 'slug': self.tool.slug})
        return None

    @property
    def action(self):
        if self.tool:
            if self.tool.is_complete is True or self.tool.status > self.tool.STATUS.customer_complete_form:
                return None
            else:
                return self.get_action_url()
        return None


class CustomerSignAndSendMarker(Marker):
    name = 'customer_sign_and_send'
    description = 'Client: Sign the Engagement Letter'
    signals = ['toolkit.apps.engageletter.signals.customer_sign_and_send']

    action_name = 'Sign Engagment Letter'
    action_type = Marker.ACTION_TYPE.redirect
    action_user_class = ['customer']

    def get_action_url(self):
        return reverse('engageletter:sign', kwargs={'slug': self.tool.slug})

    @property
    def action(self):
        if self.tool:
            if self.tool.status == self.tool.STATUS.customer_sign_and_send:
                return self.get_action_url()
        return None


class LawyerSignMarker(Marker):
    name = 'lawyer_sign'
    description = 'Attorney: Sign the Engagement Letter'
    signals = ['toolkit.apps.engageletter.signals.customer_sign_and_send']

    action_name = 'Sign & Confirm Engagment Letter'
    action_type = Marker.ACTION_TYPE.redirect
    action_user_class = ['lawyer']

    def get_action_url(self):
        if self.tool is not None:
            return self.tool.signing_url

    @property
    def action(self):
        if self.tool:
            if self.tool.status == self.tool.STATUS.lawyer_sign:
                return self.get_action_url()
        return None


class ProcessCompleteMarker(Marker):
    name = 'complete'
    description = 'Process Complete'
    signals = ['toolkit.apps.engageletter.signals.complete']


class EngagementLetterMarkers(BaseSignalMarkers):
    prerequisite_signal_map = [
        LawyerSetupTemplatePrerequisite,
    ]
    signal_map = [
        LawyerCreateLetterMarker(1),
        LawyerReviewEngagementLetterMarker(2),
        LawyerInviteUserMarker(3),
        CustomerCompleteLetterFormMarker(4),
        CustomerSignAndSendMarker(5),
        LawyerSignMarker(6),
        ProcessCompleteMarker(7)
    ]
