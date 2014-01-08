# -*- coding: utf-8 -*-
from toolkit.mailers import BaseMailerService


class WelcomeEmail(BaseMailerService):
    """
    m = WelcomeEmail(
            recipients=(('Alex', 'alex@lawpal.com')))
    m.process()
    """
    email_template = 'welcome_email'