# -*- coding: utf-8 -*-

from toolkit.mailers import BaseMailerService


class InviteUserToToolEmail(BaseMailerService):
    """
    m = InviteUserToToolEmail(
            subject='A new 83b has been created for you',
            message='{from_name} has created an 83b form for you, you can find it at {location}',
            recipients=(('Alex', 'alex@lawpal.com')))
    m.process()
    """
    email_template = 'invite_user_to_tool'