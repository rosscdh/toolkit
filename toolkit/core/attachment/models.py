# -*- coding: utf-8 -*-
from django.db import models
from django.db.models.signals import post_save
from django.template.defaultfilters import slugify

from storages.backends.s3boto import S3BotoStorage
from toolkit.core.signals import on_revision_post_save

from toolkit.utils import get_namedtuple_choices

from jsonfield import JSONField

import os

BASE_REVISION_STATUS = get_namedtuple_choices('REVISION_STATUS', (
                                (0, 'draft', 'Draft'),
                                (1, 'requested', 'Requested'),
                                (2, 'for_discussion', 'For Discussion'),
                                (3, 'final', 'Final'),
                                (4, 'executed', 'Executed'),
                                (5, 'filed', 'Filed'),
                            ))


def _upload_file(instance, filename):
    filename = os.path.split(filename)[-1]
    filename_no_ext, ext = os.path.splitext(filename)
    return 'executed_files/%s-%d-%s-%s%s' % (instance.slug, instance.item.pk, instance.uploaded_by.username, slugify(filename_no_ext), ext)


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
    signatories = models.ManyToManyField('auth.User', related_name='revision_signatories', blank=True, null=True)

    # allow reviewers to upload alternatives to the current
    # these alternatives may be set as the "current" if the lawyer approves
    alternatives = models.ManyToManyField('attachment.Revision', null=True, blank=True, symmetrical=False, related_name="parent")

    data = JSONField(default={}, blank=True)

    date_created = models.DateTimeField(auto_now=False, auto_now_add=True, db_index=True)
    date_modified = models.DateTimeField(auto_now=True, auto_now_add=True, db_index=True)

    class Meta:
        # @BUSINESS RULE always return the oldest to newest
        ordering = ('id',)

    def __unicode__(self):
        return '%s %s' % (self.pk, self.slug)

    @property
    def revisions(self):
        return self.item.revision_set.all()

    def get_revision_label(self, version=None):
        label = 'v{version}'

        if version is not None and type(version) is not int:
            raise Exception('version must be an int')

        return label.format(version=self.get_revision_id() if version is None else version)

    def get_revision_id(self):
        """
        return the relative revision id for this revision
        Used in the signal to generate the attachment slug
        and revision_label
        """
        version = 1 # default is 1
        for c, r in enumerate(self.revisions):
            version = c + 1
            if r.pk == self.pk:
                break
        return version

    def next(self):
        return self.revisions.filter(pk__gt=self.pk).first()

    def previous(self):
        return self.revisions.filter(pk__lt=self.pk).first()


post_save.connect(on_revision_post_save, sender=Revision)


from .signals import (ensure_revision_slug,)
