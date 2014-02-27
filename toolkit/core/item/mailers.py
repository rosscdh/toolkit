# -*- coding: utf-8 -*-
from toolkit.mailers import BaseMailerService


class ReviewerReminderEmail(BaseMailerService):
    """
    m = ReviewerReminderEmail(recipients=(('Alex', 'alex@lawpal.com')))
    m.process(subject='[ACTION REQUIRED] Reminder to review', action_url='http://lawpal.com/etc/')
    """
    name = 'Reviewer Reminder Email'
    email_template = 'reviewer_reminder'


class SignatoryReminderEmail(BaseMailerService):
    """
    m = SignatoryReminderEmail(recipients=(('Alex', 'alex@lawpal.com')))
    m.process(subject='[ACTION REQUIRED] Reminder to sign', action_url='http://lawpal.com/etc/')
    """
    name = 'Signatory Reminder Email'
    email_template = 'signatory_reminder'
