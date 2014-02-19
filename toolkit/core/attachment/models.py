# -*- coding: utf-8 -*-
from django.db import models
from django.template.defaultfilters import slugify
from storages.backends.s3boto import S3BotoStorage

from jsonfield import JSONField

import os


def _upload_file(instance, filename):
    filename = os.path.split(filename)[-1]
    filename_no_ext, ext = os.path.splitext(filename)
    return 'executed_files/%d-%s-%s%s' % (instance.item.pk, instace.uploaded_by.username, slugify(filename_no_ext), ext)


class Revision(models.Model):
    executed_file = models.FileField(upload_to=_upload_file, storage=S3BotoStorage(), null=True, blank=True)

    item = models.ForeignKey('item.Item')
    uploaded_by = models.ForeignKey('auth.User')

    # self referencing to allow for revisions to be able to see each other in a set (linked list)
    revisions = models.ManyToManyField('attachment.Revision', null=True, blank=True, symmetrical=False, related_name="own_revisions")

    reviewers = models.ManyToManyField('auth.User', related_name='revision_reviewers', blank=True, null=True)
    signatories = models.ManyToManyField('auth.User', related_name='revision_signatories', blank=True, null=True)

    data = JSONField(default={}, blank=True)

    date_created = models.DateTimeField(auto_now=False, auto_now_add=True, db_index=True)
    date_modified = models.DateTimeField(auto_now=True, auto_now_add=True, db_index=True)

    class Meta:
        # @BUSINESS RULE always return the latest revision first!
        ordering = ('-id',)

    def revision_id(self):
        """
        return the relative revision id for this revision
        """
        for i, obj in enumerate(self.revisions.all()):
            if obj.pk == self.pk:
                return i + 1
        return 1

    def next(self):
        return self.revisions.filter(pk__gt=self.pk).first()

    def previous(self):
        return self.revisions.filter(pk__lt=self.pk).first()