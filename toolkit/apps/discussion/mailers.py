# -*- coding: utf-8 -*-
from toolkit.mailers import BaseMailerService


class AddedToThreadEmail(BaseMailerService):
    """
    m = AddedToThreadEmail(recipients=(('Alex', 'alex@lawpal.com')))
    m.process()
    """
    email_template = 'user_added'


class NewCommentEmail(BaseMailerService):
    """
    m = NewCommentEmail(recipients=(('Alex', 'alex@lawpal.com')))
    m.process()
    """
    email_template = 'new_comment'
