# -*- coding: utf-8 -*-
from django.db import models

from toolkit.utils import get_namedtuple_choices

from jsonfield import JSONField


ITEM_STATUS = get_namedtuple_choices('ITEM_STATUS', (
                                (0, 'new', 'New'),
                                (1, 'awaiting_document', 'Awaiting Document'),
                                (2, 'final', 'Final'),
                                (3, 'executed', 'Executed'),
                            ))


class Item(models.Model):
    """
    Matter.item (workspace tool)
    """
    name = models.CharField(max_length=255)
    description = models.TextField()
    matter = models.ForeignKey('workspace.Workspace')
    responsible_party = models.ForeignKey('auth.User', null=True, blank=True)

    status = models.IntegerField(choices=ITEM_STATUS.get_choices(), default=ITEM_STATUS.new)

    # enables Forking and Cloning for document automation
    parent = models.ForeignKey('item.Item', blank=True, null=True)

    # if is final is true, then the latest_revision will be available for sending for signing
    is_final = models.BooleanField(default=False, db_index=True)

    closing_group = models.CharField(max_length=128, null=True)

    is_complete = models.BooleanField(default=False, db_index=True)

    data = JSONField(default={})

    date_due = models.DateTimeField(auto_now=False, auto_now_add=False, null=True, blank=True, db_index=True)
    date_created = models.DateTimeField(auto_now=False, auto_now_add=True, db_index=True)
    date_modified = models.DateTimeField(auto_now=True, auto_now_add=True, db_index=True)

    @property
    def display_status(self):
        return ITEM_STATUS.get_desc_by_value(self.status)

    @property
    def latest_revision(self):
        """
        @BUSINESSRULE always return the latest revision
        revisions are ordered by -id
        """
        return self.revision_set.all().first()

    def participants(self):
        return self.data.get('participants', [])

    def reviewers(self):
        return self.data.get('reviewers', [])

    def signatories(self):
        return self.data.get('signatories', [])