# -*- coding: utf-8 -*-
from .signals import crocodoc_webhook_event_recieved

import os
from storages.backends.s3boto import S3BotoStorage
from django.template.defaultfilters import slugify
from django.db import models
from toolkit.apps.workspace.models import Workspace

from toolkit.core.mixins import IsDeletedMixin


def _upload_file(instance, filename):
    full_file_name = None

    split_file_name = os.path.split(filename)[-1]
    filename_no_ext, ext = os.path.splitext(split_file_name)

    identifier = '%s-%d' % (instance.matter.slug, instance.matter.pk)
    full_file_name = '%s-%s%s' % (identifier, slugify(filename_no_ext), ext)

    if identifier in slugify(filename):
        #
        # If we already have this filename as part of the recombined filename
        #
        full_file_name = filename

    return 'exported_matters/%s' % full_file_name


# TODO: shall this live here or in workspace.models ?
class ExportedMatter(IsDeletedMixin,
                     models.Model):
    matter = models.ForeignKey(Workspace)
    file = models.FileField(upload_to=_upload_file, storage=S3BotoStorage(), null=True, blank=True)
    token = models.SlugField(db_index=True)