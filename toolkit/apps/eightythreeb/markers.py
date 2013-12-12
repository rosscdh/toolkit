# -*- coding: utf-8 -*-
from django.core.urlresolvers import reverse

from toolkit.apps.workspace.markers import BaseSignalMarkers, Marker

class EditFormMarker(Marker):
    action_user_class = ['lawyer', 'customer']

    def action_url(self):
        if self.tool.is_complete is True or self.tool.status < self.val:
            return None
        else:
            return reverse('workspace:tool_object_edit', kwargs={'workspace': self.tool.workspace.slug, 'tool': self.tool.tool_slug, 'slug': self.tool.slug})


class LawyerInviteUserMarker(Marker):
    action_user_class = ['lawyer',]

    def action_name(self):
        return 'Re-invite Client' if self.is_complete is True else 'Invite Client'

    def action_url(self):
        return reverse('workspace:tool_object_invite', kwargs={'workspace': self.tool.workspace.slug, 'tool': self.tool.tool_slug, 'slug': self.tool.slug})


class CustomerDownloadDocMarker(Marker):
    action_name = 'Download PDF'
    action_user_class = ['customer', 'lawyer',]

    def action_url(self):
        """
        Always allow download no rules applied
        """
        return reverse('workspace:tool_object_download', kwargs={'workspace': self.tool.workspace.slug, 'tool': self.tool.tool_slug, 'slug': self.tool.slug})


class CustomerTrackingNumberMarker(Marker):
    action_name = 'Enter Tracking Number'
    action_user_class = ['customer', 'lawyer']

    def action_url(self):
        # Dont allow the tracking number to be updated if we have the tracking number in the data and the status is greater than
        if self.tool.is_complete is True or self.tool.status < self.val:
            return None
        else:
            return reverse('eightythreeb:tracking_code', kwargs={'slug': self.tool.slug})


class EightyThreeBSignalMarkers(BaseSignalMarkers):
    signal_map = [
        # Have taken out the "edit form marker", i don't think we want them to be able to do this. Will check. 
        Marker(0, 'lawyer_complete_form', '[Attorney] Setup 83b Election Letter', signals=['toolkit.apps.eightythreeb.signals.lawyer_complete_form'], next=None, previous=None),
        LawyerInviteUserMarker(1, 'lawyer_invite_customer', '[Attorney] Invite client to complete the 83b Election Letter', signals=['toolkit.apps.eightythreeb.signals.lawyer_invite_customer'], next=None, previous=None),
        Marker(2, 'customer_complete_form', '[Client] Complete 83b Election Letter', signals=['toolkit.apps.eightythreeb.signals.customer_complete_form'], next=None, previous=None),
        CustomerDownloadDocMarker(3, 'customer_download_pdf', '[Client] Download 83b Election Letter and Instructions', long_description='Customer should download the 83b form.', signals=['toolkit.apps.eightythreeb.signals.customer_download_pdf'], next=None, previous=None),
        Marker(4, 'customer_print_and_sign', '[Client] Print, check and sign 83b Election Letter', long_description='Customer is to print and sign 2 copies, plus a 3rd for their own records', signals=['toolkit.apps.eightythreeb.signals.customer_print_and_sign'], next=None, previous=None),
        CustomerTrackingNumberMarker(5, 'mail_to_irs_tracking_code', '[Client] Mail to IRS & register Tracking Code', long_description='Customer mail 83b form using USPS Registered Post *ONLY* and enter the Tracking Number here', signals=['toolkit.apps.eightythreeb.signals.mail_to_irs_tracking_code'], next=None, previous=None),
        Marker(6, 'irs_recieved', 'Waiting for reciept of 83b by IRS (via USPS)', signals=['toolkit.apps.eightythreeb.signals.irs_recieved'], next=None, previous=None),
        Marker(7, 'datestamped_copy_recieved', '[Client] Date stamped copy received', signals=['toolkit.apps.eightythreeb.signals.datestamped_copy_recieved'], next=None, previous=None),
        Marker(8, 'copy_sent_to_lawyer', 'Customer to send copy of date-stamped doc to Attorney', signals=['toolkit.apps.eightythreeb.signals.copy_sent_to_lawyer'], next=None, previous=None),
        Marker(9, 'copy_sent_to_accountant', 'Customer to send copy of date-stamped doc to Accountant', signals=['toolkit.apps.eightythreeb.signals.copy_sent_to_accountant'], next=None, previous=None),
        Marker(10, 'complete', 'Process Complete', signals=['toolkit.apps.eightythreeb.signals.complete'], next=None, previous=None)
    ]