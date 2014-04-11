# -*- coding: utf-8 -*-
from toolkit.mailers import BaseMailerService


class ReviewerReminderEmail(BaseMailerService):
    """
    m = ReviewerReminderEmail(recipients=(('Alex', 'alex@lawpal.com'),), from_tuple=(from_user.get_full_name(), from_user.email,))
    m.process(subject='[ACTION REQUIRED] Reminder to review', action_url='http://lawpal.com/etc/')
    """
    subject = '[ACTION REQUIRED] Invitation to review a document'
    email_template = 'reviewer_reminder'