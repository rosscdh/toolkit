# -*- coding: utf-8 -*-
from toolkit.mailers import BaseMailerService


class AddedUserEmail(BaseMailerService):
    """
    m = AddedUserEmail(recipients=(('Alex', 'alex@lawpal.com')))
    m.process()
    """
    email_template = 'added_user'


class CommentedEmail(BaseMailerService):
    """
    m = CommentedEmail(recipients=(('Alex', 'alex@lawpal.com')))
    m.process()
    """
    email_template = 'commented'
