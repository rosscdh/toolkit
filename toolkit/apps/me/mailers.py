# -*- coding: utf-8 -*-
from django.core import signing
from django.conf import settings
from django.core.urlresolvers import reverse

from toolkit.mailers import BaseMailerService
from toolkit.apps.default.templatetags.toolkit_tags import ABSOLUTE_BASE_URL


class WelcomeEmail(BaseMailerService):
    """
    m = WelcomeEmail(
            recipients=(('Alex', 'alex@lawpal.com')))
    m.process()
    """
    email_template = 'welcome_email'


class ValidateEmailMailer(BaseMailerService):
    """
    m = ValidateEmailMailer(
            recipients=(('Alex', 'alex@lawpal.com')))
    m.process(user=user_send_validation_email_to)
    """
    email_template = 'validate_email'

    def process(self, user, **kwargs):
        token = signing.dumps(user.pk, salt=settings.SECRET_KEY)

        action_url = ABSOLUTE_BASE_URL(reverse('me:confirm-email-address', kwargs={'token': token}))

        kwargs.update({
            'action_url': action_url
        })

        super(ValidateEmailMailer, self).process(**kwargs)