# -*- coding: utf-8 -*-
from django.db import models
from django.template.defaultfilters import slugify
from storages.backends.s3boto import S3BotoStorage

from jsonfield import JSONField

import os


def _upload_file(instance, filename):
    filename = os.path.split(filename)[-1]
    filename_no_ext, ext = os.path.splitext(filename)
    return 'executed_files/%s-%d-%s-%s%s' % (instance.slug, instance.item.pk, instance.uploaded_by.username, slugify(filename_no_ext), ext)


class Revision(models.Model):
    executed_file = models.FileField(upload_to=_upload_file, storage=S3BotoStorage(), null=True, blank=True)
    slug = models.SlugField(null=True)  # stores the revision number v3..v2..v1

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
        for c, r in enumerate(self.revisions):
            version = c + 1
            if r.pk == self.pk:
                break
        return version

    def next(self):
        return self.revisions.filter(pk__gt=self.pk).first()

    def previous(self):
        return self.revisions.filter(pk__lt=self.pk).first()


from .signals import (ensure_revision_slug,)
