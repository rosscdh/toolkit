# -*- coding: utf-8 -*-
from django.contrib.auth.models import User

from toolkit.mailers import BaseMailerService

import re
import logging
logger = logging.getLogger('django.request')


class YouWereMentionedEmail(BaseMailerService):
    """
    m = YouWereMentionedEmail(recipients=(('Alex', 'alex@lawpal.com'),),)
    m.process()
    """
    email_template = 'you_were_mentioned'
    subject = u'{mentioned_by} mentioned you in a comment'


class MentionsService(object):
    """
    service to parse comment text for @username mentions
    al la trello
    regexes used from http://blogs.openshine.com/pvieytes/2011/05/18/parsing-twitter-user-timeline-with-python/
    """
    RE_USER = re.compile(r'@[0-9a-zA-Z+_-]*',re.IGNORECASE)  # my-username-is
    #RE_HASH = re.compile(r'#[0-9a-zA-Z+_]*',re.IGNORECASE)

    users = None
    mentioned_usernames = None
    mentioned_by = None

    def __init__(self, mentioned_by, *args, **kwargs):
        self.users = None
        mentioned_usernames = None
        self.mentioned_by = mentioned_by

    def get_users(self, mentioned_usernames):
        """
        get queryset of users
        mentioned_usernames - List of usernames
        """
        if type(mentioned_usernames) not in [list]:
            raise Exception('mentioned_usernames should be a list ["username_a"]')

        return User.objects.filter(username__in=mentioned_usernames)

    def notify_users(self, mention, **kwargs):
        """
        Send the notifications after you have called parse
        """
        users =  kwargs.get('users', self.users)
        access_url = kwargs.get('access_url', None)
        mentioned_by = kwargs.get('mentioned_by', self.mentioned_by)

        subject = kwargs.get('subject', YouWereMentionedEmail.subject)

        kwargs.update({
            'users': users,
            'access_url': access_url,
            'mentioned_by': mentioned_by,
            'mention': mention
        })

        subject = subject.format(**kwargs)  # update the subject with the passed in info

        kwargs.update({
            'subject': subject
        });

        for user in self.users:
            m = YouWereMentionedEmail(recipients=((user.get_full_name(), user.email),),)
            m.process(**kwargs)

    def extract_mentions(self, text):
        usernames = []
        for iterator in self.RE_USER.finditer(text):
            a_username = iterator.group(0)
            username = a_username.replace('@', '')
            usernames.append(username)

        return usernames

    def process(self, text, notify=False, **kwargs):
        """
        Parse the comment for usernames and send the mention emails
        text - The comment the user was mentioned in
        notify - (bool) Send the notifications immediately or not
        """
        self.mentioned_usernames = self.extract_mentions(text=text)

        if self.mentioned_usernames:
            # we have some users so set them up
            self.users = self.get_users(mentioned_usernames=self.mentioned_usernames)

            if self.users and notify is True:
                self.notify_users(mention=text, **kwargs)

        return self.users