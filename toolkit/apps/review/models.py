# -*- coding: utf-8 -*-
from django.db import models
from django.core.urlresolvers import reverse

from toolkit.apps.default.templatetags.toolkit_tags import ABSOLUTE_BASE_URL

from .mixins import UserAuthMixin
from .mailers import ReviewerReminderEmail

from uuidfield import UUIDField
from jsonfield import JSONField

import logging
logger = logging.getLogger('django.request')


class ReviewDocument(UserAuthMixin, models.Model):
    """
    An object to represent a url that allows multiple reviewers to view
    a document using a service like crocodoc
    """
    slug = UUIDField(auto=True, db_index=True)
    document = models.ForeignKey('attachment.Revision')
    participants = models.ManyToManyField('auth.User', related_name='review_owners')
    reviewers = models.ManyToManyField('auth.User')
    data = JSONField(default={})

    class Meta:
        # @BUSINESS RULE always return the oldest to newest
        ordering = ('id',)

    def get_absolute_url(self, user):
        return reverse('review:review_document', kwargs={'slug': self.slug, 'auth_slug': self.make_user_auth_key(user=user)})

    def send_invite_email(self, from_user, users=[]):
        """
        @BUSINESSRULE requested users must be in the reviewers object
        """
        if type(users) not in [list]:
            raise Exception('users must be of type list: users=[<User>]')

        for u in self.reviewers.all():
            #
            # @BUSINESSRULE if no users passed in then send to all of the reviewers
            #
            if users == [] or u in users:
                #
                # send email
                #
                logger.info('Sending ReviewDocument invite email to: %s' % u)

                m = ReviewerReminderEmail(recipients=((u.get_full_name(), u.email,),))
                m.process(subject=m.subject,
                          item=self.document.item,
                          document=self.document,
                          from_name=from_user.get_full_name(),
                          action_url=ABSOLUTE_BASE_URL(path=self.get_absolute_url(user=u)))


from .signals import (on_participant_add,
                      on_participant_add,
                      on_reviewer_add,
                      on_reviewer_remove,)