# -*- coding: utf-8 -*-
from django.db import models
from django.template.defaultfilters import slugify

from storages.backends.s3boto import S3BotoStorage

from toolkit.utils import get_namedtuple_choices

from jsonfield import JSONField

from .managers import RevisionManager

import re
import os

BASE_REVISION_STATUS = get_namedtuple_choices('REVISION_STATUS', (
                                (0, 'draft', 'Draft'),
                                (1, 'for_discussion', 'For Discussion'),
                                (2, 'final', 'Final'),
                                (3, 'executed', 'Executed'),
                                (4, 'filed', 'Filed'),
                            ))


def _upload_file(instance, filename):
    full_file_name = None

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


class Revision(models.Model):
    REVISION_STATUS = BASE_REVISION_STATUS

    name = models.CharField(max_length=255, null=True, blank=True)
    description = models.CharField(max_length=255, null=True, blank=True)

    slug = models.SlugField(blank=True, null=True)  # stores the revision number v3..v2..v1

    executed_file = models.FileField(upload_to=_upload_file, storage=S3BotoStorage(), null=True, blank=True)

    status = models.IntegerField(choices=REVISION_STATUS.get_choices(), default=REVISION_STATUS.draft)

    item = models.ForeignKey('item.Item')
    uploaded_by = models.ForeignKey('auth.User')

    reviewers = models.ManyToManyField('auth.User', related_name='revision_reviewers', blank=True, null=True)
    signers = models.ManyToManyField('auth.User', related_name='revision_signers', blank=True, null=True)

    # allow reviewers to upload alternatives to the current
    # these alternatives may be set as the "current" if the lawyer approves
    alternatives = models.ManyToManyField('attachment.Revision', null=True, blank=True, symmetrical=False, related_name="parent")

    # True by default, so that on create of a new one, it's set as the current revision
    is_current = models.BooleanField(default=True)

    data = JSONField(default={}, blank=True)

    date_created = models.DateTimeField(auto_now=False, auto_now_add=True, db_index=True)
    date_modified = models.DateTimeField(auto_now=True, auto_now_add=True, db_index=True)

    objects = RevisionManager()

    class Meta:
        # @BUSINESS RULE always return the oldest to newest
        ordering = ('id',)

    def __unicode__(self):
        return 'Revision %s' % (self.slug)

    @property
    def revisions(self):
        return self.item.revision_set.all()

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
        """
        return self.revisions.count() + 1 # default is 1

    def next(self):
        return self.revisions.filter(pk__gt=self.pk).first()

    def previous(self):
        return self.revisions.filter(pk__lt=self.pk).first()

from .signals import (ensure_revision_slug,
                      ensure_one_current_revision,
                      set_item_is_requested_false,
                      set_previous_revision_is_current_on_delete,
                      ensure_revision_reviewdocument_object,
                      ensure_revision_item_latest_revision_is_current,
                      on_reviewer_add,
                      on_reviewer_remove,
                      on_upload_set_item_is_requested_false)
