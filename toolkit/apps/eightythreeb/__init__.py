# -*- coding: utf-8 -*-
from toolkit.utils import get_namedtuple_choices

EIGHTYTHREEB_STATUS = get_namedtuple_choices('EIGHTYTHREEB_STATUS', (
    (0, 'LAWYER_COMPLETE_FORM', 'Attorney to complete 83b Form'),  # attorney - default status when the form is initialized
    (1, 'CUSTOMER_COMPLETE_FORM', 'Customer to complete 83b Form'),  # customer - changed to when attorney invites customer
    (2, 'CUSTOMER_PRINT_AND_SIGN', 'Print and sign 83b Election Form'), # customer - changed to when the customer completes the form
    (3, 'MAIL_TO_IRS', 'Mail to IRS & register Tracking Code'),  # customer; collect usps registration code here - changed to after user indicates they have printed and signed the form
    (4, 'IRS_RECIEVED', 'Recieved by IRS'),  # webhook callback/cron to query usps for this status
    (5, 'DATESTAMPPED_COPY_RECIEVED', 'Date stamped copy received'),  # attorney/customer - attorney/customer indicates they recieved the copy (may need to upload scan?)
    (6, 'COPY_SENT_TO_COMPANY', 'Copy sent to company'), # attorney/customer sends copy to company (? depending on 5.)
    (7, 'COPY_SENT_TO_ACCOUNTANT', 'Copy sent to accountant'), # attorney/customer sends copy to accountant (?)
))