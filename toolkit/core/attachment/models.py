# -*- coding: utf-8 -*-
from django.db import models
from django.template.defaultfilters import slugify
from storages.backends.s3boto import S3BotoStorage

from jsonfield import JSONField

import os


def _upload_file(instance, filename):
    filename = os.path.split(filename)[-1]
    filename_no_ext, ext = os.path.splitext(filename)
    return 'attachment/%s-%s%s' % (instance.tool.username, slugify(filename_no_ext), ext)


class Attachment(models.Model):
    attachment = models.FileField(upload_to=_upload_file, storage=S3BotoStorage())

    item = models.ForeignKey('item.Item')
    uploaded_by = models.ForeignKey('auth.User')

    revisions = models.ManyToManyField('attachment.Attachment', null=True, blank=True, symmetrical=False, related_name="own_revisions")

    data = JSONField(default={}, blank=True)

    date_created = models.DateTimeField(auto_now=False, auto_now_add=True, db_index=True)
    date_modified = models.DateTimeField(auto_now=True, auto_now_add=True, db_index=True)

    def next(self):
        return self.revisions.filter(pk__gt=self.pk)

    def previous(self):
        return self.revisions.filter(pk__lt=self.pk)