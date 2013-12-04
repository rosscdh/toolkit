# -*- coding: utf-8 -*-
from toolkit.utils import get_namedtuple_choices

EIGHTYTHREEB_STATUS = get_namedtuple_choices('EIGHTYTHREEB_STATUS', (
    (0, 'lawyer_complete_form', 'Attorney to complete 83b Form'),  # attorney - default status when the form is initialized
    (1, 'lawyer_invite_customer', 'Attorney to invite customer to complete the 83b form'),  # attorney - needs to invite the customer
    (2, 'customer_complete_form', 'Customer to complete 83b Form'),  # customer - changed to when attorney invites customer
    (3, 'customer_print_and_sign', 'Customer to Print and sign 83b Election Form'),  # customer - changed to when the customer completes the form
    (4, 'mail_to_irs', 'Customer to Mail to IRS & register Tracking Code'),  # customer; collect usps registration code here - changed to after user indicates they have printed and signed the form
    (5, 'irs_recieved', 'Recieved by IRS'),  # webhook callback/cron to query usps for this status
    (6, 'datestampped_copy_recieved', 'Date stamped copy received by Customer'),  # attorney/customer - attorney/customer indicates they recieved the copy (may need to upload scan?)
    (7, 'copy_sent_to_lawyer', 'Customer to send copy of date-stamped doc to Lawyer'),  # attorney/customer sends copy to company (? depending on 5.)
    (8, 'copy_sent_to_accountant', 'Customer to send copy of date-stamped doc to accountant'),  # attorney/customer sends copy to accountant (?)
))
