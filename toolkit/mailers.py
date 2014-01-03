# -*- coding: utf-8 -*-
from django.conf import settings
from templated_email import send_templated_mail

import logging
LOGGER = logging.getLogger('django.request')


class BaseMailerService(object):
    email_template = None
    base_email_template_location = 'email/'
    user = {
        "name": None,
        "email": None
    }

    def __init__(self, recipients, from_tuple=None, subject=None, message=None, **kwargs):
        """
        subject : string
        message : string
        from_tuple : (:name, :email)
        recipients : ((:name, :email), (:name, :email),)
        """
        self.subject = subject
        self.message = message

        # if no from_tuple is provided simply use the defaults
        if from_tuple is None:
            from_tuple = settings.DEFAULT_FROM[0]

        self.from_tuple = self.user.copy()
        self.from_tuple.update({
            'name': from_tuple[0],
            'email': from_tuple[1],
        })

        self.recipients = []
        for r in recipients:
            u = self.user.copy()
            u.update({
                'name': r[0],
                'email': r[1]
            })
            self.recipients.append(u)

        assert self.email_template  # defined in inherited classes
        assert self.from_tuple
        assert type(self.from_tuple) is dict
        assert self.recipients
        assert type(self.recipients) is list
        assert len(self.recipients) >= 1

    def process(self, attachments=None, **kwargs):

        for r in self.recipients:
            context = {
                'from': self.from_tuple.get('name'),
                'from_email': self.from_tuple.get('email'),
                'to': r.get('name'),
                'to_email': r.get('email'),
                'subject': self.subject,
                'message': self.message
            }

            context.update(**kwargs)

            self.send_mail(context=context, attachments=attachments)

    def send_mail(self, context, attachments=None):
            send_templated_mail(
                template_name=self.email_template,
                template_prefix=self.base_email_template_location,
                from_email=context.get('from_email'),
                recipient_list=[context.get('to_email')],
                bcc=['founders@lawpal.com'] if settings.PROJECT_ENVIRONMENT == 'prod' else [],  # only bcc us in on live mails
                context=context,
                attachments=attachments)
