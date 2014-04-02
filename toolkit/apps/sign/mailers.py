# -*- coding: utf-8 -*-
from toolkit.mailers import BaseMailerService


class SignerReminderEmail(BaseMailerService):
    """
    m = SignerReminderEmail(recipients=(('Alex', 'alex@lawpal.com'),))
    m.process(subject='[ACTION REQUIRED] Reminder to sign', action_url='http://lawpal.com/etc/')
    """
    name = 'Signer Reminder Email'
    subject = '[ACTION REQUIRED] Invitation to sign a document'
    email_template = 'sign_reminder'