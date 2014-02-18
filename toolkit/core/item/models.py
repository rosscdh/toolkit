# -*- coding: utf-8 -*-
from django.db import models
from toolkit.utils import get_namedtuple_choices

from jsonfield import JSONField

ITEM_TYPES = get_namedtuple_choices('ITEM_TYPES', (
                (0, 'negotiated', 'Negotiated Document'),
                (1, 'upload_only', 'Upload Document'),
             ))


class Item(models.Model):
    """
    Matter.item (workspace tool)
    """
    name = models.CharField(max_length=255)

    item_type = models.IntegerField(choices=ITEM_TYPES.get_choices(), default=ITEM_TYPES.negotiated, db_index=True)
    
    revisions = models.ManyToManyField('attachment.Attachment', related_name='item_revisions', blank=True, null=True)
    participants = models.ManyToManyField('auth.User', related_name='item_participants', blank=True, null=True)
    reviewers = models.ManyToManyField('auth.User', related_name='item_reviewers', blank=True, null=True)
    signatories = models.ManyToManyField('auth.User', related_name='item_signatories', blank=True, null=True)

    is_complete = models.BooleanField(default=False, db_index=True)

    data = JSONField(default={})

    date_due = models.DateTimeField(auto_now=False, auto_now_add=False, blank=True, db_index=True)
    date_created = models.DateTimeField(auto_now=False, auto_now_add=True, db_index=True)
    date_modified = models.DateTimeField(auto_now=True, auto_now_add=True, db_index=True)