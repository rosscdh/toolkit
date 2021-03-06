# -*- coding: utf-8 -*-
from django.db import models
from django.template.defaultfilters import slugify

from toolkit.core import _managed_S3BotoStorage

from toolkit.core.mixins import (ApiSerializerMixin, IsDeletedMixin, FileExistsLocallyMixin)
from toolkit.utils import get_namedtuple_choices

from uuidfield import UUIDField
from jsonfield import JSONField

from rulez import registry as rulez_registry

from .managers import RevisionManager
from .mixins import StatusLabelsMixin

import re
import os

BASE_REVISION_STATUS = get_namedtuple_choices('REVISION_STATUS', (
                                (0, 'draft', 'Draft'),
                                (1, 'for_discussion', 'For Discussion'),
                                (2, 'final', 'Final'),
                                (3, 'executed', 'Executed'),
                                (4, 'filed', 'Filed'),
                            ))


def _upload_revision(instance, filename):
    split_file_name = os.path.split(filename)[-1]
    filename_no_ext, ext = os.path.splitext(split_file_name)

    identifier = '%s-%d-%s' % (instance.slug, instance.item.pk, instance.uploaded_by.username)
    full_file_name = '%s-%s%s' % (identifier, slugify(filename_no_ext), ext)

    if identifier in slugify(filename):
        #
        # If we already have this filename as part of the recombined filename
        #
        full_file_name = filename

    return 'executed_files/%s' % full_file_name


def _upload_attachment(instance, filename):
    split_file_name = os.path.split(filename)[-1]
    filename_no_ext, ext = os.path.splitext(split_file_name)

    identifier = '%d-%s' % (instance.item.pk, instance.uploaded_by.username)
    full_file_name = '%s-%s%s' % (identifier, slugify(filename_no_ext), ext)

    if identifier in slugify(filename):
        #
        # If we already have this filename as part of the recombined filename
        #
        full_file_name = filename

    return 'attachments/%s' % full_file_name


class Revision(IsDeletedMixin,
               ApiSerializerMixin,
               StatusLabelsMixin,
               FileExistsLocallyMixin,
               models.Model):
    REVISION_STATUS = BASE_REVISION_STATUS

    name = models.CharField(max_length=255, null=True, blank=True)
    description = models.CharField(max_length=255, null=True, blank=True)

    slug = models.SlugField(blank=True, null=True)  # stores the revision number v3..v2..v1

    executed_file = models.FileField(upload_to=_upload_revision, max_length=255, storage=_managed_S3BotoStorage(),
                                     null=True, blank=True)

    item = models.ForeignKey('item.Item')
    uploaded_by = models.ForeignKey('auth.User')

    reviewers = models.ManyToManyField('auth.User', related_name='revision_reviewers', blank=True, null=True)
    signers = models.ManyToManyField('auth.User', related_name='revision_signers', blank=True, null=True)

    # allow reviewers to upload alternatives to the current
    # these alternatives may be set as the "current" if the lawyer approves
    alternatives = models.ManyToManyField('attachment.Revision', null=True, blank=True, symmetrical=False,
                                          related_name="parent")

    # True by default, so that on create of a new one, it's set as the current revision
    is_current = models.BooleanField(default=True)

    # when the hellosign webhook calls back and sets the document to is_executed = True
    is_executed = models.BooleanField(default=False)

    data = JSONField(default={}, blank=True)

    date_created = models.DateTimeField(auto_now=False, auto_now_add=True, db_index=True)
    date_modified = models.DateTimeField(auto_now=True, auto_now_add=True, db_index=True)

    objects = RevisionManager()

    _serializer = 'toolkit.api.serializers.RevisionSerializer'

    class Meta:
        # @BUSINESS RULE always return the oldest to newest
        ordering = ('id',)

    def __unicode__(self):
        return 'Revision %s' % (self.slug)

    @property
    def revisions(self):
        return self.item.revision_set.all()

    @property
    def primary_reviewdocument(self):
        """
        get the last onthe list which is the first one and the original one
        """
        # is this *really* only the case for a NEW reviewdocument/revision?
        #return self.reviewdocument_set.filter(reviewers=None).last() 
        return self.reviewdocument_set.all().last() 

    @property
    def primary_signdocument(self):
        # there is only ever 1 of these, per revision (document)
        sign_document, is_new = self.signdocument_set.model.objects.get_or_create(document=self)
        if is_new is True:
            #
            # set the sign_doc signers to the current object signers
            #
            sign_document.signers = self.signers.all()
        return sign_document

    # override for FileExistsLocallyMixin:
    def get_document(self):
        return self.executed_file

    def get_absolute_url(self):
        """
        @TODO currently there is no GUI route to handle linking directly to a revision
        """
        # return '{url}'.format(url=self.item.get_absolute_url())
        return '{url}/revision/{slug}'.format(url=self.item.get_absolute_url(), slug=self.slug)

    def get_regular_url(self):
        """
        Used in notficiations & activity
        """
        return self.get_absolute_url()

    def get_user_review_url(self, user, review_document=None):
        """
        Try to provide an initial review url from the base review_document obj
        for the currently logged in user
        """
        if review_document is None:
            review_document = self.primary_reviewdocument
        return review_document.get_absolute_url(user=user, use_absolute=False) if review_document is not None else None

    def get_user_sign_url(self, user, sign_document=None):
        """
        Try to provide an initial signing url from the base sign_document obj
        for the currently logged in user
        """
        if sign_document is None:
            sign_document = self.primary_signdocument
        return sign_document.get_absolute_url(user=user, use_absolute=False) if sign_document is not None else None

    def get_revision_label(self):
        """
        potential bug here.. if the uuid starts with a  v.
        """
        if self.pk in [None, ''] or self.slug in [None, ''] or not re.search(r'^v(\d+)$', self.slug):
            #
            # Does not have a version so increment
            #
            label = 'v{version}'  # append the v
            next_version = int(self.get_next_revision_id())
            return label.format(version=next_version)

        if re.search(r'^v(\d+)$', self.slug):
            #
            # already has a Version
            #
            return self.slug
        raise Exception('Unable to get_revision_label for revision: %s %s' % (self.pk, self.slug))

    def get_next_revision_id(self):
        """
        return the relative revision id for this revision
        Used in the signal to generate the attachment slug
        and revision_label
        NB! must exclude the self.pk otherwise the increment will be wrong +1
        """
        return self.revisions.exclude(pk=self.pk).count() + 1 # default is 1

    def next(self):
        return self.revisions.filter(pk__gt=self.pk).first()

    def previous(self):
        return self.revisions.filter(pk__lt=self.pk).first()

    def can_read(self, user):
        return user in self.item.matter.participants.all() or user in self.reviewers.all() or user in self.signers.all()


class Attachment(IsDeletedMixin,
                 ApiSerializerMixin,
                 FileExistsLocallyMixin,
                 models.Model):
    slug = UUIDField(auto=True, db_index=True)
    name = models.CharField(max_length=255, null=True, blank=True)

    attachment = models.FileField(upload_to=_upload_attachment, max_length=255, storage=_managed_S3BotoStorage())

    item = models.ForeignKey('item.Item', related_name='attachments')
    uploaded_by = models.ForeignKey('auth.User')

    data = JSONField(default={}, blank=True)

    date_created = models.DateTimeField(auto_now=False, auto_now_add=True, db_index=True)

    _serializer = 'toolkit.api.serializers.AttachmentSerializer'

    def get_absolute_url(self):
        """
        return url to the primary item
        """
        return self.item.get_absolute_url()

    # override for FileExistsLocallyMixin:
    def get_document(self):
        return self.attachment

    def can_read(self, user):
        return user in self.item.matter.participants.all()

    def can_edit(self, user):
        if self.pk is None: # create
            return user in self.item.matter.participants.all()
        else:
            return user == self.uploaded_by \
                   or user.matter_permissions(self.item.matter).has_permission(manage_attachments=True)

    def can_delete(self, user):
        return user == self.uploaded_by \
               or user.matter_permissions(self.item.matter).has_permission(manage_attachments=True)

rulez_registry.register("can_read", Attachment)
rulez_registry.register("can_edit", Attachment)
rulez_registry.register("can_delete", Attachment)


from .signals import (ensure_revision_slug,
                      ensure_one_current_revision,
                      set_item_is_requested_false,
                      set_previous_revision_is_current_on_delete,
                      ensure_revision_reviewdocument_object,
                      ensure_revision_item_latest_revision_is_current,
                      on_reviewer_add,
                      on_reviewer_remove,
                      on_signatory_add,
                      on_signatory_remove,
                      on_upload_set_item_is_requested_false)
