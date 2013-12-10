# -*- coding: utf-8 -*-
from toolkit.apps.workspace.markers import BaseSignalMarkers, Marker


class EightyThreeBSignalMarkers(BaseSignalMarkers):
    signal_map = [
        Marker(0, 'lawyer_complete_form', 'Attorney to complete 83b Form', signals=['toolkit.apps.eightythreeb.signals.lawyer_complete_form'], next=None, previous=None),
        Marker(1, 'lawyer_invite_customer', 'Attorney to invite customer to complete the 83b form', signals=['toolkit.apps.eightythreeb.signals.lawyer_invite_customer'], next=None, previous=None),
        Marker(2, 'customer_complete_form', 'Customer to complete 83b Form', signals=['toolkit.apps.eightythreeb.signals.customer_complete_form'], next=None, previous=None),
        Marker(3, 'customer_download_pdf', 'Customer to Download 83b Form', signals=['toolkit.apps.eightythreeb.signals.customer_download_pdf'], next=None, previous=None),
        Marker(4, 'customer_print_and_sign', 'Customer to Print and sign 83b Election Form', signals=['toolkit.apps.eightythreeb.signals.customer_print_and_sign'], next=None, previous=None),
        Marker(5, 'mail_to_irs_tracking_code', 'Customer to Mail to IRS & register Tracking Code', signals=['toolkit.apps.eightythreeb.signals.mail_to_irs_tracking_code'], next=None, previous=None),
        Marker(6, 'irs_recieved', 'Waiting for reciept of 83b by IRS (via USPS)', signals=['toolkit.apps.eightythreeb.signals.irs_recieved'], next=None, previous=None),
        Marker(7, 'datestamped_copy_recieved', 'Date stamped copy received by Customer', signals=['toolkit.apps.eightythreeb.signals.datestamped_copy_recieved'], next=None, previous=None),
        Marker(8, 'copy_sent_to_lawyer', 'Customer to send copy of date-stamped doc to Lawyer', signals=['toolkit.apps.eightythreeb.signals.copy_sent_to_lawyer'], next=None, previous=None),
        Marker(9, 'copy_sent_to_accountant', 'Customer to send copy of date-stamped doc to accountant', signals=['toolkit.apps.eightythreeb.signals.copy_sent_to_accountant'], next=None, previous=None),
        Marker(10, 'complete', 'Process Complete', signals=['toolkit.apps.eightythreeb.signals.complete'], next=None, previous=None)
    ]