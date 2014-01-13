# -*- coding: utf-8 -*-
from django.utils import formats
from django.core.urlresolvers import reverse
from django.utils.safestring import mark_safe

from dateutil import parser

from toolkit.apps.workspace.markers import BaseSignalMarkers, Marker


class LawyerCompleteFormMarker(Marker):
    name = 'lawyer_complete_form'
    description = 'Attorney: Setup 83(b) Election Letter'
    signals = ['toolkit.apps.eightythreeb.signals.lawyer_complete_form']

    action_name = 'Setup 83(b)'
    action_type = Marker.ACTION_TYPE.modal
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
    action_type = Marker.ACTION_TYPE.redirect
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
    action_type = Marker.ACTION_TYPE.redirect
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
    """
    Relies on jquery plugin to detect successful download of document and reload page
    thus it must be Marker.ACTION_TYPE.redirect
    """
    name = 'customer_download_pdf'
    description = 'Client: Download 83(b) Election Letter and Instructions'
    _long_description = ''
    signals = ['toolkit.apps.eightythreeb.signals.customer_download_pdf']

    action_type = Marker.ACTION_TYPE.redirect
    action_user_class = ['customer']

    @property
    def action_name(self):
        return 'Re-download 83(b)' if self.is_complete is True else 'Download 83(b)'

    def get_action_url(self):
        return reverse('workspace:tool_object_download', kwargs={'workspace': self.tool.workspace.slug, 'tool': self.tool.tool_slug, 'slug': self.tool.slug})

    @property
    def action(self):
        if self.tool.status < self.val:
            return None
        else:
            return self.get_action_url()


class CustomerPrintAndSignMarker(Marker):
    name = 'customer_print_and_sign'
    description = 'Client: Print, check and sign 83(b) Election Letter'
    _long_description = 'Print and sign the 83(b) Election where indicated.'
    signals = ['toolkit.apps.eightythreeb.signals.customer_print_and_sign']

    action_name = 'I have printed and signed the Election'
    action_type = Marker.ACTION_TYPE.remote
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
        return reverse('api:eightythreeb-detail', kwargs={'pk': self.tool.pk})

    @property
    def action(self):
        if self.tool.status in [self.val]:
            return self.get_action_url()
        return None


class CustomerUploadScanMarker(Marker):
    name = 'copy_uploaded'
    description = 'Client: Scan and upload signed copy'
    signals = ['toolkit.apps.eightythreeb.signals.copy_uploaded']

    action_type = Marker.ACTION_TYPE.redirect
    action_user_class = ['customer',]

    @property
    def action_name(self):
        return 'Re-upload Attachment' if self.is_complete is True else 'Upload Attachment'

    def get_action_url(self):
        return reverse('eightythreeb:attachment', kwargs={'slug': self.tool.slug})

    @property
    def action(self):
        if self.tool.status in [self.val] or self.is_complete is False and self.tool.status > self.val:
            return self.get_action_url()
        return None

    @property
    def is_complete(self):
        if self.tool is not None:
            return self.tool.attachment_set.all().count() > 0 and self.name in self.tool.data['markers']
        return False

    @property
    def long_description(self):
        msg = None
        attachment = self.tool.attachment_set.all().first()
        if attachment is not None:
            msg = mark_safe('You have successfully uploaded a scan of your 83b, <a target="_BLANK" href="%s">click here</a> to view it' % attachment.url)

        return msg


class CustomerTrackingNumberMarker(Marker):
    name = 'mail_to_irs_tracking_code'
    description = 'Client: Mail to IRS & register Tracking Code'
    _long_description = 'Mail 83(b) form using USPS Registered Post *ONLY* and enter the Tracking Number here'
    signals = ['toolkit.apps.eightythreeb.signals.mail_to_irs_tracking_code']

    action_name = 'Enter Tracking Number'
    action_type = Marker.ACTION_TYPE.modal
    action_user_class = ['customer', 'lawyer']

    def get_action_url(self):
        return reverse('eightythreeb:tracking_code', kwargs={'slug': self.tool.slug})

    @property
    def action(self):
        if self.tool.status in [self.val, self.tool.STATUS_83b.irs_recieved]:  # allow them to change the number?
            if 'usps_log' not in self.tool.data:  # @BUSINESS_RULE only show the button as long as we have no usps_log
                return self.get_action_url()
        # dont show if the status is less than self.val
        return None


class CustomerValidTrackingNumberMarker(Marker):
    """
    When the customer enters a tracking number and it is validated as a real USPS tracking number
    we need to record this event and the datetime it happened so that it can act as a legal marker
    This marker gets fired in the TRackingNumberForm when the field is guaranteed to be clean
    because its been validated by the usps.validators.USPSTrackingCodeField
    """
    name = 'valid_usps_tracking_marker'
    description = 'Client: Has provided a valid USPS Tracking Code'
    _long_description = 'This marker will indicate the date a valid USPS Tracking Number was entered'
    signals = ['toolkit.apps.eightythreeb.signals.valid_usps_tracking_marker']

    action = None
    action_name = None
    action_type = None
    action_user_class = []

    def get_action_url(self):
        return None

    @property
    def long_description(self):
        marker_data = self.tool.data['markers'].get('valid_usps_tracking_marker')

        if marker_data is not None:
            entered_tracking_code = marker_data.get('tracking_code', None)

            if entered_tracking_code is not None:
                entered_date = parser.parse(marker_data.get('date_of'))
                entered_date = formats.date_format(entered_date, "SHORT_DATETIME_FORMAT")

                if self.tool and entered_tracking_code is not None:
                    return 'Tracking Code: %s Date Entered: %s' % (entered_tracking_code, entered_date)

        return self._long_description


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

        if msg in ['', None]:
            msg = 'Waiting for USPS response'

        return msg


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
        CustomerValidTrackingNumberMarker(50),
        USPSDeliveryStatusMarker(7),
        ProcessCompleteMarker(8)
    ]
