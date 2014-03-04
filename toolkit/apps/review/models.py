# -*- coding: utf-8 -*-
from django.db import models
from django.core.urlresolvers import reverse

from uuidfield import UUIDField
from jsonfield import JSONField


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