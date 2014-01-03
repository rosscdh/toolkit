# -*- coding: utf-8 -*-
from django.core.urlresolvers import reverse
from django.utils.safestring import mark_safe

from toolkit.apps.workspace.markers import BaseSignalMarkers, Marker


class LawyerCompleteFormMarker(Marker):
    name = 'lawyer_complete_form'
    description = 'Attorney: Setup 83(b) Election Letter'
    signals = ['toolkit.apps.eightythreeb.signals.lawyer_complete_form']

    action_name = 'Setup 83(b)'
    action_type = Marker.ACTION_TYPE_REDIRECT
    action_user_class = ['lawyer']

    def get_action_url(self):
        return reverse('workspace:tool_object_edit', kwargs={'workspace': self.tool.workspace.slug, 'tool': self.tool.tool_slug, 'slug': self.tool.slug})

    @property
    def action(self):
        if self.tool.is_complete is True or self.tool.status > self.val:
            return None
        else:
            return self.get_action_url()


class LawyerInviteUserMarker(Marker):
    name = 'lawyer_invite_customer'
    description = 'Attorney: Invite client to complete the 83(b) Election Letter'
    signals = ['toolkit.apps.eightythreeb.signals.lawyer_invite_customer']

    action_name = 'Invite Client'
    action_type = Marker.ACTION_TYPE_REDIRECT
    action_user_class = ['lawyer']

    @property
    def action_name(self):
        return 'Reinvite Client' if self.is_complete is True else 'Invite Client'

    def get_action_url(self):
        return reverse('workspace:tool_object_invite', kwargs={'workspace': self.tool.workspace.slug, 'tool': self.tool.tool_slug, 'slug': self.tool.slug})

    @property
    def action(self):
        if self.tool.is_complete is True or self.tool.status > self.tool.STATUS_83b.customer_complete_form:
            return None
        else:
            return self.get_action_url()


class CustomerCompleteFormMarker(Marker):
    name = 'customer_complete_form'
    description = 'Client: Complete 83(b) Election Letter'
    signals = ['toolkit.apps.eightythreeb.signals.customer_complete_form']

    action_name = 'Complete 83(b)'
    action_type = Marker.ACTION_TYPE_REDIRECT
    action_user_class = ['customer']

    def get_action_url(self):
        return reverse('workspace:tool_object_edit', kwargs={'workspace': self.tool.workspace.slug, 'tool': self.tool.tool_slug, 'slug': self.tool.slug})

    @property
    def action(self):
        if self.tool.is_complete is True or self.tool.status > self.val:
            return None
        else:
            return self.get_action_url()


class CustomerDownloadDocMarker(Marker):
    name = 'customer_download_pdf'
    description = 'Client: Download 83(b) Election Letter and Instructions'
    long_description = ''
    signals = ['toolkit.apps.eightythreeb.signals.customer_download_pdf']

    action_name = 'Download 83(b)'
    action_type = Marker.ACTION_TYPE_REDIRECT
    action_user_class = ['customer']

    def get_action_url(self):
        return reverse('workspace:tool_object_download', kwargs={'workspace': self.tool.workspace.slug, 'tool': self.tool.tool_slug, 'slug': self.tool.slug})

    @property
    def action(self):
        if self.tool.is_complete is True or self.tool.status > self.val:
            return None
        else:
            return self.get_action_url()


class CustomerPrintAndSignMarker(Marker):
    name = 'customer_print_and_sign'
    description = 'Client: Print, check and sign 83(b) Election Letter'
    long_description = 'Print and sign the 83(b) Election where indicated.'
    signals = ['toolkit.apps.eightythreeb.signals.customer_print_and_sign']

    action_name = 'I have printed and signed the Election'
    action_type = Marker.ACTION_TYPE_REMOTE
    action_user_class = ['customer']

    @property
    def action_attribs(self):
        return {
            'method': 'PATCH',
            'status': self.val,
            'tool': self.tool.tool_slug,
            'tool_object_id': self.tool.pk
        }

    def get_action_url(self):
        return u'/api/83b/%s' % self.tool.pk  # Modify this to come from reverse

    @property
    def action(self):
        if self.tool.is_complete is True or self.tool.status > self.val:
            return None
        else:
            return self.get_action_url()


class CustomerUploadScanMarker(Marker):
    name = 'copy_uploaded'
    description = 'Client: Scan and upload signed copy'
    signals = ['toolkit.apps.eightythreeb.signals.copy_uploaded']

    action_type = Marker.ACTION_TYPE_REDIRECT
    action_user_class = ['customer',]

    @property
    def action_name(self):
        return 'Re-upload Attachment' if self.is_complete is True else 'Upload Attachment'

    def get_action_url(self):
        return reverse('eightythreeb:attachment', kwargs={'slug': self.tool.slug})

    @property
    def action(self):
        if self.tool.status >= self.tool.STATUS_83b.copy_uploaded and self.tool.status <= self.tool.STATUS_83b.mail_to_irs_tracking_code:
            return self.get_action_url()
        else:
            return None

    @property
    def is_complete(self):
        if self.tool is not None:
            return self.tool.attachment_set.all().count() > 0 and self.name in self.tool.data['markers']
        return False

    @property
    def long_description(self):
        msg = None

        if self.tool.attachment_set.all().first().url is not None:
            msg = mark_safe('You have successfully uploaded a scan of your 83b, <a target="_BLANK" href="%s">click here</a> to view it' % self.tool.attachment.url)

        return msg


class CustomerTrackingNumberMarker(Marker):
    name = 'mail_to_irs_tracking_code'
    description = 'Client: Mail to IRS & register Tracking Code'
    long_description = 'Mail 83(b) form using USPS Registered Post *ONLY* and enter the Tracking Number here,'
    signals = ['toolkit.apps.eightythreeb.signals.mail_to_irs_tracking_code']

    action_name = 'Enter Tracking Number'
    action_type = Marker.ACTION_TYPE_REDIRECT
    action_user_class = ['customer', 'lawyer']

    def get_action_url(self):
        reverse('eightythreeb:tracking_code', kwargs={'slug': self.tool.slug})

    @property
    def action(self):
        if self.tool.is_complete is True or self.tool.status > self.val:
            return None
        else:
            return self.get_action_url()


class USPSDeliveryStatusMarker(Marker):
    name = 'irs_recieved'
    signals = ['toolkit.apps.eightythreeb.signals.irs_recieved']

    @property
    def description(self):
        if self.tool and self.tool.tracking_code is not None:
            return 'Waiting for reciept of 83(b) by IRS (via USPS) for %s' % self.tool.tracking_code
        else:
            return 'Waiting for reciept of 83(b) by IRS (via USPS)'

    @property
    def long_description(self):
        msg = self.tool.usps_current_status

        if msg is not None:
            msg = 'Current Status: %s' % msg
        else:
            msg = 'Pending USPS response'

        return msg


class DateStampedCopyRecievedMarker(Marker):
    name = 'datestamped_copy_recieved'
    description = 'Client: Date-stamped copy received'
    long_description = 'Customer is to print and sign 2 copies, plus a 3rd for their own records.'
    signals = ['toolkit.apps.eightythreeb.signals.datestamped_copy_recieved']

    action_name = 'I have recieved the date-stamped copy back from the IRS'
    action_type = Marker.ACTION_TYPE_REMOTE
    action_user_class = ['customer']

    @property
    def action_attribs(self):
        return {
            'method': 'PATCH',
            'status': self.val,
            'tool': self.tool.tool_slug,
            'tool_object_id': self.tool.pk
        }

    def get_action_url(self):
        return u'/api/83b/%s' % self.tool.pk  # Modify this to come from reverse

    @property
    def action(self):
        if self.tool.is_complete is True or self.tool.status > self.val:
            return None
        else:
            return self.get_action_url()


class ProcessCompleteMarker(Marker):
    name = 'complete'
    description = 'Process Complete'
    signals = ['toolkit.apps.eightythreeb.signals.complete']


class EightyThreeBSignalMarkers(BaseSignalMarkers):
    signal_map = [
        # Have taken out the "edit form marker", i don't think we want them to be able to do this. Will check.
        LawyerCompleteFormMarker(0),
        LawyerInviteUserMarker(1),
        CustomerCompleteFormMarker(2),
        CustomerDownloadDocMarker(3),
        CustomerPrintAndSignMarker(4),
        CustomerUploadScanMarker(5),
        CustomerTrackingNumberMarker(6),
        USPSDeliveryStatusMarker(7),
        DateStampedCopyRecievedMarker(8),
        ProcessCompleteMarker(9)
    ]
