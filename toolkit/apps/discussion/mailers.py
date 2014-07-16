# -*- coding: utf-8 -*-
from toolkit.mailers import BaseMailerService


class DiscussionAddedUserEmail(BaseMailerService):
    """
    m = DiscussionAddedUserEmail(recipients=(('Alex', 'alex@lawpal.com')))
    m.process()
    """
    email_template = 'added_user'


class DiscussionCommentedEmail(BaseMailerService):
    """
    m = DiscussionCommentedEmail(recipients=(('Alex', 'alex@lawpal.com')))
    m.process()
    """
    email_template = 'commented'
