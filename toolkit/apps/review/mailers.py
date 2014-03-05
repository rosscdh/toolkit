# -*- coding: utf-8 -*-
from toolkit.mailers import BaseMailerService


class ReviewerReminderEmail(BaseMailerService):
    """
    m = ReviewerReminderEmail(recipients=(('Alex', 'alex@lawpal.com'),))
    m.process(subject='[ACTION REQUIRED] Reminder to review', action_url='http://lawpal.com/etc/')
    """
    name = 'Reviewer Reminder Email'
    subject = '[ACTION REQUIRED] Invitation to review a document'
    email_template = 'reviewer_reminder'