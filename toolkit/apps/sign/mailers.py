# -*- coding: utf-8 -*-
from toolkit.mailers import BaseMailerService


class SignerReminderEmail(BaseMailerService):
    """
    m = SignerReminderEmail(recipients=(('Alex', 'alex@lawpal.com'),), from_tuple=(from_user.get_full_name(), from_user.email,))
    m.process(subject='[ACTION REQUIRED] Reminder to sign', action_url='http://lawpal.com/etc/')
    """
    name = 'Signer Reminder Email'
    subject = '[ACTION REQUIRED] Invitation to sign a document'
    email_template = 'sign_reminder'