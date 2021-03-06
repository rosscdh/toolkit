# -*- coding: utf-8 -*-
from django.db import models
from django.core.urlresolvers import reverse
from django.db.models.signals import pre_save, post_save


from .signals import (on_item_save_category,
                      on_item_save_closing_group,
                      on_item_save_manual_latest_item_delete,
                      on_item_post_save)

from toolkit.core.mixins import IsDeletedMixin, ApiSerializerMixin

from toolkit.utils import get_namedtuple_choices

from .managers import ItemManager
from .mixins import (RequestDocumentUploadMixin,
                     ReviewInProgressMixin,
                     SigningInProgressMixin,
                     RequestedDocumentReminderEmailsMixin,
                     RevisionReviewReminderEmailsMixin,
                     RevisionSignReminderEmailsMixin,
                     ItemLastCommentByMixin)

from jsonfield import JSONField
from uuidfield import UUIDField

import datetime

BASE_ITEM_STATUS = get_namedtuple_choices('ITEM_STATUS', (
                                (0, 'new', 'New'),
                                (1, 'final', 'Final'),
                                (2, 'executed', 'Executed'),
                            ))


class Item(IsDeletedMixin,
           ApiSerializerMixin,
           RequestDocumentUploadMixin,
           ReviewInProgressMixin,
           SigningInProgressMixin,
           RequestedDocumentReminderEmailsMixin,
           RevisionReviewReminderEmailsMixin,
           RevisionSignReminderEmailsMixin,
           ItemLastCommentByMixin,
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

    latest_revision = models.ForeignKey('attachment.Revision', null=True, blank=True,
                                        related_name='item_latest_revision', on_delete=models.SET_NULL)

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

    _serializer = 'toolkit.api.serializers.ItemSerializer'

    class Meta:
        ordering = ('sort_order',)
        # permissions = (("read_item", "Can read items"), )

    @property
    def task_status(self):
        return self.data.get('tasks', {'complete': 0, 'total': 0})

    @property
    def client(self):
        return self.matter.client

    @property
    def display_status(self):
        return self.ITEM_STATUS.get_desc_by_value(self.status)

    @property
    def has_expired(self):
        if self.date_due:
            return True if self.date_due < datetime.datetime.utcnow() else False
        return False

    def __unicode__(self):
        return u'%s' % self.name

    def get_absolute_url(self):
        return '{url}#/checklist/{item_slug}'.format(
            url=reverse('matter:detail', kwargs={'matter_slug': self.matter.slug}),
            item_slug=self.slug
        )

    def get_regular_url(self):
        """
        Used in notficiations & activity
        """
        return self.get_absolute_url()

    def get_user_review_url(self, user, version_slug=None):
        if version_slug is not None:
            revision = self.revision_set.get(slug=version_slug)
        else:
            revision = self.latest_revision
        return revision.get_user_review_url(user=user)

    def get_user_sign_url(self, user, version_slug=None):
        if version_slug is not None:
            revision = self.revision_set.get(slug=version_slug)
        else:
            revision = self.latest_revision
        return revision.get_user_sign_url(user=user)

    def participants(self):
        return self.data.get('participants', [])

    def reviewers(self):
        return self.data.get('reviewers', [])

    def signers(self):
        return self.data.get('signers', [])

    def save(self, *args, **kwargs):
        """
            reset percentage completed of the matter only if item is newly created or
                                                          if item.is_complete changed
                                                          if item.is_deleted

            This is done here and not in a signal because the percentage has to get calculated with the NEW
            is_complete-value which is not yet available present in the matters' .reset_percentage()-function when
            using pre_save.
            It is only available after the saving.
        """
        do_recalculate = True
        try:
            # get the current
            previous_instance = self.__class__.objects.get(pk=self.pk)
            if previous_instance.is_complete == self.is_complete and not self.is_deleted:
                do_recalculate = False

        except Item.DoesNotExist:
            pass

        super(Item, self).save(*args, **kwargs)

        if do_recalculate:
            self.matter.update_percent_complete()

    def needs_review(self, user):
        if self.latest_revision:
            return user in self.latest_revision.reviewers.all()
        return False

    def needs_signature(self, user):
        if self.latest_revision:
            return user in self.latest_revision.signers.all()
        return False

    def needs_upload(self, user):
        return self.is_requested and self.responsible_party == user

    def can_read(self, user):
        return user in self.matter.participants.all()

    def can_edit(self, user):
        return user in self.matter.participants.all()

    def can_delete(self, user):
        return user.profile.is_lawyer and user in self.matter.participants.all()

#
# rulez_registry.register("can_read", Item)
# rulez_registry.register("can_edit", Item)
# rulez_registry.register("can_delete", Item)


"""
Connect signals
"""
pre_save.connect(on_item_save_category, sender=Item, dispatch_uid='item.pre_save.category')
pre_save.connect(on_item_save_closing_group, sender=Item, dispatch_uid='item.pre_save.closing_group')
pre_save.connect(on_item_save_manual_latest_item_delete, sender=Item, dispatch_uid='item.pre_save.on_item_save_manual_latest_item_delete')
post_save.connect(on_item_post_save, sender=Item, dispatch_uid='item.post_save.category')
