# -*- coding: utf-8 -*-
from django.db import models
from django.core.urlresolvers import reverse

from uuidfield import UUIDField
from jsonfield import JSONField

import logging
logger = logging.getLogger('django.request')


class ReviewDocument(models.Model):
    """
    An object to represent a url that allows multiple reviewers to view
    a document using a service like crocodoc
    """
    slug = UUIDField(auto=True, db_index=True)
    document = models.ForeignKey('attachment.Revision')
    reviewers = models.ManyToManyField('auth.User')
    data = JSONField(default={})

    def get_absolute_url(self):
        return reverse('review:review_document', kwargs={'slug': self.slug})

    def send_invite_emails(self, users=[]):
        """
        @BUSINESSRULE requested users must be in the reviewers object
        """
        for u in self.reviewers.all():
            #
            # @BUSINESSRULE if no users passed in then send to all of the reviewers
            #
            if users is [] or u in users:
                #
                # send email
                #
                logger.info('Sending ReviewDocument invite email to: %s' % u)

from .signals import (on_reviewer_add, on_reviewer_remove,)