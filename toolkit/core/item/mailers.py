# -*- coding: utf-8 -*-
from toolkit.mailers import BaseMailerService


class SignatoryReminderEmail(BaseMailerService):
    """
    m = SignatoryReminderEmail(recipients=(('Alex', 'alex@lawpal.com')))
    m.process(subject='[ACTION REQUIRED] Reminder to sign', action_url='http://lawpal.com/etc/')
    """
    name = 'Signatory Reminder Email'
    email_template = 'signatory_reminder'
