# -*- coding: utf-8 -*-
from django.db import models
from django.db.models.signals import pre_save, post_save

from toolkit.core.signals.activity import (on_item_post_save,)
from .signals import (on_item_save_category,
                      on_item_save_closing_group)

from toolkit.core.mixins import IsDeletedMixin

from toolkit.utils import get_namedtuple_choices

from .managers import ItemManager
from .mixins import (RequestDocumentUploadMixin,
                     RequestedDocumentReminderEmailsMixin,
                     LatestRevisionReminderEmailsMixin,)

from jsonfield import JSONField
from uuidfield import UUIDField
from rulez import registry as rulez_registry

BASE_ITEM_STATUS = get_namedtuple_choices('ITEM_STATUS', (
                                (0, 'new', 'New'),
                                (1, 'final', 'Final'),
                                (2, 'executed', 'Executed'),
                            ))


class Item(IsDeletedMixin, RequestDocumentUploadMixin,
           RequestedDocumentReminderEmailsMixin,
           LatestRevisionReminderEmailsMixin,
           models.Model):
    """
    Matter.item
    """
    ITEM_STATUS = BASE_ITEM_STATUS

    slug = UUIDField(auto=True, db_index=True)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)

    matter = models.ForeignKey('workspace.Workspace')
    responsible_party = models.ForeignKey('auth.User', null=True, blank=True)

    status = models.IntegerField(choices=ITEM_STATUS.get_choices(), default=ITEM_STATUS.new)

    sort_order = models.IntegerField(blank=True, null=True)  # global sort_order for the item within the checklist

    # enables Forking and Cloning for document automation
    parent = models.ForeignKey('item.Item', blank=True, null=True)

    closing_group = models.CharField(max_length=128, null=True, blank=True, db_index=True)
    category = models.CharField(max_length=128, null=True, blank=True, db_index=True)

    # if is final is true, then the latest_revision will be available for sending for signing
    is_final = models.BooleanField(default=False, db_index=True)
    # this item is complete and signed off on
    is_complete = models.BooleanField(default=False, db_index=True)
    # when requesting a revision from someone
    is_requested = models.BooleanField(default=False, db_index=True)

    data = JSONField(default={})

    date_due = models.DateTimeField(auto_now=False, auto_now_add=False, null=True, blank=True, db_index=True)

    date_created = models.DateTimeField(auto_now=False, auto_now_add=True, db_index=True)
    date_modified = models.DateTimeField(auto_now=True, auto_now_add=True, db_index=True)

    objects = ItemManager()

    class Meta:
        ordering = ('sort_order',)

    def __unicode__(self):
        return u'%s' % self.name

    @property
    def display_status(self):
        return self.ITEM_STATUS.get_desc_by_value(self.status)

    @property
    def latest_revision(self):
        """
        @BUSINESSRULE always return the latest revision
        """
        return self.revision_set.all().last()

    def participants(self):
        return self.data.get('participants', [])

    def reviewers(self):
        return self.data.get('reviewers', [])

    def signatories(self):
        return self.data.get('signatories', [])

    def can_read(self, user):
        return user in self.matter.participants.all()

    def can_edit(self, user):
        return user in self.matter.participants.all()

    def can_delete(self, user):
        # for testing only!
        # to delete a comment via ItemCommentEndpoint this seems to be required.
        return True
        return user.profile.is_lawyer and user in self.matter.participants.all()

"""
Connect signals
"""
pre_save.connect(on_item_save_category, sender=Item, dispatch_uid='item.post_save.category')
pre_save.connect(on_item_save_closing_group, sender=Item, dispatch_uid='item.post_save.closing_group')
post_save.connect(on_item_post_save, sender=Item, dispatch_uid='item.post_save.category')


rulez_registry.register("can_read", Item)
rulez_registry.register("can_edit", Item)
rulez_registry.register("can_delete", Item)
