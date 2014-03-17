# -*- coding: utf-8 -*-
from toolkit.mailers import BaseMailerService


class RequestedDocumentReminderEmail(BaseMailerService):
    """
    m = RequestedDocumentReminderEmail(recipients=(('Alex', 'alex@lawpal.com'),))
    m.process(subject='[ACTION REQUIRED] Request to provide a document', action_url='http://lawpal.com/etc/')
    """
    subject = '[ACTION REQUIRED] Request to provide a document'
    email_template = 'provide_document_reminder'


class SignatoryReminderEmail(BaseMailerService):
    """
    m = SignatoryReminderEmail(recipients=(('Alex', 'alex@lawpal.com')))
    m.process(subject='[ACTION REQUIRED] Reminder to sign', action_url='http://lawpal.com/etc/')
    """
    name = 'Signatory Reminder Email'
    email_template = 'signatory_reminder'
